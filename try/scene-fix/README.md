# scene-fix —— 用"机位"而不是"提示词"重画这张 Hero 背景

原图（ChatGPT 生成）的问题不是风格，是**机位**：桌子的长边斜着、人物是侧背对镜头、
相机在房间中段。改提示词永远改不动，因为朝向是低频构图属性，由初始噪声和结构条件决定。

这里的做法：**自己算机位**。用 9 行代码在 3D 里摆一个方盒房间，按目标相机参数渲一张
"白模 + 深度图"，再把深度图交给 ControlNet 当硬约束。机位从"求模型给"变成"我自己定"。

## 结果

| 文件 | 内容 |
|---|---|
| `hero-library-1672x941.png` | 成品：相机后上方 30° 俯视、桌面横置、人物左侧面、光从左侧窗来 |
| `alt-empty-room-1672x941.png` | 同机位的空景版（纯背景，UI 直接压上去最省事） |
| `before-after.png` | 原图 / 成品对照 |
| `graybox.png` | 结构锚：白模渲染色块图，ControlNet 的输入来源 |

## 机位参数（要改就改这几个数）

`pipeline/render_box.py` 末尾：

```python
cam = Cam((3.62, 2.46, 5.72),   # 相机位置 x, y(高度), z
          0.0,                  # yaw 水平转角，0 = 正对 -z
          -30.0,                # pitch 俯角，负数是俯视
          63.0,                 # hfov 水平视场，约等于 26mm
          1344, 768)            # 渲染分辨率
```

房间尺寸在文件顶部 `RW, RD, RH = 7.0, 4.8, 3.05`（宽 / 深 / 高，单位米）。
桌子、人物、书架的坐标都在 `build_scene()` 里，全是盒子，改数字即可。

## 复现命令

```bash
P=/home/justin/.venvs/imggen/bin/python      # 已装好 torch 2.4.1 + diffusers 0.31 + SDXL

# 1) 渲白模与深度图
$P pipeline/render_box.py                    # → out/box_color.png, out/box_depth.png

# 2) ControlNet-depth 出图（风格由 prompt 决定，机位由深度图锁死）
$P pipeline/gen_cn.py \
   --depth out/box_depth.png --out out/try \
   --prompt-file prompt.txt --seeds 11,22,33 --cn-scale 0.7

# 3) 想换成"图生图 + 深度"就用 gen_cn2img.py（同参数，多 --init/--strength）
```

模型放在 `~/imggen-work/models/`：

- `sd_xl_base_1.0.safetensors`（6.9G）
- ControlNet depth: `xinsir/controlnet-depth-sdxl-1.0`（HF 缓存里，已下好）

HF 直连不通，全部走镜像：`export HF_ENDPOINT=https://hf-mirror.com`。

## 已知的天花板（下次别再撞）

1. **SDXL base 不肯在 ControlNet 锁死的格子里画人。** 深度图上明明是个人形，
   模型一律把她画成一摞书或者一块亮面板。试过 cn-scale 0.42 / 0.55 / 0.62 / 0.7 / 0.8，
   换过 prompt、去掉椅子、把书架挪走、把人放大——都不行。
   → 所以成品里的人物是**单独生成后合成进去的**（GrabCut 抠图 + 羽化 + 0.42 denoise 统一）。
2. **img2img 强度 > 0.85 会丢机位，< 0.6 又上不了色。** 0.62 只是把白模擦亮，
   0.85–0.90 才开始真上色，但同一步相机就滑回平视众数了。这个区间没有解，
   必须靠 ControlNet 而不是靠强度。
3. **要真正一次成图，需要一个"人物强"的底模**（SD1.5 动漫模型 / Illustrious / Pony 系），
   SDXL base 不是画二次元角色的料。CN-depth 的对应版本要另外下一份（~1.45G，SD1.5 尺度）。
4. **UI 不要交给图像模型。** 原图里 `I welieve your this every graceful typography`、
   `Dstber 10, 2023` 全是模型乱码。背景图里出现任何可读字符，这张图就废。

## 下一步（前端那边）

版面元素走真 HTML/CSS：背景图 `hero-library-1672x941.png` 铺满，
文案压在**左侧 40%**，上面盖一层 `linear-gradient(90deg, rgba(20,12,8,.55), transparent)`
做 scrim。判据：白字压在背景最亮处，对比度 ≥ 4.5:1（拿 DevTools 取色算）。
