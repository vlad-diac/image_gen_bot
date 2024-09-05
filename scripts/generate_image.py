import sys
import os
import importlib
import PIL
from datetime import datetime
import random
import uuid

import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file as load_safetensors
from comfy import model_management
from comfy.sd import load_state_dict_guess_config, VAE
from nodes import CLIPTextEncode, VAEDecode, KSampler

class ImageGenerator:
    def __init__(self):
        self.device = model_management.get_torch_device()
        model_management.load_models_gpu([])

        custom_nodes = importlib.import_module("custom_nodes.ComfyUI-GGUF.nodes")
        self.DualCLIPLoaderGGUF = custom_nodes.DualCLIPLoaderGGUF
        self.UnetLoaderGGUF = custom_nodes.UnetLoaderGGUF

        self.unet_loader = self.UnetLoaderGGUF()
        self.unet = self.unet_loader.load_unet("flux1-dev-Q4_0.gguf")[0]

        self.clip_loader = self.DualCLIPLoaderGGUF()
        self.clip = self.clip_loader.load_clip(clip_name1="clip_l.safetensors", clip_name2="t5xxl_fp16.safetensors", type="flux")[0]

        vae_state_dict = load_safetensors("models/vae/ae.safetensors")
        self.vae = VAE(sd=vae_state_dict)

        self.clip_text_encode = CLIPTextEncode()
        self.negative_prompt = self.clip_text_encode.encode(self.clip, "ugly, blurry")[0]

    def tensor_to_image(self, tensor):
        tensor = tensor.detach().cpu()
        tensor = tensor * 255
        tensor = np.array(tensor, dtype=np.uint8)
        if np.ndim(tensor) > 3:
            assert tensor.shape[0] == 1
            tensor = tensor[0]
        return PIL.Image.fromarray(tensor)

    def generate_image(self, prompt, cfg, steps, seed, width=512, height=768):
        positive_prompt = self.clip_text_encode.encode(self.clip, prompt)[0]

        latent_image = torch.zeros((1, 4, height // 8, width // 8), device=self.device)
        latent_image_dict = {"samples": latent_image}

        sampler = KSampler()
        latent = sampler.sample(
            model=self.unet,
            seed=seed,
            steps=steps,
            cfg=cfg,
            sampler_name="euler",
            scheduler="simple",
            positive=positive_prompt,
            negative=self.negative_prompt,
            latent_image=latent_image_dict,
            denoise=1.0
        )[0]

        vae_decode = VAEDecode()
        image = vae_decode.decode(self.vae, latent)[0]
        image = self.tensor_to_image(image)

        filename = f"output/generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        image.save(filename)
        
        output = {
            "id": str(uuid.uuid4()),
            "image": image,
            "filename": filename
        }
        print(f"Image generated and saved as '{filename}'")
        return output