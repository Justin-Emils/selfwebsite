# AGENTS.md — 个人网站 selfwebsite

> 给在这个工作区里工作的 AI 助手看的项目基本情况。
> 最后更新：2026-11-23（范围扩为全栈项目；新增文档地图；作废 M0–M5 旧计划）
> **改动历史见 `docs/决策记录.md`；本文件只写"稳定的规矩"，进度一律写 `docs/项目状态.md`。**

---

## 0. 环境与路径（先看这节）

| 项 | 值 |
|---|---|
| 项目根目录 | **`/home/justin/code/selfwebsite`**（本地盘 ZFS，`/home`） |
| 旧副本 | `/rd/Justin/selfwebsite` —— **已废弃**，只是备份，别在那儿开发 |
| 为什么换盘 | `/rd` 是 CIFS 网络盘（`//192.168.1.112/bluemsunDisk`），不支持 `chmod` / 软链接 / `fs.copyFileSync`，前端工具链在上面必崩。详见第 8 节 |
| 启动 | `cd ~/code/selfwebsite && npm run dev` → http://localhost:5173 ；对外访问加 `npm run dev -- --host 0.0.0.0` 后用 `http://192.168.1.117:5173` |
| Node / npm | v22.22.1 / 10.9.4 |
| 远端仓库 | `git@github.com:Justin-Emils/selfwebsite.git`（SSH，分支 `main` 跟踪 `origin/main`） |
| 离线备份 | `~/selfwebsite-legacy-2026-11-22.tar.gz`（459MB，含 `try/lappland` 全部素材，**这是唯一一份旧项目完整快照**） |

新 shell 里推代码前先记住钥匙短语：

```bash
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519_github
```

## 0.5 文档地图（**任何会话开工前先读这一节**）

项目的一切结论都在 `docs/` 里，**不依赖任何一次会话的上下文**。不要凭记忆回答项目问题，先去找文档。

| 你要知道什么 | 去读 |
|---|---|
| **现在到哪了、下一步做什么、有没有阻塞** | **`docs/项目状态.md`**（唯一的状态真相，每次会话结束必须更新） |
| 文档之间怎么找、谁说了算、交接检查单 | `docs/README.md` |
| 作者是什么人、会什么不会什么、**什么话不能说** | `docs/用户画像/`（先看 `技术水平.md` 与 `偏好与协作.md`） |
| 学到哪了、接下来学什么 | `docs/学习计划/进度.md` + `00-总览.md` |
| 项目建什么、不建什么、什么算做完 | `docs/设计.md`（v0.3 草案） |
| 主题与视觉（艾米尔斯图书馆） | `docs/主题.md` |
| 每个决定为什么这么做、当时的代价 | `docs/决策记录.md`（只追加，看最新那条） |
| 建表语句、接口清单、nginx/systemd | `docs/实施细节.md`（可改） |
| 报错很眼熟 | `docs/开发历程.md` |

**三条硬规矩**

1. **`try/` 目录里的任何东西都不是项目依据**（实验区，已被明确否掉过一次）。
2. 项目**不能**放在 `/rd`（CIFS 网络盘）：`chmod`/软链/`copyFileSync` 全失败，`npm install` 会挂。
3. 默认**只给方案不动代码**，除非他当轮明确要求。会话结束前更新 `docs/项目状态.md`。
4. **文档自动更新已授权**（`docs/README.md` 5.1 权限矩阵）：`项目状态.md`、`学习计划/进度.md`、`用户画像/*`、`开发历程.md`、`决策记录.md`、`实施细节.md` 可直接改；`设计.md` 正文、`主题.md` M 节之后的推导、`学习计划/00–04`、`AGENTS.md` 属"有条件"；`主题.md` 的 A–L 节是作者原文，**不许改**。

---

## 1. 项目是什么

- **用户的第一个个人网站**，同时是他练前端手艺的主战场。
- 原计划是静态单页，2026-11-23 起范围已扩为：**多用户 + 门户 + 博客 + 评论 + 权限网关 + 服务器控制台**，最终形态是"艾米尔斯图书馆"（3D/静帧场景导航）。详见 `docs/设计.md`。
- 站点语言中文；**代码注释中文、标识符英文**。

