"""Two-panel visual teaser: a large recorded point cloud and the current Table 1 plot."""
from pathlib import Path
from html import escape
import json,math,xml.etree.ElementTree as E
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT
PAPER=ROOT
from draw_latency import render_latency, table_rows
NS={'s':'http://www.w3.org/2000/svg'}
E.register_namespace('','http://www.w3.org/2000/svg')
W,H=2900,1000
C=dict(ink='#2D3638',gray='#677170',muted='#87908D',line='#D8DDDA',coral='#D85A30',teal='#168E75')
S=[]
def put(s):S.append(s)
def attr(a):return ''.join(f' {k.replace("_","-")}="{v}"' for k,v in a.items())
def group(name):put(f'<g id="{name}">')
def end():put('</g>')
def text(x,y,t,fs=32,c=None,b=False,anchor='start',**a):
    put(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{fs}" fill="{c or C["gray"]}" font-weight="{700 if b else 400}" text-anchor="{anchor}"{attr(a)}>{escape(t)}</text>')
def path(d,c=None,sw=2,fill='none',arrow=None,**a):
    if arrow:a['marker_end']='url(#'+arrow+')'
    put(f'<path d="{d}" fill="{fill}" stroke="{c or C["gray"]}" stroke-width="{sw}"{attr(a)}/>')
def line(a,b,**kw):path(f'M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f}',**kw)
def dot(p,r,fill,stroke='none',sw=0):put(f'<circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def rect(x,y,w,h,fill='none',stroke='none',sw=1.5,rx=0):put(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>')
def halo_head(a,b,size=10):
    angle=math.atan2(b[1]-a[1],b[0]-a[0]);R=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    pts=np.array([[-.9*size,-.5*size],[.1*size,0],[-.9*size,.5*size]])@R.T+b
    path('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in pts)+' Z',c='none',sw=0,fill='#FFFFFF')

def main():
    S.clear()
    D=dict(np.load(PAPER/'data/labels.npz'))
    rgb=np.asarray(Image.open(PAPER/'data/frame_tau_rgb.png'))
    depth=np.load(PAPER/'data/frame_tau_depth_m.npy')
    world_from_base=np.linalg.inv(np.load(PAPER/'data/base_from_world.npy'))
    cam=D['world_from_camera_cv'];K=D['camera_intrinsics'];p0=D['target_position_world_m'][0]
    def lift(pixels):
        z=depth[pixels[:,1].astype(int),pixels[:,0].astype(int)]
        return ((np.c_[pixels,np.ones(len(pixels))]@np.linalg.inv(K).T)*z[:,None])@cam[:3,:3].T+cam[:3,3]
    view=np.array([1.15,-1.75,1.30]);view/=np.linalg.norm(view)
    right=np.cross([0,0,1],view);right/=np.linalg.norm(right);up=np.cross(view,right)
    def project(p):return np.asarray(p)@np.array([right,-up]).T
    yy,xx=np.mgrid[0:224,0:224];pixels=np.c_[xx.ravel(),yy.ravel()]
    cloud=lift(pixels);z=depth[pixels[:,1],pixels[:,0]]
    selected=(z>0)&(z<1.8)&(cloud[:,2]>p0[2]-.06)&(np.linalg.norm(cloud[:,:2]-p0[:2],axis=1)<.62)
    cloud=cloud[selected];pixels=pixels[selected]
    src=lift(D['source_px_xy']);flow=D['flow_robot_base_m']@world_from_base[:3,:3].T
    source_depth=depth[D['source_px_xy'][:,1].astype(int),D['source_px_xy'][:,0].astype(int)]
    shown=(source_depth>0)&(source_depth<1.8)&(src[:,2]>p0[2]-.06)&(np.linalg.norm(src[:,:2]-p0[:2],axis=1)<.62)&D['flow_valid'][:,-1]&D['flow_visible'][:,-1]
    moving=shown&(np.linalg.norm(flow[:,-1],axis=1)>1e-6)
    corners=np.array([[a,b,c] for a in [-.025,.025] for b in [-.017,.017] for c in [-.012,.012]])
    poses=[corners@D['target_rotation_world'][i].T+D['target_position_world_m'][i] for i in range(9)]
    extent=np.concatenate([project(cloud),project(src[moving]+flow[moving,-1]*3),project(np.concatenate(poses))])
    lo,hi=extent.min(0),extent.max(0)
    scene_box=np.array([-100.,145.,1500.,805.])
    scale=min(scene_box[2]/(hi[0]-lo[0]),scene_box[3]/(hi[1]-lo[1]))
    def screen(p):return (np.asarray(p)-(lo+hi)/2)*scale+scene_box[:2]+scene_box[2:]/2
    cloud_px=screen(project(cloud));src_px=screen(project(src));dst_px=screen(project(src+flow[:,-1]*3))

    put(f'<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{6.875*H/W:.6f}in" viewBox="0 0 {W} {H}" role="img">')
    put('<title>FoveaWAM: role-aware geometric futures and success versus latency</title>')
    put('<desc>A large colored point cloud from a recorded RGB-D observation, sparse 400 ms flow labels displayed at 3x, and precise target pose labels. These are supervision examples, not model predictions. Right: current Table 1 Paused SR versus measured native p95.</desc>')
    put('<defs>')
    for key,size in [('gray',10),('coral',9),('teal',9),('flow',7.5)]:
        col=C['teal'] if key=='flow' else C[key]
        put(f'<marker id="{key}" viewBox="0 0 10 10" markerWidth="{size}" markerHeight="{size}" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 Z" fill="{col}"/></marker>')
    put('<style>text{font-family:Arial,Helvetica,sans-serif;font-variant-numeric:tabular-nums}path{stroke-linecap:round;stroke-linejoin:round}</style></defs>')
    rect(0,0,W,H,'#FFFFFF')
    group('Hero_Labels')
    text(45,62,'(a) FoveaWAM',40,C['ink'],True)
    text(45,119,'Role-aware 4D geometry',32)
    text(1805,62,'Geometric supervision',25,C['muted'],anchor='end')
    end()
    group('Scene_Cloud')
    for k in np.argsort(cloud@view):
        px=pixels[k];v=rgb[px[1],px[0]]
        color='#'+''.join(f'{int(c):02x}' for c in v)
        if D['target_mask_tau'][px[1],px[0]]:color=C['coral']
        dot(cloud_px[k],1.65,color)
    end()
    group('Scene_Anchors')
    for i in np.flatnonzero(shown&~moving):dot(src_px[i],2.5,'#ADB8B1')
    end()
    group('Scene_Flow')
    for i in np.flatnonzero(moving):
        a,b=src_px[i],dst_px[i]
        line(a,b,c='#FFFFFF',sw=5.8);halo_head(a,b)
        line(a,b,c=C['teal'],sw=3,arrow='flow')
        dot(a,3.3,C['teal'],'#FFFFFF',.9)
    end()

    group('Target_Path')
    target_px=screen(project(D['target_position_world_m']))
    path('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in target_px),c=C['coral'],sw=3.2)
    for i in [0,1,4,8]:dot(target_px[i],4.4,C['coral'],'#FFFFFF',.9)
    target_bounds=screen(project(np.concatenate(poses)))
    target_lo=target_bounds.min(0)-10;target_hi=target_bounds.max(0)+10
    rect(*target_lo,*(target_hi-target_lo),stroke=C['coral'],sw=2.8)
    # Leaders denote a magnified pose-detail panel, not physical displacement vectors.
    line([target_hi[0],target_lo[1]],[1255,605],c='#C8A18E',sw=1.8)
    line(target_hi,[1255,835],c='#C8A18E',sw=1.8)
    end()

    group('Target_Detail')
    rect(1255,605,570,230,'#FFFFFF','#DDB7A6',1.6,3)
    pb=np.array([project(np.concatenate(poses)).min(0)-.012,project(np.concatenate(poses)).max(0)+.012])
    def pose_screen(uv,x):
        size=np.array([170.,125.]);s=min(size/(pb[1]-pb[0]))
        return (np.asarray(uv)-pb.mean(0))*s+[x+85,690]
    edges=[(i,j) for i in range(8) for j in range(i+1,8) if bin(i^j).count('1')==1]
    for x,i,label in [(1270,1,'+50 ms'),(1455,4,'+200 ms'),(1640,8,'+400 ms')]:
        old=pose_screen(project(poses[0]),x);new=pose_screen(project(poses[i]),x)
        for a,b in edges:line(old[a],old[b],c='#D5D0CB',sw=1.6)
        for a,b in edges:line(new[a],new[b],c=C['coral'],sw=3)
        p=D['target_position_world_m'][i];R=D['target_rotation_world'][i]
        q=pose_screen(project(np.vstack([p,p+R[:,0]*.036,p+R[:,1]*.03,p+R[:,2]*.032])),x)
        for j,col in [(1,C['coral']),(2,'#8D6654'),(3,'#B29684')]:line(q[0],q[j],c=col,sw=2.6)
        dot(q[0],3.8,C['coral'])
        text(x+85,804,label,29,anchor='middle')
    end()

    group('Hero_Annotations')
    text(1290,570,'Precise target SE(3)',34,C['coral'],True)
    text(1280,258,'Sparse 3D flow',34,C['teal'],True)
    text(1280,304,'14 × 14 anchors',30)
    text(1280,346,'+400 ms',29,C['muted'])
    line([1244,246],[1270,246],c=C['teal'],sw=3,arrow='teal')
    text(45,965,'Current scene point cloud',28,C['gray'])
    end()

    chart,chart_meta=render_latency()
    cg=E.fromstring(chart);cg.set('id','Performance')
    for t in cg.findall('text'):
        if t.text=='(c) Success vs. latency':t.text='(b) Success vs. latency'
        if t.text=='FoveaWAM' or (t.text and '%'+('†' if chart_meta['ours']['prior_sync_reference'] else '')+' · ' in t.text):
            t.set('x',str(float(t.get('x'))+60))
        if t.text=='50 ms':
            t.set('x','2242');t.set('y','785');t.set('text-anchor','start')
    for r in cg.findall('rect'):
        if float(r.get('width'))==220 and float(r.get('height'))==78:r.set('x',str(float(r.get('x'))+60))
    put(E.tostring(cg,encoding='unicode'))
    group('Page_Furniture')
    line([1870,40],[1870,947],c=C['line'],sw=2)
    end()
    put('</svg>')
    (OUT/'fig1.svg').write_text('\n'.join(S),encoding='utf8')

    report=dict(layout='Two panels: geometric visualization and performance',
        source_frame=29,time_s=1.45,cloud_points=len(cloud),cloud_pixel_stride=1,
        depth_clip_m=1.8,z_min_world_m=float(p0[2]-.06),target_xy_crop_radius_m=.62,
        view_vector=view.tolist(),cloud_colors='Observed RGB; target mask highlighted coral',
        visible_valid_anchors=int(shown.sum()),nonzero_flow_vectors=int(moving.sum()),
        flow_horizon_ms=400,flow_display_magnification=3,nonzero_tolerance_m=1e-6,
        target_horizons_ms=[50,200,400],target_main_translation_magnification=1,
        scene_box=scene_box.tolist(),chart=chart_meta,width_in=6.875,height_in=6.875*H/W,
        geometry='Current recorded RGB-D; future geometry is ground-truth supervision')
    (ROOT/'layout_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'cloud_points':len(cloud),'flow_vectors':int(moving.sum()),'ours_ms':chart_meta['ours']['p95_ms']}))


if __name__=='__main__':
    main()
