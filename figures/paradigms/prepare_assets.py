#!/usr/bin/env python3
"""Project the recorded labels of the Fig. 2 episode into the agent-view renders.

Reads   ../Fig1/data/labels.npz            camera, 14x14 patch pixels, flow end pixels
        ../Fig2/assets/geometry_labels.npz  patch points, 3D flow, target SE(3) at 0..400 ms
        assets/frame_{now,p200,p400}.png    Blender renders of the recorded states (640 px)
Writes  assets/overlay.json                 everything build_paradigms.py draws, in 640-px
                                            image coordinates

Nothing here is a model prediction: flow, poses and silhouettes all come from the recorded
t5_replan episode (frame 29 and its eight 50 ms horizons). Needs numpy, pillow, contourpy.
"""
import json
from pathlib import Path

import contourpy
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
PX = 640
AXIS_M = 0.028          # drawn length of each pose axis
MOVING_M = 0.002        # flow below this is drawn as a static sample


def main():
    cam = np.load(HERE.parent / "Fig1" / "data" / "labels.npz")
    geo = np.load(HERE.parent / "Fig2" / "assets" / "geometry_labels.npz")
    K, world_from_cam = cam["camera_intrinsics"], cam["world_from_camera_cv"]
    cam_from_world = np.linalg.inv(world_from_cam)
    scale = PX / cam["target_mask_tau"].shape[0]

    def project(points):
        points = np.atleast_2d(points)
        pc = (cam_from_world[:3, :3] @ points.T).T + cam_from_world[:3, 3]
        u = K[0, 0] * pc[:, 0] / pc[:, 2] + K[0, 2]
        v = K[1, 1] * pc[:, 1] / pc[:, 2] + K[1, 2]
        return np.column_stack([(u + 0.5) * scale, (v + 0.5) * scale])

    patch, flow = geo["patch_xyz_world"], geo["flow_xyz_world"]
    src = project(patch)
    end = project(patch + flow[:, -1])
    assert np.abs(src - (cam["source_px_xy"] + 0.5) * scale).max() < 1e-6
    assert np.abs(end - (cam["flow_end_px"][:, -1] + 0.5) * scale).max() < 1e-6
    moving = np.linalg.norm(flow[:, -1], axis=1) > MOVING_M

    pos, rot = geo["target_pos_world"], geo["target_R_world"]
    origins = project(pos)
    triads = {}
    for k in (0, 4, 8):
        tips = pos[k] + AXIS_M * rot[k].T          # rows: body x, y, z axes in the world
        triads[str(k)] = {"origin": origins[k].tolist(), "tips": project(tips).tolist()}
    yaw = [float(np.degrees(np.arctan2(r[1, 0], r[0, 0]))) for r in rot]

    outlines = {}
    for k, name in ((0, "frame_now.png"), (4, "frame_p200.png"), (8, "frame_p400.png")):
        rgb = np.asarray(Image.open(ASSETS / name).convert("RGB")).astype(int)
        outlines[str(k)] = trace(target_mask(rgb, origins[k], drop_striker=(k == 0)))

    data = {
        "image_px": PX,
        "episode": "v1:test_id:t5_replan:000000~r000000, frame 29 (1.45 s), horizons 50..400 ms",
        "lattice": [{"src": s.tolist(), "end": e.tolist(), "moving": bool(m), "instance": str(i)}
                    for s, e, m, i in zip(src, end, moving, cam["patch_instance"])],
        "target_origin_px": origins.tolist(),
        "target_yaw_deg": yaw,
        "triads": triads,
        "outlines": outlines,
        "counts": {
            "patches": int(len(src)),
            "patches_on_target": int((cam["patch_instance"] == "target").sum()),
            "moving_patches": int(moving.sum()),
            "target_pixels_at_224": int(cam["target_mask_tau"].sum()),
            "pixels_at_224": int(cam["target_mask_tau"].size),
        },
    }
    (ASSETS / "overlay.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(data["counts"]), "yaw 0/200/400 ms:", [round(yaw[k], 1) for k in (0, 4, 8)])


def target_mask(rgb, origin, drop_striker):
    """Pixels of the target part: the orange component under its projected origin."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    orange = (r - g > 18) & (r - b > 18)        # reddish, including the part's shaded sides
    if drop_striker:                              # the striker touches the target at impact
        orange &= ~((g >= 108) & (b < 96))
    seed = (int(round(origin[1])), int(round(origin[0])))
    mask = np.zeros_like(orange)
    stack = [seed]
    while stack:
        y, x = stack.pop()
        if 0 <= y < PX and 0 <= x < PX and orange[y, x] and not mask[y, x]:
            mask[y, x] = True
            stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return mask


def trace(mask):
    """Outer boundary of a mask as a simplified sub-pixel polygon (pixel-centre + 0.5)."""
    soft = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(1.3))).astype(float) / 255
    lines = contourpy.contour_generator(z=soft).lines(0.5)
    line = max(lines, key=len) + 0.5
    return simplify(line[:-1], 0.3).tolist()


def simplify(points, tol):
    """Ramer-Douglas-Peucker on a closed polygon."""
    def rdp(seg):
        if len(seg) < 3:
            return seg
        a, b = seg[0], seg[-1]
        d = b - a
        n = np.hypot(*d) or 1.0
        dist = np.abs(d[0] * (seg[:, 1] - a[1]) - d[1] * (seg[:, 0] - a[0])) / n
        i = int(dist.argmax())
        if dist[i] <= tol:
            return np.array([a, b])
        return np.vstack([rdp(seg[:i + 1])[:-1], rdp(seg[i:])])
    far = int(np.linalg.norm(points - points[0], axis=1).argmax())
    return np.vstack([rdp(points[:far + 1])[:-1], rdp(np.vstack([points[far:], points[:1]]))[:-1]])


if __name__ == "__main__":
    main()
