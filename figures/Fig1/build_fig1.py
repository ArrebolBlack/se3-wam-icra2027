"""Selected three-column teaser: E near view, black-box b top, linear c.

Run with the paper Python environment; then run render_fig1.mjs for PDF/PNG.
"""
from pathlib import Path
from html import escape
import base64, json, math
import numpy as np
from PIL import Image
from draw_latency import table_rows, render_latency

ROOT=Path(__file__).resolve().parent
A=ROOT/'data/reference_frames'
D=dict(np.load(ROOT/'data/labels.npz'))
D.update(rgb=np.asarray(Image.open(ROOT/'data/frame_tau_rgb.png')),depth=np.load(ROOT/'data/frame_tau_depth_m.npy'),
         base_from_world=np.load(ROOT/'data/base_from_world.npy'))
W,H=2900,1000
C=dict(ink='#2D3638',gray='#677170',muted='#87908D',line='#D8DDDA',
       warm='#F3F1EB',paper='#FCFDFC',coral='#D85A30',coral_bg='#FCF0E9',
       teal='#168E75',teal_bg='#EDF6F2')
S=[]
def put(s): S.append(s)
def attr(a): return ''.join(f' {k.replace("_","-")}="{v}"' for k,v in a.items())
def group(name,**a):put(f'<g id="{name}"{attr(a)}>')
def end():put('</g>')
def text(x,y,s,fs=35,c=None,b=False,anchor='start',**a):
    put(f'<text x="{x}" y="{y}" font-size="{fs}" fill="{c or C["ink"]}" font-weight="{700 if b else 400}" text-anchor="{anchor}"{attr(a)}>{escape(s)}</text>')
