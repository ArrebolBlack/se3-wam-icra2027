"""Build editable Blender stills from the already verified Fig.4 recordings.

No simulation or pose interpolation. Scene and historical mesh transforms come
from exact saved samples. Historical poses are isolated render layers composited
with native visibility masks; text and paths are separate PDF/SVG vectors.
"""
from pathlib import Path
import argparse, json, os, sys
import bpy
import numpy as np
from mathutils import Quaternion


HERE=Path(__file__).resolve().parents[1]
SOURCE=None
PROTOCOL_SOURCE=None
SIZE=1024
HISTORY='#2D6B91'
# 2026-11-16: use the Pass fixture's middle sRGB channel (~0.18) for
# neutral work surfaces, including Capture ramps and both protocol frames.
# The large background table and green conveyors retain their recorded colors.
TABLE_COLOR='#2E2E2E'
SURFACE_COLORS={'db0_buzz_fixture_base_visual':TABLE_COLOR,'ramp_visual':TABLE_COLOR,
                **{f'ramp_support_{i}_visual':'#6B6B6B' for i in range(4)}}

def linear(hexcode):
    vals=[int(hexcode[i:i+2],16)/255 for i in (1,3,5)]
    return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals]

def collection(name):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c

def move(obj,c):
    for old in list(obj.users_collection):old.objects.unlink(obj)
    c.objects.link(obj)

def ghost_material(j):
    # Opaque isolated surfaces avoid opacity accumulating through concave meshes.
    m=bpy.data.materials.new(f'History {j+1}');m.use_nodes=True
    surface=m.node_tree.nodes.get('Principled BSDF')
    surface.inputs['Base Color'].default_value=(*linear(HISTORY),1)
    surface.inputs['Roughness'].default_value=.9
    surface.inputs['Specular IOR Level'].default_value=importer.DEFAULTS['specular']
    surface.inputs['Emission Color'].default_value=(*linear(HISTORY),1)
    surface.inputs['Emission Strength'].default_value=.06
    return m

def composite_history(scene, task, groups):
    # All layers use the exact same camera. Masks preserve historical visibility
    # and current foreground occlusion; opacity is applied once per whole pose.
    base=scene.view_layers[0];base.name='Current'
    for group in groups:base.layer_collection.children[group.name].exclude=True
    scene.render.film_transparent=True
    scene.use_nodes=True
    tree=scene.node_tree;tree.nodes.clear()
    previous=tree.nodes.new('CompositorNodeRLayers');previous.layer='Current'
    previous.location=(-700,300)
    count=len(groups)
    for j,group in enumerate(groups):
        layer=scene.view_layers.new(f'History {j+1}')
        for item in layer.layer_collection.children:
            item.exclude=item.name.startswith('Current') or (item.name.startswith('History') and item.name!=group.name)
        render=tree.nodes.new('CompositorNodeRLayers');render.layer=layer.name
        mask=tree.nodes.new('CompositorNodeImage')
        mask.image=bpy.data.images.load(str(HERE/'assets'/task/f'overlay_mask_{j}.png'),check_existing=True)
        mask.image.colorspace_settings.name='Non-Color';mask.image.pack()
        visible=tree.nodes.new('CompositorNodeMath');visible.operation='MULTIPLY'
        tree.links.new(mask.outputs['Image'],visible.inputs[0]);tree.links.new(render.outputs['Alpha'],visible.inputs[1])
        alpha=tree.nodes.new('CompositorNodeMath');alpha.operation='MULTIPLY'
        alpha.inputs[1].default_value=.52 if count==1 else [.32,.52][j]
        tree.links.new(visible.outputs[0],alpha.inputs[0])
        mix=tree.nodes.new('CompositorNodeMixRGB');mix.blend_type='MIX'
        tree.links.new(alpha.outputs[0],mix.inputs[0]);tree.links.new(previous.outputs['Image'],mix.inputs[1]);tree.links.new(render.outputs['Image'],mix.inputs[2])
        render.location=(-700,-j*400);mask.location=(-700,-j*400-160)
        visible.location=(-450,-j*400);alpha.location=(-250,-j*400);mix.location=(j*220,300)
        previous=mix
    output=tree.nodes.new('CompositorNodeComposite');output.location=(500,300)
    tree.links.new(previous.outputs['Image'],output.inputs['Image'])

