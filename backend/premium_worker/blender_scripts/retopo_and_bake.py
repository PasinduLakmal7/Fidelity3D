import sys
import os
import bpy

def retopo_and_bake(input_path, output_path):
    print(f"Blender process started: {input_path} -> {output_path}")
    
    # 1. Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 2. Import the low-poly model
    if input_path.endswith('.obj'):
        bpy.ops.import_scene.obj(filepath=input_path)
    elif input_path.endswith('.glb') or input_path.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=input_path)
    else:
        # Try importing as OBJ first
        try:
            bpy.ops.import_scene.obj(filepath=input_path)
        except Exception:
            bpy.ops.import_scene.gltf(filepath=input_path)
            
    # 3. Select the imported mesh
    imported_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not imported_objs:
        print("No mesh imported!")
        return
        
    mesh_obj = imported_objs[0]
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)
    
    # 4. Perform geometry cleaning & smoothing
    print("Blender: Cleaning and smoothing mesh...")
    
    # Add Subsurf modifier for high-res mesh refinement
    subsurf = mesh_obj.modifiers.new(name="Subdivision", type="SUBSURF")
    subsurf.levels = 1
    subsurf.render_levels = 2
    
    # Add Laplacian Smooth modifier
    smooth = mesh_obj.modifiers.new(name="Smooth", type="SMOOTH")
    smooth.factor = 0.5
    smooth.iterations = 8
    
    # Apply modifiers
    for modifier in mesh_obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        
    # 5. Smart UV Project
    print("Blender: Creating Smart UV projections...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 6. Export high-quality model
    print(f"Blender: Exporting refined model to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if output_path.endswith('.obj'):
        bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    elif output_path.endswith('.glb') or output_path.endswith('.gltf'):
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
    else:
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
        
    print("Blender: Processing complete!")

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        if len(args) >= 2:
            retopo_and_bake(args[0], args[1])
        else:
            print("Error: Missing args. Usage: blender -b -P script.py -- <in> <out>")
    else:
        print("Error: Pass arguments after '--'")
