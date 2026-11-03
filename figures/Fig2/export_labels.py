"""Export one real Dynamic-14 query, without a policy or generated imagery.

Runs on CPU on Windows or Linux. The source episode and its Fig.4 clean Blender
render must refer to the same camera and tick. Units: metres, seconds, xyzw.
"""
from pathlib import Path
import argparse
import json
import platform
import shutil

import h5py
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation


def project(points, camera, intrinsic):
    camera_points = (np.asarray(points) - camera[:3, 3]) @ camera[:3, :3]
    homogeneous = camera_points @ intrinsic.T
    assert np.all(camera_points[..., 2] > 0)
    return homogeneous[..., :2] / homogeneous[..., 2, None]


def export(episode, beauty, output, tick):
    output.mkdir(parents=True, exist_ok=True)
    with h5py.File(episode, 'r') as f:
        meta = json.loads(f['metadata/episode_json'][()].decode())
        t = f['policy/timestamp_s'][:]
        assert 7 <= tick and tick + 8 < len(t)
        assert np.allclose(np.diff(t[tick-7:tick+9]), .05, atol=1e-8)
        depth = f['policy/depth_m'][tick:tick+9, 0].astype(float)
        geom = f['supervision/geom_id'][tick:tick+9, 0]
        transforms = f['supervision/world_from_geom'][tick:tick+9]
        cameras = f['policy/world_from_camera_cv'][tick:tick+9, 0]
        intrinsics = f['policy/camera_intrinsics'][tick:tick+9, 0]
        base = f['policy/T_robot_base_from_world'][:]
        poses = f['supervision/target_object_pose_world'][tick-7:tick+9]
        eef = f['policy/eef_position'][tick:tick+9]
        action = f['action/value'][tick:tick+8]
        rgb = f['policy/rgb'][tick, 0]
        height, width = depth.shape[1:]
        # Identical row-major sampling and tie rule to the native model adapter.
        xy = np.asarray([(((2*c+1)*width-1)//28, ((2*r+1)*height-1)//28)
                         for r in range(14) for c in range(14)])
        x, y = xy.T
        ids = geom[0, y, x]
        good = np.isfinite(depth[0, y, x]) & (depth[0, y, x] > 0) & (ids >= 0)
        assert good.all(), 'This figure query requires all 196 real source points.'
        rays = np.column_stack((xy, np.ones(196))) @ np.linalg.inv(intrinsics[0]).T
        source_camera = rays * depth[0, y, x, None]
        source_world = source_camera @ cameras[0, :3, :3].T + cameras[0, :3, 3]
        local = np.einsum('pji,pj->pi', transforms[0, ids, :3, :3],
                          source_world - transforms[0, ids, :3, 3])
        future = np.stack([np.einsum('pij,pj->pi', transforms[h, ids, :3, :3], local)
                           + transforms[h, ids, :3, 3] for h in range(1, 9)], 1)
        flow = (future - source_world[:, None]) @ base[:3, :3].T
        visible = np.zeros((196, 8), bool)
        for h in range(8):
            cp = (future[:, h] - cameras[h+1, :3, 3]) @ cameras[h+1, :3, :3]
            uvh = cp @ intrinsics[h+1].T
            uv = uvh[:, :2] / uvh[:, 2, None]
            inside = (cp[:, 2] > 0) & (uv[:, 0] >= 0) & (uv[:, 0] <= width-1) & (uv[:, 1] >= 0) & (uv[:, 1] <= height-1)
            selected = np.flatnonzero(inside)
            u, v = np.floor(uv[inside]+.5).astype(int).T
            visible[selected, h] = (geom[h+1, v, u] == ids[selected]) & (np.abs(depth[h+1, v, u] - cp[selected, 2]) <= np.maximum(.001, .001*cp[selected, 2]))
        # Dense cloud is only a visual substrate; the supervised flow stays 14x14.
        yy, xx = np.mgrid[:height, :width]
        pixels = np.stack((xx, yy, np.ones_like(xx)), -1)
        cloud_camera = (pixels @ np.linalg.inv(intrinsics[0]).T) * depth[0, ..., None]
        cloud_world = cloud_camera @ cameras[0, :3, :3].T + cameras[0, :3, 3]
        source_base = source_world @ base[:3, :3].T + base[:3, 3]
        target_base = poses[:, :3] @ base[:3, :3].T + base[:3, 3]
        rotations = base[:3, :3] @ Rotation.from_quat(poses[:, 3:]).as_matrix()
        target_delta = target_base[8:] - target_base[7]
        rot_delta = Rotation.from_matrix(rotations[8:] @ rotations[7].T).as_rotvec()
        # Recorded EEF states are already in the robot base frame.
        eef_world = (eef - base[:3, 3]) @ base[:3, :3]
        payload = dict(depth_m=depth[0].astype(np.float32), rgb_native=rgb,
                       source_pixel_xy=xy, source_geom_id=ids,
                       source_world_m=source_world, source_robot_base_m=source_base,
                       future_world_m=future, flow_robot_base_m=flow.astype(np.float32),
                       flow_valid=np.ones((196, 8), bool), future_visible=visible,
                       cloud_world_m=cloud_world, world_from_camera_cv=cameras[0],
                       camera_intrinsics=intrinsics[0], T_robot_base_from_world=base,
                       history_pose_world_xyzw=poses[:8], future_pose_world_xyzw=poses[8:],
                       target_displacement_robot_base_m=target_delta,
                       target_left_rotvec_robot_base_rad=rot_delta,
                       eef_world_m=eef_world, action_value=action,
                       history_time_s=t[tick-7:tick+1], future_time_s=t[tick+1:tick+9])
        np.savez_compressed(output/'labels.npz', **payload)
        Image.fromarray(rgb).save(output/'rgb_native.png')
        # Monotone metric depth display; bounds retained for unambiguous reuse.
        lo, hi = .65, 1.45
        z = np.clip((depth[0]-lo)/(hi-lo), 0, 1)
        near, far = np.array([39, 83, 120]), np.array([234, 242, 247])
        Image.fromarray((near[None, None]*(1-z[..., None])+far[None, None]*z[..., None]).astype(np.uint8)).save(output/'depth.png')
        shutil.copyfile(beauty, output/'rgb_blender.png')
        reproj = project(source_world, cameras[0], intrinsics[0])
        error = float(np.max(np.abs(reproj-xy)))
        assert error < 1e-8
        motion = np.linalg.norm(flow[:, -1], axis=1)
        target_ids = [r['geom_id'] for r in meta['geom_table'] if r['instance_identity'] == 'target']
        target_sample = np.isin(ids, target_ids)
        assert target_sample.any()
        table = dict(task_id=meta['task_id'], scenario_id=meta['scenario_id'],
                     episode_id=meta['episode_id'], policy='native-oracle', seed=2,
                     camera='agentview', capture_tick=tick, capture_time_s=float(t[tick]),
                     history_offsets_ms=list(range(-350, 1, 50)), future_offsets_ms=list(range(50, 401, 50)),
                     action_offsets_ms=list(range(0, 400, 50)),
                     source_episode=str(episode.resolve()), source_blender_render=str(beauty.resolve()),
                     execution_host=platform.node(), execution_platform=platform.platform(),
                     depth_display_range_m=[lo, hi],
                     flow_shape=list(flow.shape), flow_frame='robot base', flow_units='m',
                     grid_sample_rule='((2*k+1)*224-1)//28; row-major',
                     geometry_source='native HDF5 rigid geom correspondences, no policy inference',
                     eef_source='recorded expert EEF states at capture + 0..350 ms; illustration of command space, not decoded model actions',
                     visual_scope='GT labels and recorded expert EEF states, no model predictions',
                     events=meta['event_times_s'],
                     validation=dict(reprojection_max_px=error, valid_sources=int(good.sum()),
                                     moving_sources_400ms=int((motion > .001).sum()),
                                     near_zero_sources_400ms=int((motion <= .001).sum()),
                                     target_grid_sources=int(target_sample.sum()),
                                     max_flow_m=float(motion.max()),
                                     target_displacement_400ms_m=float(np.linalg.norm(target_delta[-1]))))
        (output/'sources.json').write_text(json.dumps(table, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        print(json.dumps(table['validation'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode', type=Path, required=True)
    parser.add_argument('--beauty', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'assets')
    parser.add_argument('--tick', type=int, default=38)
    args = parser.parse_args()
    export(args.episode, args.beauty, args.output, args.tick)