def rect(x,y,w,h,fill='none',stroke='none',sw=2,rx=0,**a):
    put(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"{attr(a)}/>')
def path(d,c=None,sw=2.5,fill='none',dash=None,arrow=None,**a):
    if dash:a['stroke_dasharray']=dash
    if arrow:a['marker_end']=f'url(#{arrow})'
    put(f'<path d="{d}" fill="{fill}" stroke="{c or C["gray"]}" stroke-width="{sw}"{attr(a)}/>')
def line(x,y,u,v,**kw):path(f'M{x:.2f},{y:.2f} L{u:.2f},{v:.2f}',**kw)
def circle(x,y,r,fill,stroke='none',sw=2,**a):
    put(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{attr(a)}/>')
def ellipse(x,y,rx,ry,fill,**a):
    put(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"{attr(a)}/>')
def image(x,y,w,h,filename,opacity=1):
    p=ROOT/'data/frame_tau_rgb.png' if filename=='frame-29.png' else A/filename
    data=base64.b64encode(p.read_bytes()).decode()
    put(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{data}" opacity="{opacity}"/>')
def stacked_frames(x,y,size,frames):
    for j,frame in enumerate(frames):
        xx=x+(len(frames)-1-j)*15; yy=y-(len(frames)-1-j)*14
        rect(xx-1,yy-1,size+2,size+2,'#FFFFFF',C['line'],1.8,3)
        image(xx,yy,size,size,f'frame-{frame:02}.png')
def triangle(x,y,r,fill,stroke=None):
    path(f'M{x},{y-r} L{x+r*.9},{y+r*.65} L{x-r*.9},{y+r*.65} Z',stroke or fill,2.3,fill)

def main():
    S.clear()
    cam=D['world_from_camera_cv']; K=D['camera_intrinsics']; p0=D['target_position_world_m'][0]
    V=np.array([[.928,-.371,0],[.2,.5,-.843]])
    def project(x):return (np.asarray(x)-p0)@V.T
    def lift(px):
        px=np.asarray(px); z=D['depth'][px[:,1].astype(int),px[:,0].astype(int)]
        return ((np.c_[px,np.ones(len(px))]@np.linalg.inv(K).T)*z[:,None])@cam[:3,:3].T+cam[:3,3]
    yy,xx=np.mgrid[0:224:2,0:224:2]; pixels=np.c_[xx.ravel(),yy.ravel()]
    cloud=lift(pixels)
    select=(np.linalg.norm(cloud[:,:2]-p0[:2],axis=1)<.62)&(cloud[:,2]>.58)&(cloud[:,2]<1.2)
    cloud=cloud[select]; pixels=pixels[select]
    cloud_uv=project(cloud)
    bounds=np.array([cloud_uv.min(axis=0),cloud_uv.max(axis=0)])
    def fit(uv,x,y,w,h,b=bounds):
        scale=min(w/(b[1,0]-b[0,0]),h/(b[1,1]-b[0,1]))
        return (np.asarray(uv)-b.mean(axis=0))*scale+np.array([x+w/2,y+h/2]),scale
    scene_box=(585,500,940,400)
    scene_points,scene_scale=fit(cloud_uv,*scene_box)
    src=lift(D['source_px_xy'])
    world_from_base=np.linalg.inv(D['base_from_world'])
    flow=D['flow_robot_base_m']@world_from_base[:3,:3].T
    src_px,_=fit(project(src),*scene_box)
    dst_px,_=fit(project(src+flow[:,-1]*3),*scene_box)
    near=(np.linalg.norm(src[:,:2]-p0[:2],axis=1)<.62)&(src[:,2]>.58)&(src[:,2]<1.2)
    shown=near&D['flow_valid'][:,-1]&D['flow_visible'][:,-1]
    valid=shown&(np.linalg.norm(flow[:,-1],axis=1)>1e-6)

    put(f'<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{6.875*H/W:.6f}in" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
    put('<title id="title">FoveaWAM: role-aware geometric futures</title>')
    put('<desc id="desc">Video WAM representation compared with role-aware FoveaWAM geometric supervision. Current point cloud and future labels are reference data, not model predictions. Panel c uses Paused SR and native p95. The FoveaWAM point and speedup are provisional layout values.</desc>')
    put('<defs>')
    for key,size in [('gray',10),('coral',9),('teal',9),('flow',5)]:
        col=C['teal'] if key=='flow' else C[key]
        put(f'<marker id="{key}" viewBox="0 0 10 10" markerWidth="{size}" markerHeight="{size}" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 Z" fill="{col}"/></marker>')
    put('<style>text{font-family:Arial,Helvetica,sans-serif;font-variant-numeric:tabular-nums}path{stroke-linecap:round;stroke-linejoin:round}</style>')
    put('</defs>')
    rect(0,0,W,H,'#FFFFFF')

    group('panel-headings')
    text(45,62,'(a) Video WAMs',40,b=True)
    text(565,62,'(b) FoveaWAM',40,b=True)
    text(45,119,'Dense visual futures',35,C['gray'])
    text(565,119,'Role-aware 4D geometry',35,C['gray'])
    line(510,40,510,947,c=C['line'],sw=2)
    line(1870,40,1870,947,c=C['line'],sw=2)
    end()

    group('video-future-comparison')
    text(64,196,'Observations',34,C['gray'])
    stacked_frames(82,239,180,[22,25,29])
    path('M225,419 V455',sw=3,arrow='gray')
    rect(105,468,265,86,C['warm'],'#9A9D96',2.4,13)
    text(237.5,525,'Video WAM',38,b=True,anchor='middle')
    path('M237,554 V592 H155 V642',sw=3,arrow='gray')
    path('M237,592 H375 V686',sw=3,arrow='gray')
    circle(237,592,3.4,C['gray'])
    stacked_frames(61,673,182,[30,33,37])
    text(61,902,'Future pixels',34,C['gray'])
    for i in range(3):rect(314+i*43,700,32,37,'#B0B4AC',rx=4)
    text(309,784,'Actions',34,C['gray'])
    end()

    group('foveawam-compact-overview')
    rect(565,190,190,67,'#FBFCFB',C['line'],2,8)
    text(660,235,'RGB-D',36,C['gray'],anchor='middle')
    rect(565,282,190,77,'#FBFCFB',C['line'],2,8)
    text(660,315,'Pose history',30,C['gray'],anchor='middle')
    hp=[(587,344),(613,335),(639,339),(667,334),(696,339),(732,347)]
    path('M'+' L'.join(f'{x},{y}' for x,y in hp),c='#8B928B',sw=2.5)
    for x,y in hp:circle(x,y,3.3,'#8B928B')
    path('M755,224 H800 V270 H838',sw=3,arrow='gray')
    path('M755,316 H800 V270',sw=3)
    circle(800,270,3.6,C['gray'])
    rect(850,222,310,96,C['warm'],'#909A92',2.6,15)
    text(1005,284,'FoveaWAM',43,b=True,anchor='middle')
    path('M1160,245 H1210 V204 H1260',c=C['coral'],sw=2.8,dash='6 6',arrow='coral')
    path('M1160,269 H1231 V252 H1260',c=C['teal'],sw=2.8,dash='6 6',arrow='teal')
    path('M1160,299 H1210 V324 H1260',sw=3,arrow='gray')
    text(1280,215,'Target SE(3)',36,C['coral'])
    text(1280,263,'Sparse 3D flow',36,C['teal'])
    text(1280,335,'Action chunk',35,C['gray'])
    rect(1577,156,219,47,'#F3F5F3',rx=4)
    text(1686.5,191,'TRAIN ONLY',34,C['gray'],True,'middle')
    for i in range(8):rect(1525+i*34,303,25,32,'#C4C9C4' if i%3 else '#8A9691',rx=3)
    end()

    group('role-aware-geometry-hero')
    rect(552,387,1281,556,C['paper'],C['line'],2,12)
    text(580,434,'Geometric future supervision',34,C['gray'])

    # Main scene: neutral current RGB-D geometry, with the actual sparse flow overlay.
    group('metric-scene')
    for k in np.argsort(cloud[:,2]):
        px=pixels[k]
        rgb=D['rgb'][px[1],px[0]].astype(float)
        shade=int(145+.37*(rgb@np.array([.299,.587,.114])))
        if rgb[1]>rgb[0]*1.8 and rgb[1]>rgb[2]*1.4:shade=225
        color=f'#{shade:02x}{min(shade+5,255):02x}{min(shade+1,255):02x}'
        if D['target_mask_tau'][px[1],px[0]]: color=C['coral']
        circle(*scene_points[k],1.72,color)
    for i in range(len(src)):
        if shown[i]:circle(*src_px[i],2.5,'#A6B3AC')
    for i in np.flatnonzero(valid):
        line(*src_px[i],*dst_px[i],c=C['teal'],sw=2.6,arrow='flow')
    end()

    # Full target motion in the scene, without magnifying its physical translation.
    target_px,_=fit(project(D['target_position_world_m']),*scene_box)
    path('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in target_px),c=C['coral'],sw=3.2)
    for i in [0,1,4,8]:
        p=D['target_position_world_m'][i]; R=D['target_rotation_world'][i]
        q=np.vstack([p,p+R[:,0]*.035,p+R[:,1]*.025,p+R[:,2]*.025])
        qp,_=fit(project(q),*scene_box)
        for j,col in [(1,C['coral']),(2,'#A8806F'),(3,'#AC9990')]:
            line(*qp[0],*qp[j],c=col,sw=2.4)
        circle(*qp[0],3.8,C['coral'])
    now=target_px[0]
    rect(now[0]-38,now[1]-37,76,74,stroke=C['coral'],sw=2.1,rx=4)
    text(now[0]-53,now[1]+70,'τ',34,C['gray'],anchor='end')

    # Target detail is an explicitly separated pose sequence, not stretched scene motion.
    rect(1180,440,620,228,C['coral_bg'],rx=17)
    text(1485,476,'Precise target SE(3)',34,C['coral'],True,'middle')
    line(now[0]+38,now[1]-37,1320,668,c='#B6A59B',sw=2)
    line(now[0]-38,now[1]-37,1200,668,c='#B6A59B',sw=2)
    corners=np.array([[a,b,c] for a in [-.025,.025] for b in [-.017,.017] for c in [-.012,.012]])
    poses=[corners@D['target_rotation_world'][i].T+D['target_position_world_m'][i] for i in range(9)]
    puv=np.concatenate([project(p) for p in poses])
    pb=np.array([puv.min(axis=0)-.012,puv.max(axis=0)+.012])
    edges=[(i,j) for i in range(8) for j in range(i+1,8) if bin(i^j).count('1')==1]
    for x,i,label in [(1202,1,'+50 ms'),(1404,4,'+200 ms'),(1606,8,'+400 ms')]:
        old,_=fit(project(poses[0]),x,490,180,111,pb)
        new,_=fit(project(poses[i]),x,490,180,111,pb)
        for a,b in edges:line(*old[a],*old[b],c='#D9CEC6',sw=1.5)
        for a,b in edges:line(*new[a],*new[b],c=C['coral'],sw=2.8)
        p=D['target_position_world_m'][i]; R=D['target_rotation_world'][i]
        axes=np.vstack([p,p+R[:,0]*.036,p+R[:,1]*.03,p+R[:,2]*.032])
        ap,_=fit(project(axes),x,490,180,111,pb)
        for j,col in [(1,C['coral']),(2,'#8D6654'),(3,'#B29684')]:
            line(*ap[0],*ap[j],c=col,sw=2.5)
        circle(*ap[0],3.7,C['coral'])
        text(x+90,640,label,34,C['gray'],anchor='middle')

    line(1450,740,1481,740,c=C['teal'],sw=3.4,arrow='teal')
    text(1498,752,'Sparse 3D flow',34,C['teal'],True)
    text(1498,800,'14 × 14 anchors',34,C['gray'])
    text(1498,844,'+400 ms',34,C['muted'])
    end()

    chart,chart_metadata=render_latency()
    put(chart)
    put('</svg>')
    (ROOT/'fig1.svg').write_text('\n'.join(S),encoding='utf8')
    report=dict(selected_b_lower='E: gray point cloud, near orthographic view',point_cloud_samples=len(cloud),
        visible_anchors_in_crop=int(shown.sum()),flow_vectors_displayed=int(valid.sum()),flow_horizon_ms=400,
        flow_display_magnification=3,flow_nonzero_tolerance_m=1e-6,
        scene_crop='Target XY radius <0.62 m; 0.58<world z<1.2 m',
        point_cloud='Current RGB-D reference geometry; target mask points are coral.',
        poses='Ground-truth supervision at +50, +200 and +400 ms. Cuboids are pose glyphs.',
        chart=chart_metadata,width_in=6.875,height_in=6.875*H/W)
    (ROOT/'layout_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'svg_bytes':(ROOT/'fig1.svg').stat().st_size,'point_cloud_samples':len(cloud),'flow_vectors':int(valid.sum())}))


if __name__ == '__main__':
    main()
