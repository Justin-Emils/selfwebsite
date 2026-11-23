# 阶段 B · React 与首页书房原型（3 周）

> 对应项目阶段 **P0**。产出：一个能在浏览器里打开、手机上也好看的首页书房。
> 前置：阶段 A 的五个练习都通过验收。

---

## 0. 用哪套教程

**官方文档中文版**：`react.dev/zh-hans` → 「学习 React」这一栏。**不要看别的**，官方教程 2023 年重写过，比任何视频都准。

| 章节 | 内容 | 处理 |
|---|---|---|
| 快速入门 | 组件、JSX、条件渲染、列表、事件、state | **必读** |
| 井字棋教程 | 完整小游戏，把核心概念串一遍 | **必做**（半天） |
| 描述 UI | 组件拆分、props、纯函数 | **必读** |
| 添加交互 | state、渲染触发、状态快照、批处理 | **必读，最重要** |
| 管理状态 | 状态结构、状态提升、保留与重置 | **必读** |
| 逃生舱 | ref、Effect、Effect 清理 | **读 useEffect 那一节** |
| （跳过）服务端渲染、Server Components | 与本项目无关 | 跳过 |

---

## 1. 第一周：React 核心概念

### 要掌握的最小集（就这 8 个，不要贪多）

| # | 概念 | 能回答的问题 |
|---|---|---|
| 1 | 组件 = 函数 | 为什么组件名必须大写？ |
| 2 | props | 父组件怎么给子组件传数据？能不能改？ |
| 3 | state + `useState` | 为什么改了变量界面不更新？ |
| 4 | 渲染 = 重新执行函数 | 一次点击到界面变化，中间发生了什么？ |
| 5 | 列表 + `key` | 为什么 `key` 不能用数组下标？ |
| 6 | 条件渲染 | `&&` 和三元怎么选？ |
| 7 | 受控输入 | `<input>` 的值为什么必须绑 state？ |
| 8 | `useEffect` + 清理 | 为什么要有 return 那个函数？ |

### 练习 B1（本周产出）

把阶段 A 的**练习 5（假服务门户）完全改写成 React**：

```
src/
├─ App.tsx
├─ components/
│  ├─ ServiceCard.tsx      # 单个卡片，接收 props
│  └─ SearchBox.tsx        # 受控输入
└─ data/services.ts        # 数据 + 类型
```

要求：
- `ServiceCard` **只能**接收 props，不能自己读数据
- 搜索用 `useState` + `filter`，**不要**用 DOM 操作
- 列表渲染必须给 `key`，且用 `slug` 而不是下标
- 状态灯的颜色由 `status: 'ok' | 'warn' | 'error'` 联合类型决定

**判据**：代码里搜不到任何 `document.querySelector`。

---

## 2. 第二周：首页书房静态叠层（P0 正式开工）

### 2.1 先准备素材

| 素材 | 怎么来 | 规格 |
|---|---|---|
| 静帧 | 用现有 `try/scene-fix/alt-empty-room-1672x941.png`（无人物版） | 转成 WebP，≤300 KB |
| 手机版 | 用同一张图裁切（居中偏下，保留窗+桌+书架） | 宽 828px，≤150 KB |
| 人物（可选） | 现在可以先不做 | — |

转 WebP 的命令（装了 `cwebp` 就能用）：

```bash
cwebp -q 82 try/scene-fix/alt-empty-room-1672x941.png -o public/scene/study/still.webp
```

### 2.2 目录与结构

```
src/
├─ routes/Home.tsx                 # 路由级组件
├─ components/scene/
│  ├─ SceneStage.tsx               # 负责铺背景图 + 承载叠层
│  └─ AnchorCard.tsx               # 定位到锚点的卡片
├─ scenes/study/
│  ├─ study.anchors.ts             # 锚点坐标（先写死百分比）
│  └─ study.content.ts             # 卡片文案
└─ styles/{reset,tokens,global}.css # 从 docs/主题.md M 节抄出来
```

### 2.3 关键技术点：卡片怎么"贴在桌面上"

**这一周先用最笨的办法**——百分比坐标。不要一上来就搞 3D 投影。

```ts
// study.anchors.ts
export const anchors = {
  deskLeft:   { x: 22, y: 58 },   // 画面百分比
  deskRight:  { x: 52, y: 55 },
  bookshelf:  { x: 74, y: 32 },
  window:     { x: 16, y: 22 },
} as const
```

```tsx
// SceneStage.tsx 里
<div style={{ position: 'relative', aspectRatio: '1672 / 941' }}>
  <img src="/scene/study/still.webp" alt="" style={{ width: '100%', display: 'block' }} />
  <AnchorCard anchor={anchors.deskLeft} />
</div>
```

**为什么先用百分比**：你这周还不懂坐标系变换，用百分比能立刻看到成品，然后把"卡片位置对不对"这个审美问题先解决掉。等阶段 C 再换成真投影——那时只需要改 `AnchorCard` 里算位置的那几行，其它代码不动。