## 2. 用户情况（决定回答方式）

> **权威版本在 `docs/用户画像/`，本节只是摘要。冲突时以那边为准。**

- **真实水平（2026-11-23 作者亲自修正）**：
  - HTML 会；**CSS 会写但很丑、容易出错、出错说不清为什么**（不是"熟悉"）
  - JS 能读懂别人的代码，**自己从零写会卡**，且**不知道怎么把 JS 接到 HTML 上**
  - **TS 连"类型注解"是什么都还不知道**
  - React / Vue 概念级，没独立写过多组件页面；Python、SQL 零基础
- 目标是**练会开发**，不是尽快上线（实习备战 + 日常自用）。所以：讲清"为什么"，给可直接复制的完整文件和命令，**由他自己敲**。
- 术语第一次出现要解释；**一次只引入一个新概念**。
- 说话前先读 `docs/用户画像/技术水平.md` 与 `docs/用户画像/偏好与协作.md`（后者有雷区清单）。

## 3. 协作规则（最高优先级）

1. **代码默认只读**：不要直接改代码、不要执行安装 / 构建 / 删除 / git 操作，**除非他在当轮明确要求**。
   默认输出形态是：命令 + 完整文件内容 + 这样写的原因，由他执行后把输出贴回来。
   **例外（2026-11-23 作者授权）**：`docs/` 下的文档由助手**自动更新**，无需逐次请求，权限矩阵见 `docs/README.md` 5.1。
   改完必须在回复里报一行 `📄 已更新：文件 → 改了什么 → 为什么`；**没报就等于没改**。
2. 不 `git commit`、不 `git push`、不打 tag，除非明确要求。
3. **不要删 `try/` 和 `开发历程/`**：那是他的实验区和开发记录区。
4. 不要反复重构脚手架。他已经决定重建一次，别再把已经跑起来的东西推倒。
5. 报错处理顺序：**要完整原始输出**（不要他复述）→ 证据 → 原因 → 最小修复，一次只改一处。
6. 回答用简体中文；命令、代码、报错信息保持原文。
7. 说"好的做法"时给可验证的判据（Lighthouse 分数、首屏体积、对比度数值），别说"这样更优雅"。
8. **交互式命令要一条一条给**。他习惯整块粘贴，`npm create` / `ssh-keygen` 这类带提示的命令粘一坨会连环失败（已发生两次）。

## 4. 目录约定

**权威版本在 `docs/设计.md` 第 4 节与第 2.4 节，本节只是速查。**

```
selfwebsite/
├─ AGENTS.md
├─ docs/                      # 全部项目文档，入口是 docs/README.md
│  ├─ README.md               # 文档地图 + 交接检查单
│  ├─ 项目状态.md              # 当前进度（唯一状态真相）
│  ├─ 设计.md 主题.md 决策记录.md 实施细节.md 开发历程.md
│  ├─ 用户画像/                # 基本情况 / 技术水平 / 偏好与协作 / 目标与动机
│  └─ 学习计划/                # 00 总览 … 04 纲要 + 进度.md
├─ try/                       # 实验区。**内容一律不是项目依据**
├─ 参考图片/                   # 作者提供的风格参考（不是素材，只作参考）
├─ 开发历程/                   # 原始截图
├─ 内容.txt                   # 早期随手记录，**不作为内容依据**
├─ public/                    # favicon / scene/（静帧图）/ media/
├─ src/
│  ├─ routes/                 # 路由级组件（Home / BlogList / Login / admin/*）
│  ├─ scenes/<sceneId>/       # 每个场景一个目录：manifest.json + 静帧
│  ├─ components/scene/       # 场景渲染 + 锚点投影
│  ├─ components/{layout,ui}/ # 通用组件
│  ├─ content/                # 文案数据
│  ├─ hooks/  lib/  styles/
├─ api/                       # 后端（P2 创建，Python + FastAPI）
└─ index.html / vite.config.ts / tsconfig*.json / eslint.config.js
```

