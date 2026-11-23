#!/usr/bin/env python3
# 用白模做结构锚，跑 SDXL img2img。阶段1 定结构(denoise 高)，阶段2 加细节(denoise 低)。
import argparse, os, glob
import torch
from diffusers import StableDiffusionXLImg2ImgPipeline
from PIL import Image

POS = ("cozy private library, warm afternoon sun through a tall window, god rays and dust motes, "
       "young scholar in a beige cardigan at a wooden desk, left-side profile facing frame left, "
       "writing in an open book, tall bookshelf wall of old books behind, potted plants, patterned rug, "
       "painterly anime background art, muted warm brown palette, soft cinematic light, no text")

NEG = ("text, letters, words, watermark, signature, logo, ui, screenshot, frame, border, "
       "blurry, lowres, jpeg artifacts, oversaturated, harsh contrast, hdr, fisheye, distorted perspective, "
       "extra limbs, extra arms, malformed hands, deformed face, ugly, cartoon outline, flat shading, "
       "front view of the person, person looking at the camera, back view of the person")

def load(path):
    pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
        path, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)
    return pipe

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/home/justin/imggen-work/models/sd_xl_base_1.0.safetensors")
    ap.add_argument("--init", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--strength", type=float, default=0.62)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=6.0)
    ap.add_argument("--seeds", default="11,22,33,44")
    ap.add_argument("--w", type=int, default=1344)
    ap.add_argument("--h", type=int, default=768)
    ap.add_argument("--prompt-file", default="")
    a = ap.parse_args()

    pos, neg = POS, NEG
    if a.prompt_file and os.path.exists(a.prompt_file):
        txt = open(a.prompt_file).read()
        pos, neg = [x.strip() for x in txt.split("---NEG---")]

    pipe = load(a.model)
    init = Image.open(a.init).convert("RGB").resize((a.w, a.h), Image.LANCZOS)
    os.makedirs(a.out, exist_ok=True)
    for s in [int(x) for x in a.seeds.split(",")]:
        g = torch.Generator("cuda").manual_seed(s)
        img = pipe(prompt=pos, negative_prompt=neg, image=init, strength=a.strength,
                   num_inference_steps=a.steps, guidance_scale=a.cfg, generator=g).images[0]
        p = os.path.join(a.out, f"s{s}.png")
        img.save(p)
        print("saved", p, flush=True)

if __name__ == "__main__":
    main()