**这就是设计文档里"renderer 可替换"的同一条思路：先让它能跑，再让它正确。**

### 2.4 样式：把主题 token 变成真文件

从 `docs/主题.md` M 节抄写，创建三个 CSS 文件：

| 文件 | 内容 |
|---|---|
| `styles/reset.css` | 清浏览器默认值（`*{box-sizing}`、图片 block、表单继承字体） |
| `styles/tokens.css` | M1–M4 的颜色/字体/间距/圆角/阴影/动效变量 |
| `styles/global.css` | body 底色、字体、链接、焦点环、`prefers-reduced-motion` 兜底 |

⚠️ 三条铁律（违反就是返工）：

1. 组件 CSS 里**不出现十六进制色值**，只用 `var(--xxx)`
2. 间距只用 `--space-1..10` 这几档
3. 组件 CSS 里**不写全局 reset**（会污染全站，这个坑你踩过）

### 2.5 响应式：只做两档

| 宽度 | 布局 |
|---|---|
| ≥768px | 静帧铺满 + 卡片按锚点绝对定位 |
| <768px | 静帧变成上方背景条（或整张铺底半透明），卡片改成流水列表 |

判据：**iPhone SE 宽度 375px 下横向不出现滚动条**（`document.documentElement.scrollWidth === clientWidth`）。

### 2.6 练习 B2（本周产出）

首页能跑起来，包含：
- 静帧背景 + 3–4 张锚点卡片（标题 + 一句话 + 可点）
- 顶部或角落：欢迎语 + 一个"结构图"占位按钮（点了先跳到空白页也行）
- 鼠标移动时全站位移 1–2px 的视差（**必须在 `prefers-reduced-motion` 下关闭**）
- 关掉图片也能看到文字（把 `<img>` 删掉试试，卡片应该仍然可读）

---

## 3. 第三周：打磨与自测

| 任务 | 判据 |
|---|---|
| 字体子集化 | 标题衬线字体下载 ≤150 KB（用 `fonttools pyftsubset` 或 `glyphhanger`） |
| 图片压缩 | 静帧 ≤300 KB，首屏总下载 ≤800 KB |
| 无障碍 | Tab 键能走到每个卡片；焦点框可见；图片有 `alt`（装饰图 `alt=""`） |
| 动效降级 | 系统开"减少动态效果"后无视差、无淡入 |
| Lighthouse | Performance ≥85，Accessibility ≥95 |
| 真机 | 用手机打开（`npm run dev -- --host 0.0.0.0` + 局域网 IP）看一遍 |

---

## 4. 验收：三个问题 + 一轮代码审查

| # | 问题 |
|---|---|
| 1 | `useState` 改了值之后，React 是怎么知道要重新渲染的？ |
| 2 | 为什么列表 `key` 不能用数组下标？给一个会出 bug 的具体场景。 |
| 3 | `useEffect` 里为什么要 return 一个函数？不写会怎样？ |

**代码审查重点**：

- 组件是否超过 150 行（超了就该拆）
- 有没有把数据直接写死在 JSX 里（应该在 `content/` 或 `data/`）
- 有没有 `any`（TS 里出现 `any` 就是放弃了类型，除了极少数情况）
- 样式是否全部走 token

---

## 5. 常见坑

| 坑 | 正确做法 |
|---|---|
| 直接改 state：`list.push(x)` 然后 `setList(list)` | 必须新建：`setList([...list, x])` |
| `useEffect` 里加事件监听没清理 | 返回 `() => removeEventListener(...)`，否则热更新会重复绑定 |
| 图片不写 `width/height` | 加载时页面跳动（CLS），必须写死宽高比 |
| 用 `index` 当 key | 删除/排序后状态错位 |
| 在组件里写 `document.querySelector` | React 里不该碰 DOM，用 ref |
| 把 CSS 写成全局选择器 `div {}` | 用 CSS Modules，类名自动隔离 |
| 卡片用 `position: absolute` 但父元素没 `position: relative` | 会定位到整个页面 |

---

## 6. 三周日程

| 周 | 内容 | 时长 |
|---|---|---|
| 第 1 周 | react.dev 快速入门 + 井字棋 + 练习 B1 | ≈10 h |
| 第 2 周 | 素材准备 + 三个 CSS + 场景组件 + 练习 B2 | ≈12 h |
| 第 3 周 | 字体子集化 + 压缩 + 无障碍 + Lighthouse + 真机 | ≈10 h |

---

## 7. 学完会得到什么

| 现在 | 学完 |
|---|---|
| 知道 React 是"组件化" | 能独立拆组件、定 props、管状态 |
| 只能照抄别人的页面 | 有一个**自己写的**首页，能在手机上打开给别人看 |
| 不知道"性能"指什么 | 知道首屏体积、对比度、CLS 这些数字怎么测、怎么改 |

---

_学完 B 阶段汇报后，我写 C 阶段的详细修订版。C 阶段会把"百分比定位"换成真正的坐标投影——那时你会用到阶段 A 练习 4 的那个 20 行函数。_