三条结构纪律：
- **新增场景 = 新增一个目录**，不改路由表（见 `docs/设计.md` 2.4）。
- **样式跟组件走**（`X.module.css`），删掉一个区不影响别的区。
- **文案放 `src/content/` 或场景目录，组件只负责渲染**。

## 5. 技术栈

**已装**：React 19.3 + TypeScript 6.0 + Vite 8.3（rolldown 引擎）+ ESLint 10.14 / typescript-eslint 8.72（flat config，含 react-hooks、react-refresh）。样式走 **CSS Modules + CSS 变量 token**。

**后端（P2 起，2026-11-23 已定）**：Python 3.12 + FastAPI + SQLAlchemy 2.0(async) + Alembic + Pydantic v2 + SQLite(WAL) + markdown-it-py/Pygments/nh3 + argon2-cffi/pyotp。部署：云上 nginx 作公网入口，计算服务器跑 API（Tailscale 内网），上传文件放存储服务器 `/rd/Justin/selfwebsite/uploads`。**数据库必须在本地盘，不得放 CIFS/NFS。**

**待装**：`three` + `three-stdlib`（P9 才装，别提前引进来把首屏撑大）；`react-router`、`@tanstack/react-query`（P1 起）。

**暂缓 / 不做**（他问起时先问清动机）：Tailwind、UI 组件库、Zustand/Redux、Next.js/SSR、富文本编辑器、Prometheus/Grafana、微服务/消息队列/缓存中间件、Prettier（后期再上）、pnpm（目前统一 npm）。
（注：**"自建 CMS" 已从暂缓变成正式需求**——站内 Markdown 写作是必须的。）

**版本策略**：优先稳定线。学习期不要拿构建工具当练习内容 —— 卡住超过半天就降回上一稳定大版本。

## 6. 里程碑与进度

**旧 M0–M5 计划已作废**（那是"静态单页"时代的）。现行有两条并行的线：

| 线 | 阶段 | 详细文档 |
|---|---|---|
| **项目线** | P0 首页原型 → P1 场景框架 → P2 后端 → P3 账号 → P4 权限网关 → P5 写博客 → P6 读博客+计数 → P7 评论 → P8 控制台 → P9 WebGL → P10 agent | `docs/设计.md` 第 12 节 |
| **学习线** | A JS/TS 地基 → B React → C 类型与投影 → D Python/FastAPI → E SQL/认证 → F 运维 → G Three.js | `docs/学习计划/` |

两者对应关系：B→P0、C→P1、D→P2、E→P3+P4、F→P5+P8、G→P9。
**当前状态永远以 `docs/项目状态.md` 为准。**

## 7. 当前状态

**不要在这里写进度——去看 `docs/项目状态.md`。**

只保留几条稳定的技术基线：

- 提交 `acba880 chore: rebuild scaffold — vite + react-ts on local disk`，已推送 `origin/main`。
- **构建基线**：`dist/assets/index-*.js` **222.44 kB / gzip 69.28 kB**，构建 348ms。加 three.js 后必须 `React.lazy` + `manualChunks` 拆 chunk。
- `src/` 目前仍是脚手架原样（样例计数器 + 模板样式），P0 会整份替换。
- `npm run dev` 已验证可用；`public/media/character.webm` 就位（2.4MB，用途待定）。

## 8. 已知坑（踩过的，别再踩）

