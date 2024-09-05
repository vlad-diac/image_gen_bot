#!/bin/bash

# Install ComfyUI

# Update system packages
apt update
apt upgrade -y

# Install required system dependencies
apt install -y git python3 python3-venv python3-pip
cd /workspace
# Clone the ComfyUI repository
git clone https://github.com/comfyanonymous/ComfyUI.git

# Navigate to the ComfyUI directory
cd /workspace/ComfyUI

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install PyTorch (adjust the CUDA version if needed)
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt

# Create a launch script
echo '#!/bin/bash
source venv/bin/activate
python3 main.py --port 8188 --listen 0.0.0.0 "$@" ' > launch.sh

# Make the launch script executable
chmod +x launch.sh
cd /workspace/ComfyUI/custom_nodes
# Clone the ComfyUI-GGUF repository
git clone https://github.com/city96/ComfyUI-GGUF
git clone https://github.com/XLabs-AI/x-flux-comfyui.git
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/jags111/efficiency-nodes-comfyui
git clone https://github.com/WASasquatch/was-node-suite-comfyui
git clone https://github.com/twri/sdxl_prompt_styler
git clone https://github.com/hylarucoder/ComfyUI-Eagle-PNGInfo
git clone https://github.com/rgthree/rgthree-comfy


cd /workspace/ComfyUI/custom_nodes/x-flux-comfyui

python3 setup.py 
# Install gguf
pip install --upgrade gguf accelerate xformers
pip install -r /workspace/ComfyUI/custom_nodes/ComfyUI-GGUF/requirements.txt
pip install -r /workspace/image_gen_bot/requirements.txt
echo "ComfyUI installation complete. You can start it by running ./launch.sh in the ComfyUI directory."

cd /workspace/ComfyUI/models/unet
wget --content-disposition https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_0.gguf?download=true

cd /workspace/ComfyUI/models/vae
wget --content-disposition https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors

cd /workspace/ComfyUI/models/clip
wget --content-disposition https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors
wget --content-disposition https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors
wget --content-disposition https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors

#move all files from scripts/ to /workspace/ComfyUi
mv /workspace/image_gen_bot/scripts/* /workspace/ComfyUI/




