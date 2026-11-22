# AGENTS.md — 个人网站 selfwebsite

> 给在这个工作区里工作的 AI 助手看的项目基本情况。
> 内容基于 2026-11 对本目录的只读检查写成；实际情况变了就更新这一份。

---

## 1. 项目是什么

- **用户的第一个个人网站**，同时是他练前端手艺的主战场。
- 站点语言中文；**代码注释中文、标识符英文**。

## 2. 用户情况（决定回答方式）

- 前端新手：HTML / CSS 熟悉；JS 在学；TS 刚开始；Vue 和 React 知道概念但缺项目经验。
- 目标是**练会开发**，不是尽快上线。所以：讲清"为什么"，给可直接复制的完整文件和命令，**由他自己敲**。
- 术语第一次出现要解释；**一次只引入一个新概念**，不要一口气塞 Tailwind + 路由 + 状态管理。

## 3. 协作规则（最高优先级）

1. **默认只读**：不要直接改文件、不要执行安装 / 构建 / 删除 / git 操作，**除非他在当轮明确要求**。
   默认输出形态是：命令 + 完整文件内容 + 这样写的原因，由他执行后把输出贴回来。
2. 不 `git commit`、不 `git push`、不打 tag，除非明确要求。
3. **不要删 `try/` 和 `开发历程/`**：那是他的实验区和开发记录区。
4. 不要反复重构脚手架。他已经决定重建一次，别再把已经跑起来的东西推倒。
5. 报错处理顺序：**要完整原始输出**（不要他复述）→ 证据 → 原因 → 最小修复，一次只改一处。
6. 回答用简体中文；命令、代码、报错信息保持原文。
7. 说"好的做法"时给可验证的判据（Lighthouse 分数、首屏体积、对比度数值），别说"这样更优雅"。

## 4. 目录约定（目标形态）

```
selfwebsite/
├─ AGENTS.md                  # 本文件
├─ docs/                      # 开发历程、决策记录（从 开发历程/ 逐步整理成文字）
├─ try/                       # 实验区：不进主构建、大素材不进 git
│  ├─ CosmicSphere.vue        # 星球背景的 Vue 版（React 版移植的来源）
│  ├─ particles.js            # 粒子背景（纯 JS 版）
│  ├─ style.css               # 星辰主题的 CSS 变量草稿
│  └─ lappland/               # sprite 帧动画实验（2828 张 png，约 500MB，勿入 git）
├─ 开发历程/                   # 原始截图记录（上来就报错.png 等）
├─ 内容.txt                   # 六块文案的原始草稿
├─ public/                    # 原样拷贝进产物
│  ├─ favicon.svg
│  └─ media/character.webm
├─ src/
│  ├─ main.tsx / App.tsx
│  ├─ styles/{reset,tokens,global}.css
│  ├─ content/{profile,awards,stack,hobbies,posts}.ts
│  ├─ sections/{Hero,About,Awards,Stack,Hobbies,Contact}/   # 一个区一个文件夹
│  ├─ components/{layout,ui,background}/
│  └─ hooks/{useInView.ts,useReducedMotion.ts}
├─ index.html
└─ vite.config.ts / tsconfig.json / eslint.config.js
```

两条结构纪律：
- **一个 section 一个文件夹**，样式 `X.module.css` 跟组件走，删掉一个区不影响别的区。
- **文案放 `src/content/`，组件只负责渲染**。改内容不碰 JSX。

## 5. 技术栈

**已定**：Vite + React 19 + TypeScript + **CSS Modules** + 原生 CSS 变量（设计 token）；3D 用 `three` + `three-stdlib`；代码检查 **ESLint**（flat config，含 typescript-eslint / react-hooks / react-refresh）。

**暂缓 / 不做**（他问起时先问清动机）：Tailwind、UI 组件库、Zustand/Redux、Next.js/SSR、自建 CMS/MDX、Prettier（M5 再上）。

**版本策略**：优先稳定线，别追 `@latest` 最前沿引擎（vite 8 / rolldown / ESLint 10 这类）。学习期不要拿构建工具当练习内容 —— 卡住超过半天就降回上一个稳定大版本。

## 6. 里程碑与进度

