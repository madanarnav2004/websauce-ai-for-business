"""Run inside Blender. A flat source-faithful image plane, not a product reconstruction."""
import argparse
import sys
from pathlib import Path
import bpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not args.image.is_file(): raise ValueError('Approved cutout not found')
    if args.output.exists(): raise ValueError('Use a new output path; do not overwrite approved work')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1080; scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 25 if args.preview else 100
    scene.render.fps = 24; scene.frame_start = 1; scene.frame_end = 240
    scene.render.image_settings.file_format = 'PNG'
    scene.world.color = (0.7, 0.66, 0.59)
    scene.view_settings.view_transform = 'Standard'
    image = bpy.data.images.load(str(args.image.resolve()))
    if image.channels != 4: raise ValueError('Provide an approved transparent RGBA cutout')
    # Require actual transparency, not merely a four-channel opaque file.
    alpha = list(image.pixels)[3::4]
    if min(alpha) > 0.1 or max(alpha) < 0.9: raise ValueError('Cutout needs transparent background and opaque product pixels')
    image.pack()
    ratio = image.size[0] / image.size[1]
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
    plane = bpy.context.object; plane.name = 'Approved photographic product — flat plane'
    plane.scale = (ratio, 1, 1)
    mat = bpy.data.materials.new('Source photo with alpha'); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    tex = nodes.new('ShaderNodeTexImage'); tex.image = image
    emission = nodes.new('ShaderNodeEmission')
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader'); out = nodes.new('ShaderNodeOutputMaterial')
    links = mat.node_tree.links
    links.new(tex.outputs['Color'], emission.inputs['Color'])
    links.new(tex.outputs['Alpha'], mix.inputs[0])
    links.new(transparent.outputs[0], mix.inputs[1]); links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs[0]); plane.data.materials.append(mat)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.1))
    background = bpy.context.object; background.name = 'Warm neutral backdrop'
    bg = bpy.data.materials.new('Warm plaster'); bg.use_nodes = True
    shader = bg.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (0.78, 0.72, 0.63, 1)
    shader.inputs['Roughness'].default_value = 1
    background.data.materials.append(bg)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    bpy.context.object.data.energy = 400; bpy.context.object.data.shape = 'DISK'; bpy.context.object.data.size = 8
    bpy.ops.object.camera_add(location=(0, 0, 6))
    camera = bpy.context.object; camera.name = 'Front-facing photographic reveal'; scene.camera = camera
    camera.data.type = 'ORTHO'
    full = max(2.3, 2 * ratio / (1080 / 1920) * 1.12)
    for frame, scale in [(1, full * 0.94), (180, full), (240, full)]:
        camera.data.ortho_scale = scale
        camera.data.keyframe_insert(data_path='ortho_scale', frame=frame)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames = args.output.parent / (args.output.stem + '-frames'); frames.mkdir(exist_ok=True)
    scene.render.filepath = str(frames.resolve()) + '/'
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()))
    if args.preview:
        for frame in (1, 120, 240):
            scene.frame_set(frame); scene.render.filepath = str(frames.resolve() / f'{frame:04d}.png')
            bpy.ops.render.render(write_still=True)
    elif args.render:
        bpy.ops.render.render(animation=True)


if __name__ == '__main__': main()
