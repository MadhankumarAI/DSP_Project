"""
Experiment 9: Text to Image Generation
Load pretrained text-to-image model, provide textual prompt & generate
an image. Experiment with different prompts.
"""
import torch
from diffusers import StableDiffusionPipeline

# Pretrained text-to-image model (lightweight SD-Turbo: 1-step generation, runs on CPU)
pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/sd-turbo", torch_dtype=torch.float32)

PROMPTS = [
    "a futuristic city skyline at sunset, digital art",
    "a watercolor painting of a mountain lake",
    "a cute robot reading a book, cartoon style",
]  # experiment with different prompts

for i, prompt in enumerate(PROMPTS, 1):
    image = pipeline(prompt, num_inference_steps=2, guidance_scale=0.0).images[0]
    out_path = f"generated_image_{i}.png"
    image.save(out_path)
    print(f"Prompt: '{prompt}' -> saved {out_path}")
