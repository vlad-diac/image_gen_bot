# ComfyUI + Market Bot Installation Guide 

This guide will walk you through the process of setting up ComfyUI on a RunPod instance with a 3090 GPU.

## 1. Deploy a RunPod Instance

1. Go to RunPod.io and log in to your account.
2. Click on "Deploy" to create a new pod.
3. Select the following configuration:
   - GPU: NVIDIA RTX 3090
   - Container Image: `runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04`
   - Container Disk: Set to at least 150GB
   - Volume Disk: Set to at least 150GB
4. Under "Exposed Ports", add a the following HTTP ports: 7860, 8188
5. Add the OpenAI API key as an environment variable:
    - Click on "Environment"
    - Add a new variable: `OPENAI_API_KEY`
    - Set the value to your OpenAI API key
6. Click "Deploy" to create your pod.

## 2. Access the Jupyter Instance

1. Once your pod is deployed, click on the "Connect" button.
2. Select "Connect to Jupyter Lab" (usually on port 8888).
3. You'll be directed to a Jupyter Lab interface in your browser.

## 3. Installation Process

1. In Jupyter Lab, open a new terminal.
2. Clone this repository:
   ```
   git clone https://github.com/vlad-diac/image_gen_bot.git
   cd image_gen_bot
   ```
3. Make the installation script executable:
   ```
   chmod +x install_runpod.sh
   ```
4. Run the installation script:
   ```
   ./install_runpod.sh
   ```
   This script will:
   - Update system packages
   - Install required dependencies
   - Clone ComfyUI and necessary custom nodes
   - Set up a Python virtual environment
   - Install PyTorch and other required packages
   - Download necessary models

## 4. Launch ComfyUI

After the installation is complete, you can start ComfyUI:

1. Navigate to the ComfyUI directory:
   ```
   cd /workspace/ComfyUI
   ```
2. Run the launch script:
   ```
   ./launch.sh
   ```
3. Accessing ComfyUI
    ComfyUI will be running on port 8188. To access it:

        1. Go back to your RunPod dashboard.
        2. Find the pod you deployed and click on "Connect".
        3. Under "HTTP Service", you should see a link for port 8188. Click on it to open ComfyUI in your browser.
## 5. Launching Market Bot
1. Navigate to the Market Bot directory:
   ```
   cd /workspace/ComfyUI/
   ```
2. Edit the .env.example file with your API keys and save it as .env
3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```
4. Run the Market Bot:
   ```
   python bot_ui.py
   ```

5. Access the Market Bot:
    Go back to your RunPod dashboard.
    Find the pod you deployed and click on "Connect".
    Under "HTTP Service", you should see a link for port 7860. Click on it to open the Market Bot in your browser.

## Troubleshooting

If you encounter any issues during the installation or while running ComfyUI, please check the following:

- Ensure all required ports (7860, 8888, 8188) are properly exposed and not blocked by any firewalls.
- Check the installation logs for any error messages.
- Make sure you have sufficient disk space on both the container and volume disks.
- Ensure your API keys are set correctly as environment variables in the RunPod dashboard. You can edit the pod and check/add the keys in the "Environment" tab.

For further assistance, please open an issue in this repository or consult the ComfyUI documentation.

## Features

1. **ComfyUI Integration**: A powerful and customizable UI for Stable Diffusion, allowing for advanced image generation workflows.

2. **Market Bot**: An AI-powered chatbot specifically designed for marketing tasks, capable of generating marketing campaign timelines and content ideas.

3. **Image Generation**: Utilizes the FLUX model to generate high-quality images based on text prompts, integrated seamlessly with the Market Bot.

4. **Real-time Speech Recognition**: Incorporates the Whisper model(huggingface) for automatic speech recognition, allowing users to interact with the bot using voice input.

5. **Custom Nodes**: Includes several custom nodes for ComfyUI, enhancing its capabilities and allowing for more complex image generation workflows.

6. **Automated Installation**: Includes a comprehensive installation script that sets up the entire environment, including ComfyUI, custom nodes, and required models.
