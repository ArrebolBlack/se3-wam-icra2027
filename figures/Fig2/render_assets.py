"""Re-render Fig. 3's saved orthographic context with the shared studio defaults.

Run with the research repository's Blender Python environment. The saved camera,
display clipping and frame-29 transforms remain unchanged. RGB reuses the
already validated agentview frame from figures/paradigms.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Quaternion, Vector

ROOT = Path(__file__).resolve().parent


def camera_state(scene):
    camera = scene.camera
    return {"name": camera.name, "matrix_world": list(map(list, camera.matrix_world)),
            "type": camera.data.type, "ortho_scale": camera.data.ortho_scale,
            "shift_x": camera.data.shift_x, "shift_y": camera.data.shift_y,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y]}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--research-root", type=Path,
                        default=Path(os.environ.get("SE3WAM_RESEARCH", "C:/workspace/se3-wam-research")))
    args = parser.parse_args()
    sys.path.insert(0, str(args.research_root / "scripts/benchmark_infra/mujoco_blender"))
    from studio_controls import DEFAULTS

    assets = ROOT / "assets"
    context = assets / "blender"
    source_path = context / "source.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    replay = Path(source["source_scene"]).parents[3] / "recordings/t5_replan/recording/replay"
    recorded = np.load(replay / "trajectory.npz")
    bpy.ops.wm.open_mainfile(filepath=str(context / "flow_context.blend"))
    scene = bpy.context.scene
    camera = camera_state(scene)
    current = next(c for c in bpy.data.collections if c.name.startswith("Current"))
    objects = [o for o in current.objects if "mujoco_geom_id" in o]
    transforms = {o.name: list(map(list, o.matrix_world)) for o in objects}
    error = 0.0
    for obj in objects:
        i = int(obj["mujoco_geom_id"])
        position, rotation, _ = obj.matrix_world.decompose()
        assert obj["sample_index"] == 29
        error = max(error, float(np.max(abs(np.asarray(position) - recorded["geom_pos"][29, i]))),
                    float(np.max(abs(np.asarray(rotation.to_matrix()) -
                                     np.asarray(Quaternion(recorded["geom_quat"][29, i]).to_matrix())))))
    assert abs(error - source["max_recorded_pose_error"]) < 1e-12, error

    # Undo the old figure-specific white-body darkening, then use the defaults.
    for change in source["presentation_refinement"]["changes"]:
        material = bpy.data.materials[change["material"]]
        material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = change["before"]
        material.diffuse_color = change["before"]
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = DEFAULTS["look"]
    scene.view_settings.exposure = DEFAULTS["exposure"]
    scene.view_settings.gamma = DEFAULTS["gamma"]
    assert not scene.use_nodes
    assert DEFAULTS["saturation"] == 1 and DEFAULTS["hue"] == 0
    assert not any(DEFAULTS[k] for k in ("belt_color_enabled", "floor_color_enabled", "table_color_enabled"))
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = DEFAULTS["world_strength"]
    for key, name in (("key", "Key softbox"), ("fill", "Fill softbox"), ("rim", "Rim softbox")):
        light = bpy.data.lights[name]
        light.energy, light.size = DEFAULTS[f"{key}_energy"], DEFAULTS[f"{key}_size"]
    material_count = 0
    for material in bpy.data.materials:
        bsdf = material.node_tree.nodes.get("Principled BSDF") if material.use_nodes else None
        if bsdf is not None:
            bsdf.inputs["Specular IOR Level"].default_value = DEFAULTS["specular"]
            bsdf.inputs["Roughness"].default_value = DEFAULTS["roughness"]
            material_count += 1

    patch = np.load(assets / "geometry_labels.npz")["patch_xyz_world"]
    projected = np.stack([patch @ source["right"], -patch @ np.asarray(source["up"])], axis=-1)
    expected = (projected - source["projection_center"]) * source["paper_scale"] + [82.5, 44]
    uv = np.array([world_to_camera_view(scene, scene.camera, Vector(p))[:2] for p in patch])
    measured = np.stack([uv[:, 0] * 165, (1 - uv[:, 1]) * 88], axis=-1)
    projection_error = float(np.max(abs(measured - expected)))
    assert projection_error < 3e-5, projection_error
    assert camera_state(scene) == camera
    assert all(list(map(list, o.matrix_world)) == transforms[o.name] for o in objects)

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
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(context / "flow_context.png")
    bpy.ops.render.render(write_still=True)
    scene.render.filepath = "//flow_context.png"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(context / "flow_context.blend"))
    shutil.copyfile(ROOT.parent / "paradigms/assets/frame_now.png", assets / "rgb.png")
    report = {"camera": camera, "camera_and_transforms_unchanged": True,
              "max_recorded_pose_error": error, "max_projection_error_at_165x88": projection_error,
              "studio_defaults": DEFAULTS, "material_count": material_count,
              "device": devices, "samples": scene.cycles.samples, "seed": scene.cycles.seed,
              "white_body": "original material colors restored; roughness 0.34",
              "rgb_source": "../paradigms/assets/frame_now.png"}
    source["render_update_20261116"] = report
    source["presentation_refinement"]["status"] = "superseded: original colors and shared roughness restored"
    source_path.write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    report_path = ROOT.parents[1] / "build/fig3-assets-20261116/render_validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pose_error": error, "projection_error": projection_error, "specular": DEFAULTS["specular"]}))


if __name__ == "__main__":
    main()
