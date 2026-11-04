"""Snapshot the Fig. 1(a) frame and its training labels from one native OnTimeBench episode.

Labels come from the training adapter itself (se3_wam.data.dynamic_benchmark.read_targets,
H=8, anchor=True); this script only projects them into the agentview image. Run with the
SE3-WAM-canonical environment (h5py, scipy, torch):

    C:/workspace/SE3-WAM-canonical/.venv/Scripts/python.exe extract_labels.py --episode <hdf5>
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import sys

import h5py
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
CONTROL_PERIOD_MS = 50
HORIZON = 8


def project(points_world, world_from_camera, intrinsic):
    camera = (points_world - world_from_camera[:3, 3]) @ world_from_camera[:3, :3]
    uv = camera @ intrinsic.T
    return uv[..., :2] / uv[..., 2:3]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--episode', type=Path, required=True)
    p.add_argument('--canonical', type=Path, default=Path('C:/workspace/SE3-WAM-canonical'))
    p.add_argument('--latency-ms', type=float, default=50.0,
                   help='p95 time-to-action of the method; rounded up to the 50 ms control period')
    p.add_argument('--frame-rule', choices=['after-onset', 'after-end'], default='after-onset',
                   help='tau = first frame after the striker contact starts (default) or ends')
    p.add_argument('--output', type=Path, default=ROOT / 'data')
    a = p.parse_args()
    sys.path.insert(0, str(a.canonical / 'src'))
    from se3_wam.data import dynamic_benchmark as db

    latency_steps = max(1, math.ceil(a.latency_ms / CONTROL_PERIOD_MS - 1e-9))
    with h5py.File(a.episode, 'r') as h:
        metadata, frames, spec, views, _ = db._inspect(h)
        events = metadata['event_times_s']
        stamps = h['policy/timestamp_s'][:]
        event = events['striker_impact_onset' if a.frame_rule == 'after-onset' else 'striker_impact_end']
        tau = int(np.flatnonzero(stamps > event + 1e-9)[0])
        if tau + HORIZON >= frames:
            raise ValueError('frame lacks complete H=8 futures')
        labels = db.read_targets(a.episode, np.array([tau]), partition=metadata['partition'],
                                 sample_rate_hz=20.0, views=views, action_spec=spec,
                                 horizon=HORIZON, anchor=True, object_reference=True)
        labels = {k: v[0].numpy() for k, v in labels.items() if v is not None}
        rgb = h['policy/rgb'][tau, 0]
        depth = h['policy/depth_m'][tau, 0]
        geom = h['supervision/geom_id'][:, 0]
        cameras = h['policy/world_from_camera_cv'][:, 0]
        intrinsics = h['policy/camera_intrinsics'][:, 0]
        base_from_world = h['policy/T_robot_base_from_world'][:]
        window = slice(tau, tau + HORIZON + 1)
        if not (np.allclose(cameras[window], cameras[tau]) and np.allclose(intrinsics[window], intrinsics[tau])):
            raise ValueError('agentview camera moves inside the label window')
    camera, intrinsic = cameras[tau], intrinsics[tau]
    world_from_base = np.linalg.inv(base_from_world)
    table = metadata['geom_table']
    target_ids = [row['geom_id'] for row in table if row['instance_identity'] == 'target']

    # Flow: same fixed 14x14 source pixels and back-projection as the label adapter.
    source = np.asarray(db._patch_source_pixels(224, 224), dtype=np.int64)  # (row, col)
    ys, xs = source.T
    pixels = np.column_stack((xs, ys, np.ones(len(xs))))
    point_world = (depth[ys, xs, None] * np.linalg.solve(intrinsic, pixels.T).T) @ camera[:3, :3].T + camera[:3, 3]
    flow_world = labels['future_flow_robot_base_m'] @ world_from_base[:3, :3].T  # (196, 8, 3)
    flow_end_px = project(point_world[:, None] + flow_world, camera, intrinsic)
    patch_instance = np.array([table[g]['instance_identity'] if g >= 0 else 'none' for g in geom[tau][ys, xs]])
    magnitude = np.linalg.norm(labels['future_flow_robot_base_m'][:, -1], axis=-1)

    # Target SE(3) labels, robot-base frame -> world; index 0 is the current pose at tau.
    position = np.concatenate([labels['current_object_position_robot_base_m'][None],
                               labels['future_anchor_position_robot_base_m']])
    quaternion = np.concatenate([labels['current_object_quaternion_robot_base_xyzw'][None],
                                 labels['future_anchor_quaternion_robot_base_xyzw']])
    from scipy.spatial.transform import Rotation
    rotation_world = world_from_base[:3, :3] @ Rotation.from_quat(quaternion).as_matrix()
    position_world = position @ world_from_base[:3, :3].T + world_from_base[:3, 3]
    yaw_deg = Rotation.from_quat(quaternion).as_euler('xyz', degrees=True)[:, 2]

    a.output.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(a.output / 'frame_tau_rgb.png')  # raw policy/rgb, lossless
    np.savez_compressed(
        a.output / 'labels.npz',
        source_px_xy=np.column_stack((xs, ys)).astype(np.float64),
        flow_robot_base_m=labels['future_flow_robot_base_m'],
        flow_valid=labels['correspondence_valid'], flow_visible=labels['future_visible'],
        flow_end_px=flow_end_px, patch_instance=patch_instance,
        target_position_world_m=position_world, target_rotation_world=rotation_world,
        target_mask_tau=np.isin(geom[tau], target_ids),
        target_mask_tau_plus_L=np.isin(geom[tau + latency_steps], target_ids),
        world_from_camera_cv=camera, camera_intrinsics=intrinsic)
    commit = subprocess.run(['git', '--no-optional-locks', '-C', str(a.canonical), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    record = dict(
        episode_hdf5=str(a.episode.resolve()).replace('\\', '/'),
        episode_sha256=hashlib.sha256(a.episode.read_bytes()).hexdigest(),
        episode_id=metadata['episode_id'], task_id=metadata['task_id'], partition=metadata['partition'],
        camera='agentview', image_px=[224, 224], frames=frames,
        frame_rule=a.frame_rule, tau_frame_index=tau, tau_time_s=round(float(stamps[tau]), 6),
        striker_impact_s=[events['striker_impact_onset'], events['striker_impact_end']],
        latency_ms_input=a.latency_ms, latency_steps=latency_steps, latency_ms_rounded=latency_steps * CONTROL_PERIOD_MS,
        tau_plus_L_frame_index=tau + latency_steps,
        horizons_ms=[CONTROL_PERIOD_MS * (h + 1) for h in range(HORIZON)],
        target_yaw_robot_base_deg=dict(zip(['tau'] + [f'h{h + 1}' for h in range(HORIZON)],
                                           np.round(yaw_deg, 2).tolist())),
        target_geom_ids=target_ids,
        label_code=dict(repo=str(a.canonical).replace('\\', '/'), commit=commit,
                        function='se3_wam.data.dynamic_benchmark.read_targets(horizon=8, anchor=True, object_reference=True)'),
        flow_at_400ms_mm={name: np.round(np.sort(magnitude[patch_instance == name])[::-1] * 1000, 1).tolist()
                          for name in sorted(set(patch_instance[magnitude > .002]))},
    )
    (a.output / 'source.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
