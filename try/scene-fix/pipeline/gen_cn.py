#!/usr/bin/env python3
# ControlNet-depth 驱动的生成：机位由我自己的白模深度图锁死，风格由 prompt 决定。
import argparse, os
import torch
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel
from PIL import Image, ImageFilter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/home/justin/imggen-work/models/sd_xl_base_1.0.safetensors")
    ap.add_argument("--cn", default="/home/justin/.cache/huggingface/hub/models--xinsir--controlnet-depth-sdxl-1.0/snapshots/961552fa2913e3aa82cdfb32cb51bf182d95207c")
    ap.add_argument("--cn-config", default="/home/justin/imggen-work/models/cn_depth_sdxl_config.json")
    ap.add_argument("--depth", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--seeds", default="11,22,33,44")
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=6.0)
    ap.add_argument("--cn-scale", type=float, default=0.85)
    ap.add_argument("--w", type=int, default=1344)
    ap.add_argument("--h", type=int, default=768)
    a = ap.parse_args()

    txt = open(a.prompt_file).read()
    pos, neg = [x.strip() for x in txt.split("---NEG---")]

    cn = ControlNetModel.from_pretrained(a.cn, torch_dtype=torch.float16)
    pipe = StableDiffusionXLControlNetPipeline.from_single_file(
        a.model, controlnet=cn, torch_dtype=torch.float16, use_safetensors=True)
    pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)

    dep = Image.open(a.depth).convert("L").resize((a.w, a.h), Image.LANCZOS)
    dep = dep.filter(ImageFilter.GaussianBlur(2.0)).convert("RGB")
    os.makedirs(a.out, exist_ok=True)
    for s in [int(x) for x in a.seeds.split(",")]:
        g = torch.Generator("cuda").manual_seed(s)
        img = pipe(prompt=pos, negative_prompt=neg, image=dep,
                   controlnet_conditioning_scale=a.cn_scale,
                   num_inference_steps=a.steps, guidance_scale=a.cfg, generator=g,
                   width=a.w, height=a.h).images[0]
        p = os.path.join(a.out, f"c{s}.png")
        img.save(p)
        print("saved", p, flush=True)

if __name__ == "__main__":
    main()
