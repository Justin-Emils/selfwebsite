#!/usr/bin/env python3
# 白模渲染器 v2：把指定的"机位"渲成色块图 + 深度图，作为 img2img / ControlNet 的结构锚。
# 纯 numpy + PIL。相机放在房间外（切面模型），避免近平面裁剪炸掉。
import math
import numpy as np
from PIL import Image, ImageDraw

# ---------------- 相机 ----------------
class Cam:
    def __init__(self, pos, yaw_deg, pitch_deg, hfov_deg, W, H):
        self.pos = np.array(pos, float)
        self.yaw = math.radians(yaw_deg)
        self.pitch = math.radians(pitch_deg)
        self.hfov = math.radians(hfov_deg)
        self.W, self.H = W, H
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        self.fwd = np.array([sy * cp, sp, -cy * cp])
        self.fwd /= np.linalg.norm(self.fwd)
        self.right = np.array([cy, 0.0, sy])
        self.up = np.cross(self.right, self.fwd)
        self.f = (W / 2) / math.tan(self.hfov / 2)
        self.cx, self.cy = W / 2, H / 2

    def to_cam(self, pts):
        d = np.atleast_2d(np.asarray(pts, float)) - self.pos
        return np.stack([d @ self.right, d @ self.up, d @ self.fwd], 1)

# ---------------- 几何 ----------------
def subdiv(v, n):
    v = np.asarray(v, float)
    lu = lambda a, b, t: a + (b - a) * t
    out = []
    for i in range(n):
        for j in range(n):
            u0, u1, w0, w1 = i / n, (i + 1) / n, j / n, (j + 1) / n
            p00 = lu(lu(v[0], v[1], u0), lu(v[3], v[2], u0), w0)
            p10 = lu(lu(v[0], v[1], u1), lu(v[3], v[2], u1), w0)
            p11 = lu(lu(v[0], v[1], u1), lu(v[3], v[2], u1), w1)
            p01 = lu(lu(v[0], v[1], u0), lu(v[3], v[2], u0), w1)
            out.append(np.array([p00, p10, p11, p01]))
    return out

def quad(v, color, layer, n=None, tiles=1, skip=None):
    v = np.asarray(v, float)
    if n is None:
        n = np.cross(v[1] - v[0], v[3] - v[0])
        n = n / (np.linalg.norm(n) + 1e-9)
    out = []
    for p in subdiv(v, tiles):
        c = p.mean(0)
        if skip is not None and skip(c):
            continue
        out.append((p, n, color, layer))
    return out

def box(center, size, color, layer, yaw=0.0):
    cx, cy, cz = center
    sx, sy, sz = size
    c, s = math.cos(yaw), math.sin(yaw)
    rot = lambda p: np.array([p[0] * c - p[2] * s, p[1], p[0] * s + p[2] * c])
    local = np.array([
        [-sx/2, -sy/2, -sz/2], [sx/2, -sy/2, -sz/2], [sx/2, -sy/2, sz/2], [-sx/2, -sy/2, sz/2],
        [-sx/2,  sy/2, -sz/2], [sx/2,  sy/2, -sz/2], [sx/2,  sy/2, sz/2], [-sx/2, sy/2, sz/2],
    ])
    V = np.array([rot(p) + np.array([cx, cy, cz]) for p in local])
    out = []
    for idx, flip in [((0,1,2,3), (0,-1,0)), ((4,5,6,7), (0,1,0)), ((0,1,5,4), (0,0,-1)),
                      ((1,2,6,5), (1,0,0)), ((2,3,7,6), (0,0,1)), ((3,0,4,7), (-1,0,0))]:
        v = V[list(idx)]
        n = np.array(flip, float)
        n = np.array([n[0]*c - n[2]*s, n[1], n[0]*s + n[2]*c])
        out.append((v, n, color, layer))
    return out

# ---------------- 渲染（真 z-buffer） ----------------
LIGHT = np.array([0.62, 0.58, 0.52])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

def shade(color, n):
    k = 0.58 + 0.52 * max(0.0, float(np.dot(n, LIGHT)))
    return np.array([min(255, c * k) for c in color], np.float32)