| 阶段 | 产出 | 学到的 | 状态 |
|---|---|---|---|
| M0 骨架 | `dev` + `build` + 部署可跑 | 工具链、lockfile、目录约定 | 进行中 |
| M1 静态单页 | 六区 HTML + CSS 排版，零交互 | flex/grid、间距体系、字阶、响应式、对比度 | 未开始 |
| M2 拆组件 | 每区变组件，文案走 `content/` | props、`map`+`key`、条件渲染 | 未开始 |
| M3 动效 | 滚动进场、hover、`prefers-reduced-motion` | `useEffect`/`useRef`、IntersectionObserver、自定义 Hook | 未开始 |
| M4 视觉重头戏 | Vue 版星球移植成 React 背景，资源就绪才淡出 loading | three.js 生命周期、`dispose()`、加载状态机、TS 类型 | 未开始 |
| M5 工程化 | TS 全量、lint、暗色模式、SEO/OG、Lighthouse、CI | 类型、质量门禁、性能预算 | 未开始 |

## 7. 当前状态（2026-11）

- **旧脚手架仍在目录里**：Windows 上 `create-vite` 的 JS + React 模板，`src/` 只有 `App.jsx` / `main.jsx` / `Loading*` / `CosmicSphereReact.jsx`，`pages/` 是空的。**重建尚未完成。**
- `node_modules/` 是 Windows 上装的：含 `@rolldown/binding-win32-x64-msvc`、`lightningcss-win32-x64-msvc`、`.cmd`/`.ps1` 的 bin 垫片 → 在 Linux 上 `npm run dev` 必然失败。**换机只复制 `package.json` + `package-lock.json`，`node_modules` 永远重装。**
- 备份：`~/selfwebsite-legacy-2026-11-22.tar.gz`（约 459MB，含 `try/lappland` 素材）。
- `dist/` 是 Windows 上 `npm run build` 的产物，`dist/assets/index-*.js` 约 725KB（未压缩，three.js 全量打进去了）。

## 8. 已知坑（踩过的，别再踩）

| 坑 | 说明 / 正确做法 |
|---|---|
| 跨系统 `node_modules` | 复制过来 = 原生二进制不匹配。删 `node_modules` 保留 lockfile，`npm ci` |
| 假 loading | `setTimeout(3000)` 固定等 3 秒 → 改成真事件：`<CosmicSphere onReady={() => setLoading(false)} />` |
| 组件 CSS 里写全局 reset | `Loading.css` 顶部 `*{margin:0;padding:0}` 会污染全站；reset 只放 `styles/reset.css` |
| 模板死代码 | `App.css`（`.hero/.framework/#root{width:1126px}`）没被 import；`index.css` 的 `#root` 固定宽度 — 全删 |
| `<video autoPlay muted>` | 缺 `playsInline` + `loop`：iOS Safari 不自动播 / 播完停住；叠 `mix-blend-mode: screen` 在深色下易"消失" |
| `public/character.webm` 2.4MB | 当加载动画太重，转 VP9 目标 ≤300KB，或改 CSS/Lottie |
| three.js 不清理 | `useEffect` cleanup 里 `cancelAnimationFrame` / `setAnimationLoop(null)` / `renderer|geometry|material.dispose()`，并监听 resize；否则 HMR 攒 WebGL context 报 "Too many active WebGL contexts" |
| `index.html` 元信息 | `lang="en"` → `zh-CN`；title/description/OG/theme-color 都要补 |
| git `dubious ownership` | 目录属主与当前用户不一致：`git config --global --add safe.directory /rd/Justin/selfwebsite` |
| `try/lappland` 500MB | 2828 张 png，**绝不入 git**；`.gitignore` 里排除，或挪到仓库外 |
| `npm create vite@mywebsite` | 项目名写进了包名位置 → `ETARGET`。正确：`npm create vite@latest mywebsite -- --template react-ts` |

## 9. 常用命令

```bash
npm ci            # 按 lockfile 精确安装（换机/CI 用这个，不是 npm install）
npm run dev       # 开发服务器（默认 5173）
npm run build     # 产出 dist/
npm run preview   # 本地预览 dist
npm run lint      # ESLint
```

部署形态（计划中）：纯静态 `dist/` 交 Nginx；`/assets/*` 长缓存 immutable，`index.html` no-cache，`try_files $uri /index.html` 兜 SPA 路由，开 gzip/brotli，certbot 上 HTTPS，用普通用户构建。

## 10. 参考资料

- `内容.txt` — 六块文案草稿（M1 要扩写成真实文案）
- `开发历程/`、`docs/` — 报错截图与决策记录；**新踩的坑记到 `docs/开发历程.md`，别只留在聊天里**
- `try/CosmicSphere.vue` — 星球背景的 Vue 原型，M4 移植 React 时以它为准
- 设计拆解模板：每次看一个网站只拆 5 层（版式栅格 / 字号阶梯 / 颜色 token / 动效时长与缓动 / 工程层体积与可访问性），**只抄结构不抄皮肤**，把抄到的 3 条规则写进 `styles/tokens.css`