def build(task,samples,device,protocol=None):
    r=json.loads((HERE/'assets'/task/'panel.json').read_text())
    folder=(PROTOCOL_SOURCE if protocol else SOURCE)/'recordings'/task/'recording/replay'
    meta=json.loads((folder/'scene.json').read_text());a=dict(np.load(folder/'trajectory.npz'));g=dict(np.load(folder/'geometry.npz'))
    out=HERE/'panels'/task
    if protocol:
        example=json.loads(Path(__file__).with_name('protocol_example.json').read_text())
        frame=example['frames'][0 if protocol=='paused' else 1]
        index=int(np.argmin(abs(a['time']-frame['time_s'])))
        assert abs(a['time'][index]-frame['time_s'])<1e-9
        target_id=next(item['id'] for item in meta['geoms'] if item['name']=='target_canonical_visual')
        assert np.max(abs(a['geom_pos'][index,target_id]-frame['body_position_world_m']))<1e-9
        r={**r,'episode_id':example['episode_id'],'frames':[{'sample_index':index,'time_s':frame['time_s']}],
           'camera_position':example['camera_position'],'camera_quaternion_wxyz':example['camera_quaternion_wxyz'],
           'vertical_fov_deg':example['vertical_fov_deg'],'crop_xywh':example['crop_xywh']}
        out=HERE/'protocol'/protocol
    out.mkdir(parents=True,exist_ok=True)
    index=r['frames'][-1]['sample_index'];bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.engine='CYCLES'
    scene.render.resolution_x=scene.render.resolution_y=SIZE;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.use_motion_blur=False;scene.render.threads_mode='FIXED';scene.render.threads=6
    scene.cycles.samples=samples;scene.cycles.seed=42;scene.cycles.use_animated_seed=False
    scene.cycles.use_denoising=True;scene.cycles.denoiser='OPTIX' if device=='OPTIX' else 'OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=device=='OPTIX'
    scene.cycles.transparent_max_bounces=32;scene.render.use_persistent_data=True
    if device!='CPU':
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type=device;prefs.get_devices()
        enabled=[]
        for d in prefs.devices:d.use=d.type==device;enabled.extend([d.name] if d.use else [])
        assert enabled,f'No {device} device';scene.cycles.device='GPU'
    scene.world=bpy.data.worlds.new('Studio world');scene.world.use_nodes=True
    defaults=importer.DEFAULTS
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.68,.72,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=defaults['world_strength']
    scene.view_settings.view_transform='AgX';scene.view_settings.look=defaults['look']
    scene.view_settings.exposure=defaults['exposure'];scene.view_settings.gamma=defaults['gamma']
    current=collection('Current — exact recorded scene');objects={};cache={};notices=[]
    room_walls={'wall_leftcorner_visual','wall_rightcorner_visual','wall_left_visual','wall_right_visual','wall_rear_visual','wall_front_visual'}
    for item in meta['geoms']:
        i=item['id'];name=item['name'] or f'geom_{i}';kind=int(g['geom_type'][i])
        if kind==7:
            mid=int(g['geom_dataid'][i])
            if mid not in cache:cache[mid]=importer.make_mesh(g,mid,notices)
            obj=bpy.data.objects.new(name,cache[mid]);current.objects.link(obj)
        else:obj=importer.primitive(kind,a['geom_size'][index,i]);move(obj,current)
        obj.name=f'geom_{i:04d}__{name}';obj['mujoco_geom_id']=i;obj['mujoco_body']=item['body'];obj['sample_index']=index
        obj.rotation_mode='QUATERNION';obj.location=a['geom_pos'][index,i];obj.rotation_quaternion=a['geom_quat'][index,i];obj.scale=importer.geom_scale(kind,a['geom_size'][index,i])
        m=importer.make_material(name,a['geom_rgba'][index,i],'studio')
        if not ('floor' in name or 'wall_' in name):importer.add_texture(m,g,int(g['geom_matid'][i]),bool(obj.data.uv_layers),notices)
        if (task.startswith('t3') or task.startswith('t4')) and name in SURFACE_COLORS:
            surface=m.node_tree.nodes['Principled BSDF'];base=surface.inputs['Base Color']
            for link in list(base.links):m.node_tree.links.remove(link)
            base.default_value=(*linear(SURFACE_COLORS[name]),1);m.diffuse_color=base.default_value
        obj.data.materials.append(m);obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=m
        obj.hide_render=int(g['geom_group'][i]) not in meta['geom_groups'] or name in room_walls;obj.hide_set(obj.hide_render);objects[i]=obj
    cam=bpy.data.cameras.new('agentview');cam.sensor_fit='VERTICAL';cam.sensor_height=32;cam.lens=32/(2*np.tan(np.deg2rad(r['vertical_fov_deg'])/2));cam.clip_start=.01;cam.clip_end=300
    camera=bpy.data.objects.new('agentview',cam);scene.collection.objects.link(camera);camera.location=r['camera_position'];camera.rotation_mode='QUATERNION';camera.rotation_quaternion=r['camera_quaternion_wxyz'];scene.camera=camera
    importer.add_area('Key softbox',(1,-2,3.3),(-.15,0,.75),defaults['key_energy'],defaults['key_size']);importer.add_area('Fill softbox',(-1.5,-.3,2.2),(-.15,0,.8),defaults['fill_energy'],defaults['fill_size']);importer.add_area('Rim softbox',(.4,2,2.6),(-.15,0,.9),defaults['rim_energy'],defaults['rim_size'])
    target_body='goal_main' if task.startswith('t2') else 'wire_main' if task.startswith('t3') else 'target_main'
    history=[];history_groups=[]
    for j,f in enumerate(r['frames'][:-1]):
        c=collection(f'History {j+1} — t={f["time_s"]:.3f}s');history_groups.append(c);m=ghost_material(j);idx=f['sample_index']
        for item in meta['geoms']:
            i=item['id']
            if item['body']!=target_body or objects[i].hide_render:continue
            if task.startswith('t3') and not item['name'].startswith('wire_segment'):continue
            obj=objects[i].copy();obj.data=objects[i].data.copy();obj.name=f'history_{j}_geom_{i}';c.objects.link(obj)
            obj.location=a['geom_pos'][idx,i];obj.rotation_quaternion=a['geom_quat'][idx,i];obj.scale=importer.geom_scale(int(g['geom_type'][i]),a['geom_size'][idx,i])
            obj.data.materials.clear();obj.data.materials.append(m);obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=m
            obj.visible_shadow=False;obj.visible_glossy=False;obj.visible_diffuse=False;obj['sample_index']=idx;obj['time_s']=f['time_s'];obj['source']='real recorded geom pose, no relocation';history.append((obj,i,idx))
    composite_history(scene,task,history_groups)
    scene['task_id']=task;scene['source_episode']=r['episode_id'];scene['source_policy']='native-oracle';scene['current_time_s']=r['frames'][-1]['time_s'];scene['history_times_s']=[f['time_s'] for f in r['frames'][:-1]]
    scene['annotations']='Sparse recorded historical poses. Vector annotations are in ontimebench.svg.'
    scene.render.filepath=str(out/'history.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    # Read the saved native deliverable, then compare all actual transforms.
    bpy.ops.wm.open_mainfile(filepath=str(out/'scene.blend'));bpy.context.view_layer.update()
    errors=[]
    for obj in bpy.data.objects:
        if 'mujoco_geom_id' not in obj or 'sample_index' not in obj:continue
        # Excluded render layers have no evaluated matrix; all recorded meshes
        # are unparented, so their saved transforms are already world transforms.
        assert obj.parent is None
        i=obj['mujoco_geom_id'];idx=obj['sample_index'];p,q,scale=obj.location,obj.rotation_quaternion,obj.scale
        errors.append([np.max(abs(np.array(p)-a['geom_pos'][idx,i])),np.max(abs(np.array(q.to_matrix())-np.array(Quaternion(a['geom_quat'][idx,i]).to_matrix()))),np.max(abs(np.array(scale)-importer.geom_scale(int(g['geom_type'][i]),a['geom_size'][idx,i])))])
    err=np.max(errors,axis=0);assert np.max(err)<1e-5,err
    materials={}
    for material in bpy.data.materials:
        surface=material.node_tree.nodes.get('Principled BSDF') if material.use_nodes else None
        if surface is None:continue
        specular=float(surface.inputs['Specular IOR Level'].default_value)
        assert abs(specular-defaults['specular'])<1e-7,(material.name,specular)
        materials[material.name]={'specular':specular,'roughness':float(surface.inputs['Roughness'].default_value),
                                  'base_color_linear':list(surface.inputs['Base Color'].default_value)}
    bpy.ops.render.render(write_still=True)
    report={'task_id':task,'episode_id':r['episode_id'],'seed':r['seed'],'camera':'agentview','camera_position':r['camera_position'],'camera_quaternion_wxyz':r['camera_quaternion_wxyz'],'vertical_fov_deg':r['vertical_fov_deg'],'selected_samples':[f['sample_index'] for f in r['frames']],'selected_times_s':[f['time_s'] for f in r['frames']],'source_record':str(HERE/'assets'/task/'panel.json'),'resolution':[SIZE,SIZE],'crop_xywh':r['crop_xywh'],'blender':bpy.app.version_string,'engine':'CYCLES','device':device,'samples':samples,'render_seed':42,'max_saved_position_error_m':float(err[0]),'max_saved_rotation_matrix_error':float(err[1]),'max_saved_scale_error':float(err[2]),'history_mesh_count':len(history),'style_changes':['six decorative room walls hidden','neutral room floor material','three studio area lights','AgX contrast','roughness .34; physical geom sizes and poses unchanged'],'notices':sorted(set(notices))}
    report.update(render_defaults=defaults,materials=materials,table_color_srgb=TABLE_COLOR,source_replay=str(folder),
                  protocol=protocol,shared_renderer=str(Path(importer.__file__).resolve()))
    report['style_changes']=['shared 2026-11-16 studio defaults; global specular 0.10',
                             'neutral table/ramp surfaces; original conveyor green',
                             'physical geom sizes, poses, cameras, masks and lights unchanged']
    (out/'validation.json').write_text(json.dumps(report,indent=2));print('COMPLETE',protocol or task,json.dumps(err.tolist()),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-project',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--tasks',nargs='*',default=[])
    p.add_argument('--protocol',action='store_true')
    p.add_argument('--protocol-source',type=Path)
    p.add_argument('--samples',type=int,default=96)
    p.add_argument('--device',choices=['OPTIX','CUDA','CPU'],default='OPTIX')
    p.add_argument('--research-root',type=Path,default=Path(os.environ.get('SE3WAM_RESEARCH','C:/workspace/se3-wam-research')))
    args=p.parse_args()
    if not args.tasks and not args.protocol:p.error('Select --tasks and/or --protocol')
    if args.protocol and args.protocol_source is None:p.error('--protocol requires --protocol-source (the held-control replay)')
    SOURCE=args.source_project;PROTOCOL_SOURCE=args.protocol_source;HERE=args.output
    sys.path.insert(0,str(args.research_root/'scripts/benchmark_infra/mujoco_blender'))
    import render_blender as importer
    for task in args.tasks:build(task,args.samples,args.device)
    if args.protocol:
        for name in ('paused','advancing'):build('t4_sphere_tabletop',args.samples,args.device,name)