def render(faces, cam, ss=3, zmin=3.05, zmax=6.9):
    W, H = cam.W * ss, cam.H * ss
    f = cam.f * ss
    cx, cy = cam.cx * ss, cam.cy * ss
    colbuf = np.zeros((H, W, 3), np.float32) + np.array([24, 20, 24], np.float32)
    zbuf = np.full((H, W), np.inf, np.float32)
    bg_shade = np.array([24, 20, 24], np.float32)

    for v, n, color, layer in faces:
        if float(np.dot(n, v.mean(0) - cam.pos)) > 0:
            continue          # 背面剔除
        pc = cam.to_cam(v)
        if np.any(pc[:, 2] < 0.2):
            continue          # 相机在房间外，理论不会发生
        sx = cx + f * pc[:, 0] / pc[:, 2]
        sy = cy - f * pc[:, 1] / pc[:, 2]
        iz = 1.0 / pc[:, 2]
        c = shade(color, n)
        for tri in [(0, 1, 2), (0, 2, 3)]:
            X = np.array([sx[i] for i in tri]); Y = np.array([sy[i] for i in tri])
            IZ = np.array([iz[i] for i in tri])
            x0, x1 = int(max(0, np.floor(X.min()))), int(min(W - 1, np.ceil(X.max())))
            y0, y1 = int(max(0, np.floor(Y.min()))), int(min(H - 1, np.ceil(Y.max())))
            if x1 <= x0 or y1 <= y0:
                continue
            den = (Y[1] - Y[2]) * (X[0] - X[2]) + (X[2] - X[1]) * (Y[0] - Y[2])
            if abs(den) < 1e-9:
                continue
            gx = np.arange(x0, x1 + 1) + 0.5
            gy = np.arange(y0, y1 + 1) + 0.5
            GX, GY = np.meshgrid(gx, gy)
            w0 = ((Y[1] - Y[2]) * (GX - X[2]) + (X[2] - X[1]) * (GY - Y[2])) / den
            w1 = ((Y[2] - Y[0]) * (GX - X[2]) + (X[0] - X[2]) * (GY - Y[2])) / den
            w2 = 1.0 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            izb = np.clip(w0 * IZ[0] + w1 * IZ[1] + w2 * IZ[2], 1e-6, None)
            zb = 1.0 / izb
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            upd = inside & (zb < sub)
            if not upd.any():
                continue
            sub[upd] = zb[upd]
            colbuf[y0:y1 + 1, x0:x1 + 1][upd] = c

    z = zbuf.copy()
    z[~np.isfinite(z)] = zmax
    dep = np.clip((zmax - z) / (zmax - zmin), 0, 1) * 255.0
    img = Image.fromarray(colbuf.astype(np.uint8)).resize((cam.W, cam.H), Image.LANCZOS)
    dimg = Image.fromarray(dep.astype(np.uint8)).resize((cam.W, cam.H), Image.LANCZOS)
    return img, dimg

# ---------------- 场景 ----------------
RW, RD, RH = 7.0, 4.8, 3.05

