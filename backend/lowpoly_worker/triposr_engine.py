import os
import sys
import time
import json
import mimetypes
import uuid
import urllib.request
import urllib.error
import trimesh

# Add VAST-AI-Research/TripoSR folder to path if cloned locally next to backend
triposr_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TripoSR")
if os.path.exists(triposr_path):
    sys.path.append(triposr_path)

def upload_to_tripo(file_path, api_key):
    url = "https://api.tripo3d.ai/v2/openapi/upload/sts"
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode('utf-8') + file_content + f"\r\n--{boundary}--\r\n".encode('utf-8')
    
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    with urllib.request.urlopen(req) as res:
        resp_data = json.loads(res.read().decode('utf-8'))
        return resp_data["data"]["image_token"]

def submit_tripo_task(image_token, api_key):
    url = "https://api.tripo3d.ai/v2/openapi/task"
    payload = {
        "type": "image_to_model",
        "file": {
            "type": "image",
            "file_token": image_token
        }
    }
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req) as res:
        resp_data = json.loads(res.read().decode('utf-8'))
        return resp_data["data"]["task_id"]

def poll_tripo_task(task_id, api_key):
    url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    max_retries = 40
    for _ in range(max_retries):
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {api_key}")
        
        with urllib.request.urlopen(req) as res:
            resp_data = json.loads(res.read().decode('utf-8'))
            status = resp_data["data"]["status"]
            
            if status == "success" or status == "SUCCEEDED":
                output_data = resp_data["data"]["output"]
                return output_data.get("model") or output_data.get("pbr_model") or output_data.get("base_model")
            elif status == "failed" or status == "FAILED":
                raise Exception("Tripo AI task failed")
                
        print("Tripo AI cloud generation processing... waiting 3 seconds")
        time.sleep(3)
    raise TimeoutError("Tripo AI cloud generation timed out")

def download_model(model_url, output_path):
    req = urllib.request.Request(model_url, method="GET")
    with urllib.request.urlopen(req) as res, open(output_path, "wb") as out_file:
        out_file.write(res.read())

def generate_3d_mesh(image_paths: str, output_path: str):
    """
    Generate a low-poly 3D mesh using TripoSR.
    Supports Cloud Tripo3D API if TRIPO_API_KEY environment variable is set.
    """
    print(f"Starting 3D mesh generation for {image_paths}...")
    
    # Load .env file manually inside the worker context
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        val_clean = val.strip().strip("'").strip('"')
                        os.environ[key.strip()] = val_clean
            print(f"Loaded environment variables manually from {env_path}")
        else:
            print(f".env file not found at {env_path}")
    except Exception as e:
        print(f"Failed to manually parse dotenv: {e}")

    # Resolve first image path
    first_image = image_paths.split(",")[0] if "," in image_paths else image_paths
    if not os.path.exists(first_image):
        raise FileNotFoundError(f"Input image not found: {first_image}")

    # Check for Cloud Tripo API Key (Fastest, best quality, zero local resources)
    tripo_api_key = os.environ.get("TRIPO_API_KEY")
    if tripo_api_key:
        print("TRIPO_API_KEY found. Utilizing Tripo3D OpenAPI Cloud Service...")
        try:
            image_token = upload_to_tripo(first_image, tripo_api_key)
            print(f"Uploaded reference image successfully. Token: {image_token}")
            task_id = submit_tripo_task(image_token, tripo_api_key)
            print(f"Submitted task successfully. Task ID: {task_id}")
            model_url = poll_tripo_task(task_id, tripo_api_key)
            print(f"Generation successful. Downloading mesh from {model_url}...")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            download_model(model_url, output_path)
            print(f"Successfully generated and saved cloud mesh to {output_path}")
            return True
        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode('utf-8') if http_err else ""
            print(f"Tripo Cloud API HTTP Error {http_err.code}: {http_err.reason}")
            print(f"Response Body: {error_body}")
            print("Falling back to local generation...")
        except Exception as api_err:
            print(f"Tripo Cloud API failed: {api_err}. Falling back to local generation...")

    # Local PyTorch TripoSR Generation Fallback
    try:
        import torch
        from PIL import Image
        from tsr.system import TSR
        from tsr.utils import remove_background, resize_foreground
    except ImportError:
        print("\n[WARNING] TripoSR ML libraries (torch, PIL, tsr) not fully installed/available.")
        print("[INFO] Set TRIPO_API_KEY in your .env file to generate real models without a local GPU!")
        print("Falling back to generating a low-poly proxy shape...")
        mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mesh.export(output_path)
        print(f"Fallback mesh exported to {output_path}")
        return True

    # Real TripoSR execution
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    weights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "weights", "model.ckpt")
    
    try:
        if not os.path.exists(weights_path):
            print("Local weights model.ckpt not found in backend/weights/. Loading from Hugging Face...")
            model = TSR.from_pretrained(
                "stabilityai/TripoSR", 
                config_name="config.yaml", 
                weight_name="model.ckpt"
            )
        else:
            print(f"Loading local weights from {weights_path}...")
            model = TSR.from_pretrained(
                "stabilityai/TripoSR", 
                config_name="config.yaml", 
                checkpoint_path=weights_path
            )
            
        model.to(device)
        model.renderer.set_chunk_size(8192)
        
        image = Image.open(first_image)
        image = remove_background(image)
        image = resize_foreground(image, 0.9)
        
        with torch.no_grad():
            scene_codes = model([image], device=device)
            meshes = model.extract_mesh(scene_codes)
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        meshes[0].export(output_path)
        print(f"Successfully generated low-poly 3D mesh at {output_path}")
        return True
        
    except Exception as e:
        print(f"Error during local TripoSR execution: {e}. Falling back to low-poly proxy shape...")
        mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mesh.export(output_path)
        return True
