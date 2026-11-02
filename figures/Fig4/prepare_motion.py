"""MuJoCo FK replay of real states; no physics steps, pose edits or image synthesis.

Historical vector silhouettes are traced from segmentation at the same real states.
Visibility is respected in the historical frame and against the current frame's
depth (including robot and canopy). Source RGB/depth/masks remain available.
"""
from pathlib import Path
from contextlib import ExitStack
import argparse, json, sys
import numpy as np
import mujoco, cv2, h5py
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=None
SIZE=1024
PANELS=[
 ('grasp','Harmonic grasp','Grasp',[.25,1.1],[0,340]),
 ('t1_belt','Conveyor grasp','Grasp',[.3,1.1,1.9],[0,330]),
 ('t1_xyz','Translating grasp','Grasp',[0,.5,1.0],[0,330]),
 ('t1_so3','Rotating grasp','Grasp',[0,.7,1.4],[0,330]),
 ('t1_occ','Occluded grasp','Grasp',[.5,1.25,2.0],[160,330]),
 ('t2_trans','Moving receptacle','Place',[0,1.4,2.8],[0,260]),
 ('t2_se3','Rotating receptacle','Place',[0,1.65,3.3],[0,260]),
 ('t3_phase','Wire passage','Pass',[10,15,20],[215,270]),
 ('t3_full','Wire passage, full','Pass',[10,15,20],[215,270]),
 ('t4_sphere','Ball capture','Capture',[.2,.45,.7],[70,180]),
 ('t4_sphere_tabletop','Ball capture, table','Capture',[.15,.4,.65],[30,330]),
 ('t4_slider','Slider capture','Capture',[.1,.35,.6],[30,330]),
 ('t4_can','Can capture','Capture',[.15,.4,.65],[30,330]),
 ('t5_replan','Post-impact grasp','Impact',[.8,1.45,2.1],[0,300]),
]
CROP=[800,510]

def matrix(q):
    a=np.empty(9);mujoco.mju_quat2Mat(a,q);return a.reshape(3,3)

def project(p,cp,cq,fovy):
    a=(np.asarray(p)-cp)@matrix(cq)
    f=SIZE/(2*np.tan(np.deg2rad(fovy)/2))
    return np.stack([SIZE/2+f*a[...,0]/(-a[...,2]),SIZE/2-f*a[...,1]/(-a[...,2])],axis=-1)

def contours(mask):
    cs,_=cv2.findContours(mask.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.approxPolyDP(c,.65,True)[:,0].tolist() for c in cs if cv2.contourArea(c)>3]

