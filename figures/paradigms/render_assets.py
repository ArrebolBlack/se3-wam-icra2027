#!/usr/bin/env python3
"""Render Fig. 2's four recorded frames with the shared studio defaults.

Run with the research repository's Blender Python environment. The accepted
native scene supplies the camera, meshes, textures and lights; only specular
changes. No simulation, interpolation, camera adjustment or color override.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Quaternion

HERE = Path(__file__).resolve().parent
FRAMES = ((29, "frame_now.png"), (30, "frame_p050.png"),
          (33, "frame_p200.png"), (37, "frame_p400.png"))


def camera_state(scene):
    cam = scene.camera
    return {"name": cam.name, "matrix_world": [list(row) for row in cam.matrix_world],
            **{key: getattr(cam.data, key) for key in
               ("type", "lens", "sensor_fit", "sensor_width", "sensor_height",
                "shift_x", "shift_y", "clip_start", "clip_end")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--research-root", type=Path,
                        default=Path(os.environ.get("SE3WAM_RESEARCH", "C:/workspace/se3-wam-research")))
    parser.add_argument("--output", type=Path, default=HERE / "assets")
    parser.add_argument("--report", type=Path,
                        default=HERE.parents[1] / "build/fig2-20261116/render_validation.json")
    args = parser.parse_args()
    sys.path.insert(0, str(args.research_root / "scripts/benchmark_infra/mujoco_blender"))
    from render_blender import geom_scale
    from studio_controls import DEFAULTS

    provenance = json.loads((HERE / "archive/three_column_pipeline/source.json").read_text(
        encoding="utf-8"))["rgb_illustrations"]
    native_scene = Path(provenance["native_scene"])
    replay = native_scene.parents[3] / "recordings/t5_replan/recording/replay"
    recorded = np.load(replay / "trajectory.npz")
    geometry = np.load(replay / "geometry.npz")
    expected = {r["frame"]: r["max_pose_error"] for r in provenance["frames"]}
    bpy.ops.wm.open_mainfile(filepath=str(native_scene))
    scene = bpy.context.scene
    camera = camera_state(scene)
    assert camera["name"] == "agentview", camera
    for group in bpy.data.collections:
        if group.name.startswith(("History", "Annotations")):
            group.hide_render = group.hide_viewport = True
    current = next(c for c in bpy.data.collections if c.name.startswith("Current"))
    objects = [o for o in current.objects if "mujoco_geom_id" in o]

    # Verify the accepted appearance before applying the one changed parameter.
    assert scene.view_settings.view_transform == "AgX"
    assert scene.view_settings.look == DEFAULTS["look"]
    assert scene.view_settings.exposure == DEFAULTS["exposure"]
    assert scene.view_settings.gamma == DEFAULTS["gamma"]
    assert DEFAULTS["saturation"] == 1 and DEFAULTS["hue"] == 0
    assert not any(DEFAULTS[k] for k in ("belt_color_enabled", "floor_color_enabled", "table_color_enabled"))
    assert abs(scene.world.node_tree.nodes["Background"].inputs[1].default_value - DEFAULTS["world_strength"]) < 1e-7
    for key, name in (("key", "Key softbox"), ("fill", "Fill softbox"), ("rim", "Rim softbox")):
        light = bpy.data.lights[name]
        assert light.energy == DEFAULTS[f"{key}_energy"]
        assert light.size == DEFAULTS[f"{key}_size"]
    materials = {}
    for material in bpy.data.materials:
        bsdf = material.node_tree.nodes.get("Principled BSDF") if material.use_nodes else None
        if bsdf is None:
            continue
        color = tuple(bsdf.inputs["Base Color"].default_value)
        roughness = float(bsdf.inputs["Roughness"].default_value)
        bsdf.inputs["Specular IOR Level"].default_value = DEFAULTS["specular"]
        assert tuple(bsdf.inputs["Base Color"].default_value) == color
        materials[material.name] = {"base_color_linear": color, "roughness": roughness,
                                    "specular": float(bsdf.inputs["Specular IOR Level"].default_value)}
    for obj in objects:
        for material in obj.data.materials:
            assert abs(materials[material.name]["roughness"] - DEFAULTS["roughness"]) < 1e-7

    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    devices = []
    for device in prefs.devices:
        device.use = device.type == "OPTIX"
        if device.use:
            devices.append(device.name)
    assert devices, "No OPTIX device"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPTIX"
    scene.cycles.denoising_use_gpu = True
    scene.render.resolution_x = scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.use_persistent_data = True
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for frame, filename in FRAMES:
        for obj in objects:
            i = int(obj["mujoco_geom_id"])
            obj.location = recorded["geom_pos"][frame, i]
            obj.rotation_quaternion = recorded["geom_quat"][frame, i]
            obj.scale = geom_scale(int(geometry["geom_type"][i]), recorded["geom_size"][frame, i])
            obj["sample_index"] = frame
        bpy.context.view_layer.update()
        max_error = 0.0
        for obj in objects:
            i = int(obj["mujoco_geom_id"])
            pos, rot, _ = obj.matrix_world.decompose()
            max_error = max(max_error,
                float(np.max(abs(np.asarray(pos) - recorded["geom_pos"][frame, i]))),
                float(np.max(abs(np.asarray(rot.to_matrix()) -
                                 np.asarray(Quaternion(recorded["geom_quat"][frame, i]).to_matrix())))))
        assert abs(max_error - expected[frame]) < 1e-12, (frame, max_error, expected[frame])
        assert camera_state(scene) == camera, "Camera changed"
        scene.render.filepath = str(args.output / filename)
        bpy.ops.render.render(write_still=True)
        records.append({"frame": frame, "time_s": float(recorded["time"][frame]),
                        "file": filename, "max_pose_error": max_error})
        print("FRAME_DONE", json.dumps(records[-1]), flush=True)
    report = {"native_scene": str(native_scene), "source_replay": str(replay),
              "episode": provenance["episode"], "camera": camera,
              "camera_unchanged": True, "render_resolution": [640, 640],
              "blender": bpy.app.version_string, "device": devices, "samples": 32,
              "render_seed": scene.cycles.seed, "render_defaults": DEFAULTS,
              "materials": materials, "frames": records}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("FIG2_FRAMES_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
