import os
import sys
import subprocess
import trimesh

def load_mesh_safely(input_model: str):
    file_type = None
    try:
        if os.path.exists(input_model):
            with open(input_model, "rb") as f:
                magic = f.read(4)
                if magic == b"glTF":
                    file_type = "glb"
    except Exception:
        pass
    print(f"Loading mesh {input_model} with format: {file_type or 'auto'}")
    return trimesh.load(input_model, file_type=file_type)

def apply_animation(input_model: str, output_model: str, is_premium: bool):
    """
    Applies bone structure/rigging.
    - Premium: Runs headless Blender to perform auto-rigging on a skeleton template.
    - Free: Converts static low-poly OBJ to static GLB directly.
    """
    quality = "High-Quality" if is_premium else "Low-Poly"
    print(f"Applying Rig/Formatting to {quality} model: {input_model} -> {output_model}")
    
    if not os.path.exists(input_model):
        raise FileNotFoundError(f"Input model not found: {input_model}")
        
    if not is_premium:
        # Free Tier: Static export (Convert OBJ to GLB via trimesh)
        print("Free tier: Exporting static model...")
        try:
            mesh = load_mesh_safely(input_model)
            os.makedirs(os.path.dirname(output_model), exist_ok=True)
            mesh.export(output_model)
            print(f"Static low-poly model exported successfully to {output_model}")
            return True
        except Exception as e:
            print(f"Failed to export static mesh: {e}")
            return False
            
    # Premium Tier: Headless Blender Auto-Rigging
    print("Premium tier: Running headless Blender auto-rigging...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "blender_rig.py")
    
    blender_execs = [
        "blender",
        "/usr/bin/blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe"
    ]
    
    blender_path = "blender"
    for path in blender_execs:
        if os.path.isabs(path) and os.path.exists(path):
            blender_path = path
            break
        elif not os.path.isabs(path):
            check_cmd = "where" if os.name == "nt" else "which"
            if subprocess.call([check_cmd, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                blender_path = path
                break
                
    cmd = [blender_path, "-b", "-P", script_path, "--", input_model, output_model]
    
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Blender Rigging stdout:")
        print(process.stdout)
        print(f"Saved Rigged Premium GLB to {output_model}")
        return True
    except Exception as e:
        print(f"Blender auto-rigging failed: {e}. Falling back to static GLB conversion...")
        try:
            mesh = load_mesh_safely(input_model)
            os.makedirs(os.path.dirname(output_model), exist_ok=True)
            mesh.export(output_model)
            print(f"Static fallback model exported to {output_model}")
            return True
        except Exception as fallback_err:
            print(f"Fallback export failed: {fallback_err}")
            return False