| 坑 | 说明 / 正确做法 |
|---|---|
| **项目不得放在 CIFS 共享盘** | `/rd` = `//192.168.1.112/bluemsunDisk`，挂载参数 `nounix,file_mode=0777`。实测：`writeFileSync` / `cp` / `rename` / 无 bin 包的 `npm install` 可用；**`chmod`、`ln -s`、`fs.copyFileSync` 全部失败** |
| `create-vite` 在 CIFS 上必挂 | 它用 `fs.copyFileSync`，内部要 `fchmod` → `EPERM ... copyFile README.md`。正确姿势：`cd /tmp && npm create vite@latest x -- --template react-ts`，再 `cp -r /tmp/x/. 目标/` |
| `npm install` 在 CIFS 上是死结 | 装到 `.bin/` 建软链时 `ENOTSUP ... symlink`。`--no-bin-links` 能装完但 `npm run dev` 找不到命令。**只能换本地盘** |
| 绝对路径被 create-vite 吃掉 | `npm create vite@latest /tmp/x` 会写到 `<cwd>/tmp/x`（内部 `path.join`）。先 `cd` 到目标父目录再只给目录名 |
| 跨系统 `node_modules` | 复制过来 = 原生二进制不匹配（win32 vs linux）。只复制 `package.json` + `package-lock.json`，重装 |
| 假 loading | `setTimeout(3000)` 固定等 3 秒 → 改成真事件：`<CosmicSphere onReady={() => setLoading(false)} />` |
| 组件 CSS 里写全局 reset | `Loading.css` 顶部 `*{margin:0;padding:0}` 污染全站；reset 只放 `styles/reset.css` |
| 模板样例样式 | `App.css` / `index.css` 仍是模板示例（`.hero`、`#root{width:1126px}`…），**P0 整份替换**，别在它上面打补丁 |
| `<video autoPlay muted>` | 缺 `playsInline` + `loop`：iOS Safari 不自动播 / 播完停住；叠 `mix-blend-mode: screen` 在深色下易"消失" |
| `character.webm` 2.4MB | 当加载动画太重，转 VP9 目标 ≤300KB，或改 CSS/Lottie |
| three.js 不清理 | `useEffect` cleanup 里 `cancelAnimationFrame` / `setAnimationLoop(null)` / `renderer|geometry|material.dispose()`，并监听 resize；否则 HMR 攒 WebGL context 报 "Too many active WebGL contexts" |
| `index.html` 元信息 | 现在是 `lang="en"`、`<title>sw-new</title>` 残留 → 改 `zh-CN` + 真标题 + description/OG/theme-color |
| git 提交身份 | 全局默认是空的，会报 `Author identity unknown`。用历史身份：`Justin6789 <woshijiaqinyan@163.com>` |
| GitHub 推不上去 | 密码认证已废弃。用 SSH key `~/.ssh/id_ed25519_github`（`~/.ssh/config` 已配 `IdentitiesOnly`）。`ssh -T` 出现 `Bye Bye` **不代表失败**，用 `git ls-remote` 或直接 push 判断 |

## 9. 常用命令

```bash
cd ~/code/selfwebsite
npm run dev        # 开发服务器 5173
npm run build      # tsc -b && vite build → dist/
npm run preview    # 预览 dist
npm run lint       # ESLint
npm ci             # 按 lockfile 精确安装（换机 / CI）

# 推代码（新 shell 先加载密钥）
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519_github
git add -A && git commit -m "..." && git push
```

部署形态（P1 起逐步落地）：纯静态 `dist/` 交云上 Nginx；`/assets/*` 长缓存 immutable，`index.html` no-cache，`try_files $uri /index.html` 兜 SPA 路由，开 gzip/brotli，certbot 上 HTTPS，用普通用户构建。

## 10. 参考资料

- `内容.txt` — 作者早期的随手记录，**不作为内容依据**（内容待议 T7，见 `docs/设计.md` 第 10 节）
- `开发历程/`、`docs/` — 报错截图与决策记录；**新踩的坑记到 `docs/开发历程.md`，别只留在聊天里**
- **`docs/主题.md` — 主题的唯一依据**（艾米尔斯图书馆；A–L 节是作者的原始设计，M 节是可执行 token）
- ⚠️ `try/CosmicSphere.vue`、`try/particles.js`、`try/style.css` —— **作者已明确作废，不得作为主题或技术依据**（见 `docs/决策记录.md` D-004）
- `try/scene-fix/` — 书房静帧的生成管线（自算机位 + ControlNet 深度锁机位）。**只作为素材来源与机位参数的参考**，不是设计依据
- `参考图片/` — 作者提供的两张风格参考图
- 设计拆解模板：每次看一个网站只拆 5 层（版式栅格 / 字号阶梯 / 颜色 token / 动效时长与缓动 / 工程层体积与可访问性），**只抄结构不抄皮肤**，把抄到的 3 条规则写进 `styles/tokens.css`
