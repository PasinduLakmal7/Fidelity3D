import sys
import os
import bpy

def auto_rig(mesh_path, output_path):
    print(f"Blender Auto-Rigging starting for: {mesh_path}")
    
    # 1. Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 2. Import high-poly mesh
    if mesh_path.endswith('.obj'):
        bpy.ops.import_scene.obj(filepath=mesh_path)
    else:
        bpy.ops.import_scene.gltf(filepath=mesh_path)
        
    mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not mesh_objs:
        print("No mesh found to rig!")
        return
        
    mesh_obj = mesh_objs[0]
    
    # 3. Create a basic skeletal armature (single spine, shoulder, arm skeleton)
    print("Blender: Creating armature...")
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    arm_obj = bpy.context.view_layer.objects.active
    
    # Rename default bone and add joints
    bpy.ops.object.mode_set(mode='EDIT')
    armature_data = arm_obj.data
    root_bone = armature_data.edit_bones[0]
    root_bone.name = "Root"
    root_bone.head = (0, 0, 0)
    root_bone.tail = (0, 0, 0.5)
    
    # Spine bone
    spine_bone = armature_data.edit_bones.new("Spine")
    spine_bone.head = (0, 0, 0.5)
    spine_bone.tail = (0, 0, 1.2)
    spine_bone.parent = root_bone
    
    # Neck/Head bone
    head_bone = armature_data.edit_bones.new("Head")
    head_bone.head = (0, 0, 1.2)
    head_bone.tail = (0, 0, 1.7)
    head_bone.parent = spine_bone
    
    # Left Arm
    l_arm = armature_data.edit_bones.new("Arm.L")
    l_arm.head = (0, 0.2, 1.1)
    l_arm.tail = (0, 0.6, 1.1)
    l_arm.parent = spine_bone
    
    # Right Arm
    r_arm = armature_data.edit_bones.new("Arm.R")
    r_arm.head = (0, -0.2, 1.1)
    r_arm.tail = (0, -0.6, 1.1)
    r_arm.parent = spine_bone
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 4. Bind/Parent the mesh to the Armature with automatic weights
    print("Blender: Parent mesh to armature with auto-weighting...")
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    # Select mesh first, then armature
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        print("Successfully bound armature with auto-weights!")
    except Exception as parent_err:
        print(f"Armature parenting failed: {parent_err}. Using generic armature parent.")
        bpy.ops.object.parent_set(type='ARMATURE')
        
    # 5. Export rigged model to GLB
    print(f"Blender: Exporting rigged GLB to {output_path}...")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    
    bpy.ops.export_scene.gltf(
        filepath=output_path, 
        export_format='GLB',
        use_selection=True,
        export_animations=True
    )
    print("Blender Auto-Rigging process finished!")

if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        if len(args) >= 2:
            auto_rig(args[0], args[1])
        else:
            print("Usage: blender -b -P script.py -- <mesh_path> <output_path>")
