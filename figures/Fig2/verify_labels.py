"""Check exported geometry against recorded labels through independent projections."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np


def verify(episode, assets):
    a = dict(np.load(assets/'labels.npz'))
    provenance = json.loads((assets/'sources.json').read_text(encoding='utf-8'))
    tick = provenance['capture_tick']
    with h5py.File(episode, 'r') as f:
        xy=a['source_pixel_xy'];x,y=xy.T
        cam=f['policy/world_from_camera_cv'][tick+1,0]
        K=f['policy/camera_intrinsics'][tick+1,0]
        cp=(a['future_world_m'][:,0]-cam[:3,3])@cam[:3,:3]
        projected=cp@K.T;uv=projected[:,:2]/projected[:,2,None]
        stored=f['supervision/flow_2d_px'][tick,0][y,x]
        native_valid=f['supervision/flow_valid'][tick,0][y,x]
        native_visible=f['supervision/flow_future_visible'][tick,0][y,x]
        error=np.max(np.abs((uv-xy)[native_valid]-stored[native_valid]))
        assert error < 1e-4,error
        assert np.array_equal(a['future_visible'][:,0][native_valid],native_visible[native_valid])
        assert np.array_equal(a['depth_m'],f['policy/depth_m'][tick,0])
        assert np.array_equal(a['history_pose_world_xyzw'],f['supervision/target_object_pose_world'][tick-7:tick+1])
        assert np.array_equal(a['future_pose_world_xyzw'],f['supervision/target_object_pose_world'][tick+1:tick+9])
        assert np.array_equal(a['action_value'],f['action/value'][tick:tick+8])
        base=a['T_robot_base_from_world']
        reconstructed=a['eef_world_m']@base[:3,:3].T+base[:3,3]
        eef_error=float(np.max(abs(reconstructed-f['policy/eef_position'][tick:tick+9])))
        assert eef_error < 1e-10
        meta=json.loads(f['metadata/episode_json'][()].decode())
        ids=a['source_geom_id'];table=meta['geom_table']
        static=np.array([table[g]['body_identity']=='world' for g in ids])
        static_max=float(np.max(np.linalg.norm(a['flow_robot_base_m'][static],axis=-1)))
        assert static_max < 1e-7
        target=np.array([table[g]['instance_identity']=='target' for g in ids])
        # This episode is translation-only until after all shown horizons.
        target_difference=float(np.max(abs(a['flow_robot_base_m'][target]-a['target_displacement_robot_base_m'][None])))
        assert target_difference < 1e-6
    result=dict(native_adjacent_flow_projection_max_px=float(error),
                native_adjacent_visibility_equal=True, static_flow_max_m=static_max,
                eef_frame_roundtrip_max_m=eef_error,
                target_flow_pose_max_difference_m=target_difference,
                exact_source_arrays=True, future_horizons=8, source_points=196)
    (assets/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--episode',type=Path,required=True)
    p.add_argument('--assets',type=Path,default=Path(__file__).parent/'assets')
    args=p.parse_args();verify(args.episode,args.assets)