def build_scene():
    F = []
    FLOOR = (176, 142, 106)
    WALL  = (216, 200, 180)
    DESK  = (128, 84, 52)
    DARK  = (62, 44, 34)
    RUG   = (128, 96, 92)
    PAPER = (242, 236, 222)
    GREEN = (74, 106, 62)
    SKIN  = (216, 186, 162)
    CLOTH = (104, 86, 68)
    RUG_X0, RUG_X1, RUG_Z0, RUG_Z1 = 1.2, 5.2, 0.9, 4.2

    # 地面（地毯区域挖空，避免 z-fighting）
    in_rug = None
    F += quad([(0,0,0),(RW,0,0),(RW,0,RD),(0,0,RD)], FLOOR, 0, np.array([0,1.,0]), tiles=28, skip=in_rug)
    F += quad([(RUG_X0,0.02,RUG_Z0),(RUG_X1,0.02,RUG_Z0),(RUG_X1,0.02,RUG_Z1),(RUG_X0,0.02,RUG_Z1)],
              RUG, 2, np.array([0,1.,0]), tiles=1)
    # 墙面
    F += quad([(0,0,0),(RW,0,0),(RW,RH,0),(0,RH,0)], WALL, 1, np.array([0,0,1.]), tiles=16)      # 后墙
    F += quad([(0,0,0),(0,0,RD),(0,RH,RD),(0,RH,0)], WALL, 1, np.array([1.,0,0]), tiles=14)      # 左墙
    F += quad([(RW,0,0),(RW,0,RD),(RW,RH,RD),(RW,RH,0)], WALL, 1, np.array([-1.,0,0]), tiles=14) # 右墙
    F += quad([(0,RH,0),(RW,RH,0),(RW,RH,RD),(0,RH,RD)], (238,232,224), 1, np.array([0,-1.,0]), tiles=16)  # 天花

    # 后墙左侧：大窗 + 窗台 + 竖框
    F += box((1.80, 1.85, 0.05), (2.55, 1.95, 0.10), (255, 249, 226), 2)
    F += box((1.80, 0.84, 0.12), (2.75, 0.10, 0.20), (240, 234, 222), 3)
    F += box((0.50, 1.85, 0.10), (0.10, 2.05, 0.20), (236, 230, 218), 3)
    F += box((3.10, 1.85, 0.10), (0.10, 2.05, 0.20), (236, 230, 218), 3)
    F += box((1.80, 1.85, 0.14), (0.06, 1.95, 0.14), (238, 232, 220), 3)
    F += box((1.80, 2.36, 0.14), (2.55, 0.06, 0.14), (238, 232, 220), 3)

    # 后墙右侧：书架
    F += box((6.00, 1.32, 0.22), (1.80, 2.64, 0.44), (94, 66, 44), 3)
    for i, y in enumerate(np.arange(0.34, 2.45, 0.36)):
        F += box((6.00, float(y), 0.46), (1.65, 0.09, 0.06), (124, 90, 60), 4)
        col = [(150,72,62),(72,98,124),(144,124,74),(92,112,82),(162,142,112)][i % 5]
        F += box((6.00, float(y)+0.22, 0.46), (1.50, 0.30, 0.05), col, 4)

    # 写字桌（长轴沿 X）
    DX, DZ = 3.10, 2.75
    F += box((DX, 0.76, DZ), (2.10, 0.07, 0.88), DESK, 5)
    for dx in (-0.94, 0.94):
        for dz in (-0.37, 0.37):
            F += box((DX+dx, 0.36, DZ+dz), (0.08, 0.72, 0.08), DARK, 5)
    F += box((DX-0.62, 0.85, DZ+0.02), (0.42, 0.10, 0.46), PAPER, 6)     # 摊开的书
    F += box((DX-0.62, 0.92, DZ-0.21), (0.38, 0.06, 0.18), PAPER, 6)
    F += box((DX-0.05, 0.86, DZ-0.13), (0.09, 0.15, 0.09), (240,238,232), 6)
    F += box((DX-0.95, 0.93, DZ+0.09), (0.12, 0.32, 0.12), (152,122,62), 6)
    F += box((DX-0.86, 1.08, DZ-0.07), (0.32, 0.13, 0.21), (198,160,92), 6)
    F += box((DX+0.62, 0.87, DZ+0.17), (0.34, 0.16, 0.26), (150,72,62), 6)
    F += box((DX+0.30, 0.84, DZ+0.23), (0.28, 0.10, 0.20), (72,98,124), 6)

    # 人物：坐在桌子右端，面朝画面左（-x）→ 左侧面朝相机。用多个盒子拼出坐姿剪影
    px, pz = DX + 1.02, DZ + 0.02
    C1, C2 = CLOTH, (92, 76, 60)
    F += box((px+0.02, 0.48, pz), (0.34, 0.20, 0.34), (58, 54, 56), 7)      # 髋
    F += box((px-0.24, 0.50, pz), (0.34, 0.15, 0.28), C2, 7)                # 大腿
    F += box((px-0.42, 0.27, pz), (0.15, 0.44, 0.15), (56, 52, 54), 7)      # 小腿
    F += box((px-0.44, 0.06, pz), (0.20, 0.08, 0.13), (44, 40, 40), 7)      # 脚
    F += box((px+0.02, 0.70, pz), (0.28, 0.24, 0.32), C1, 7)                # 下躯干
    F += box((px-0.01, 0.96, pz), (0.28, 0.28, 0.36), C1, 7)                # 胸
    F += box((px-0.02, 1.13, pz), (0.26, 0.09, 0.40), C1, 7)                # 肩
    F += box((px-0.04, 1.21, pz), (0.12, 0.08, 0.12), SKIN, 7)              # 颈
    F += box((px-0.07, 1.35, pz), (0.21, 0.22, 0.21), SKIN, 7)              # 头
    F += box((px-0.06, 1.46, pz), (0.23, 0.09, 0.23), (56, 44, 40), 7)      # 头发
    F += box((px-0.16, 0.96, pz-0.02), (0.11, 0.24, 0.13), C1, 7)           # 上臂
    F += box((px-0.34, 0.86, pz-0.05), (0.28, 0.10, 0.11), C1, 7)           # 前臂
    F += box((px-0.50, 0.84, pz-0.05), (0.10, 0.07, 0.09), SKIN, 7)         # 手
    # 椅子（只留座面，背靠交给模型自己补）
    F += box((px+0.12, 0.42, pz), (0.50, 0.07, 0.50), DARK, 6)
    # 窗边绿植（左后）
    F += box((0.30, 0.34, 2.60), (0.48, 0.70, 0.48), (178, 150, 118), 6)
    for i in range(7):
        a = i * 0.897
        F += box((0.30 + 0.26*math.cos(a), 1.10 + 0.22*(i % 3), 2.60 + 0.26*math.sin(a)),
                 (0.60, 0.40, 0.28), GREEN, 6, yaw=a)
    # 前景扶手椅（左下，压边）
    F += box((1.35, 0.62, 4.15), (1.00, 0.62, 0.92), (60, 68, 86), 8)
    F += box((1.35, 0.26, 4.15), (1.08, 0.32, 1.00), (68, 76, 94), 8)
    return F

def main():
    W, H = 1344, 768
    cam = Cam((3.62, 2.46, 5.72), 0.0, -30.0, 63.0, W, H)
    faces = build_scene()
    img, dep = render(faces, cam)
    img.save("/home/justin/imggen-work/out/box_color.png")
    dep.save("/home/justin/imggen-work/out/box_depth.png")
    print("rendered", img.size, len(faces), "faces")

if __name__ == "__main__":
    main()