def render(panel):
    task,name,family,times,origin=panel
    folder=SOURCE/'recordings'/task/'recording/replay';out=ROOT/'assets'/task;out.mkdir(parents=True,exist_ok=True)
    meta=json.loads((folder/'scene.json').read_text());a=dict(np.load(folder/'trajectory.npz'))
    assert meta['mujoco_version']==mujoco.__version__
    cam=meta['cameras'].index('agentview')
    indices=[int(np.argmin(abs(a['time']-t))) for t in times]
    model=load_model(folder,int(a['model_epoch'][indices[-1]]));data=mujoco.MjData(model)
    model.vis.global_.offwidth=SIZE;model.vis.global_.offheight=SIZE
    option=mujoco.MjvOption();option.geomgroup[:]=0;option.geomgroup[meta['geom_groups']]=1;option.sitegroup[:]=0
    body='goal_main' if task.startswith('t2') else 'wire_main' if task.startswith('t3') else 'target_main'
    gids=[g['id'] for g in meta['geoms'] if g['body']==body]
    bid=model.body(body).id
    obstacle_ids=[g['id'] for g in meta['geoms'] if g['body']=='occluder_main' or (task=='t4_sphere' and g['name'] in ('safety_tray_collision','table_visual'))]
    if task.startswith('t3'):obstacle_ids=[g['id'] for g in meta['geoms'] if g['name'].startswith('wire_segment')]
    frame_records=[];arrays=[];errors=[]
    epoch=int(a['model_epoch'][indices[-1]])
    with ExitStack() as stack:
        renderer=stack.enter_context(mujoco.Renderer(model,width=SIZE,height=SIZE))
        for j,i in enumerate(indices):
            if int(a['model_epoch'][i])!=epoch:
                renderer.close()
                epoch=int(a['model_epoch'][i]);model=load_model(folder,epoch);data=mujoco.MjData(model)
                model.vis.global_.offwidth=SIZE;model.vis.global_.offheight=SIZE
                renderer=stack.enter_context(mujoco.Renderer(model,width=SIZE,height=SIZE))
            mujoco.mj_setState(model,data,a['state'][i],meta['state_spec']);mujoco.mj_forward(model,data)
            errors.append(float(np.max(abs(data.geom_xpos-a['geom_pos'][i]))))
            assert errors[-1]<1e-10
            renderer.update_scene(data,camera='agentview',scene_option=option)
            rgb=renderer.render().copy();renderer.enable_depth_rendering();depth=renderer.render().copy();renderer.disable_depth_rendering()
            renderer.enable_segmentation_rendering();seg=renderer.render().copy();renderer.disable_segmentation_rendering()
            mask=np.isin(seg[:,:,0],gids)&(seg[:,:,1]==int(mujoco.mjtObj.mjOBJ_GEOM))
            Image.fromarray(rgb).save(out/f'frame_{j}.png');Image.fromarray((mask*255).astype('uint8')).save(out/f'target_mask_{j}.png')
            arrays.append((depth,seg,mask))
            frame_records.append(dict(frame_file=f'assets/{task}/frame_{j}.png',sample_index=i,time_s=float(a['time'][i]),body_position_world_m=a['body_pos'][i,bid].tolist(),body_quaternion_wxyz=a['body_quat'][i,bid].tolist(),visible_pixels=int(mask.sum())))
    cdepth,cseg,cmask=arrays[-1]
    vectors=[]
    for j,(depth,seg,mask) in enumerate(arrays[:-1]):
        # Real historical silhouette, also occluded by foreground in the current view.
        visible=mask&(depth<=cdepth+.002)&~cmask
        Image.fromarray((visible*255).astype('uint8')).save(out/f'overlay_mask_{j}.png')
        vectors.append(contours(visible))
    np.savez_compressed(out/'depth_and_segmentation.npz',depth=np.stack([x[0] for x in arrays]),segmentation=np.stack([x[1] for x in arrays]))
    current=indices[-1]; cp=a['camera_pos'][current,cam];cq=a['camera_quat'][current,cam];fovy=float(a['camera_fovy'][current,cam])
    # Trace real 20 Hz centers. For the rotating wire use its off-axis high bend;
    # the entry and COM lie on the rotation axis and therefore do not translate.
    trace_indices=np.arange(indices[0],indices[-1]+1,max(1,round(.05/float(np.median(np.diff(a['time']))))))
    if trace_indices[-1]!=current:trace_indices=np.append(trace_indices,current)
    positions=a['body_pos'][trace_indices,bid].copy()
    if task.startswith('t3'):
        local=np.asarray(meta['context']['scenario']['geometry']['wire_path_points_frame_m'][8])
        positions+=np.array([matrix(a['body_quat'][i,bid])@local for i in trace_indices])
    points=project(positions,cp,cq,fovy)
    obs=np.isin(cseg[:,:,0],obstacle_ids)&(cseg[:,:,1]==int(mujoco.mjtObj.mjOBJ_GEOM))
    # OCC: do not draw any trajectory behind the canopy. Preserve a real visibility gap.
    allowed=np.ones(len(points),bool)
    if task=='t1_occ':
        for k,(x,y) in enumerate(points):
            if 0<=x<SIZE and 0<=y<SIZE and obs[int(y),int(x)]:allowed[k]=False
    roles={}
    if task.startswith('t3'):
        pts=np.asarray(meta['context']['scenario']['geometry']['wire_path_points_frame_m'])
        world=a['body_pos'][current,bid]+pts@matrix(a['body_quat'][current,bid]).T
        roles['wire_path']=project(world,cp,cq,fovy).tolist();roles['entry']=roles['wire_path'][0]
        gid=model.geom('db0_buzz_fixture_motor_housing_visual').id
        visible=(cseg[:,:,0]==gid).astype('uint8');cx,cy=origin
        inside=np.zeros_like(visible);inside[cy+45:cy+CROP[1]-45,cx+45:cx+CROP[0]-45]=1;visible*=inside
        assert visible.any(),'wire motor must be visible inside the common crop'
        dist=cv2.distanceTransform(visible,cv2.DIST_L2,5);py,px=np.unravel_index(np.argmax(dist),dist.shape)
        roles['driver']=[float(px),float(py)]
    elif task.startswith('t4'):
        roles['driver']=project(data.geom('ramp_visual').xpos,cp,cq,fovy).tolist()
    elif task in ('t1_belt','t1_occ','t5_replan'):
        belt_id=model.geom('belt_visual').id
        belt_mask=(cseg[:,:,0]==belt_id).astype('uint8')
        crop_mask=np.zeros_like(belt_mask);cx,cy=origin
        crop_mask[cy+45:cy+CROP[1]-45,cx+45:cx+CROP[0]-45]=1
        belt_mask*=crop_mask
        dist=cv2.distanceTransform(belt_mask,cv2.DIST_L2,5)
        py,px=np.unravel_index(np.argmax(dist),dist.shape)
        roles['driver']=[float(px),float(py)]
        if task=='t5_replan':
            roles['striker']=project(data.body('left_striker').xpos,cp,cq,fovy).tolist()
    epfile=next((folder.parent/'episodes').glob('*.hdf5'))
    with h5py.File(epfile) as f:ep=json.loads(f['metadata/episode_json'][()])
    manifest=json.loads((folder.parent.parent/'manifest.jsonl').read_text().splitlines()[0])
    cue=None
    if task in ('t1_so3','t2_se3','t3_phase','t3_full'):
        rotation=meta['context']['scenario']['motion'][0]['rotation'];axis=np.array(rotation['axis_world']);sign=np.sign(rotation['angular_speed_rad_s'])
        u=np.array([1.,0,0]) if abs(axis[2])>.5 else np.array([0.,1,0]);v=np.cross(axis,u)
        theta=np.linspace(0,sign*1.65*np.pi,50)
        arc=a['body_pos'][current,bid]+.05*(np.cos(theta[:,None])*u+np.sin(theta[:,None])*v)
        cue={'type':'rotation','projected_icon':project(arc,cp,cq,fovy).tolist(),'angular_speed_rad_s':rotation['angular_speed_rad_s'],'axis_world':axis.tolist(),'meaning':'Qualitative rotation-direction symbol; displayed size and angular span are symbolic, not a historical pose or measured excursion.'}
    if task=='grasp':
        center=a['body_pos'][current,bid];q=project(np.stack([center+[-.04,0,0],center+[.04,0,0]]),cp,cq,fovy)
        cue={'type':'oscillation','projected_icon':q.tolist(),'meaning':'Qualitative bidirectional oscillation symbol along the true world-X harmonic axis; not a historical pose.'}
    if task=='t5_replan':
        onset=ep['event_times_s']['striker_impact_onset'];end=ep['event_times_s']['striker_impact_end']
        impact_indices=np.flatnonzero((a['time']>=onset)&(a['time']<=end));assert len(impact_indices)>0
        ii=int(impact_indices[0]);ip=project(a['body_pos'][ii,bid],cp,cq,fovy)
        assert indices[1] == ii, 'The middle pose must show the recorded impact sample.'
        roles['impact']={'pixel':ip.tolist(),'sample_index':ii,'sample_time_s':float(a['time'][ii]),'contact_interval_s':[onset,end],'meaning':'Target center at a recorded sample inside the actual striker-contact interval; not an asserted contact-point coordinate.'}
    obstacle_contours=contours(obs)
    if task=='t4_sphere':
        # Outline the actual tray perimeter, not the silhouettes of legs occluding it.
        g=model.geom('safety_tray_collision');sx,sy,sz=g.size;pos=data.geom_xpos[g.id];rot=data.geom_xmat[g.id].reshape(3,3)
        vertices=np.array([[-sx,-sy,sz],[sx,-sy,sz],[sx,sy,sz],[-sx,sy,sz],[-sx,-sy,sz]])
        edge_segments=[]
        for start,end in zip(vertices[:-1],vertices[1:]):
            world=np.linspace(start,end,101)@rot.T+pos;pixels=project(world,cp,cq,fovy);z=-((world-cp)@matrix(cq))[:,2];run=[]
            for xy,dep in zip(pixels,z):
                px,py=np.round(xy).astype(int)
                visible=0<=px<SIZE and 0<=py<SIZE and dep<=cdepth[py,px]+.005
                if visible:run.append(xy.tolist())
                elif run:edge_segments.append(run);run=[]
            if run:edge_segments.append(run)
        roles['obstacle_edges']=edge_segments;obstacle_contours=[]
        roles['tray_anchor']=project(pos+rot@np.array([0.,0.,sz]),cp,cq,fovy).tolist()
    record=dict(task_id=task,name=name,family=family,seed=manifest['source_seed'],episode_id=ep['episode_id'],scenario_id=manifest['scenario_id'],policy='native-oracle',camera='agentview',camera_position=cp.tolist(),camera_quaternion_wxyz=cq.tolist(),vertical_fov_deg=fovy,render_pixels=[SIZE,SIZE],crop_xywh=[*origin,*CROP],frames=frame_records,history_contours=vectors,current_contours=contours(cmask),obstacle_contours=obstacle_contours,trajectory_pixels=points.tolist(),trajectory_times_s=a['time'][trace_indices].tolist(),trajectory_visible=allowed.tolist(),roles=roles,motion_cue=cue,events=ep['event_times_s'],max_replay_geometry_error_m=max(errors),status='ready')
    (out/'panel.json').write_text(json.dumps(record,indent=2))
    print(task,'ready',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tasks',nargs='*');p.add_argument('--source-project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    SOURCE=args.source_project;ROOT=args.output
    sys.path.insert(0,str(SOURCE/'scripts'))
    from trajectory import load_model
    for panel in PANELS:
        if args.tasks is None or panel[0] in args.tasks:render(panel)
