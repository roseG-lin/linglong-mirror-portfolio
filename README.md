# 玲珑镜面 MIRROR — 作品集静态包（离线版）

白纸 · 手绘黑线 · 彩色贴纸 —— 单页作品集，全部资源已本地化，零外链、零 CDN 依赖。

## 打开方式

**方式一（推荐）**：双击运行 `start.bat`（Windows），自动启动本地服务器并打开浏览器。

**方式二（手动）**：

```bash
node server.js
# 打开 http://127.0.0.1:7100/
```

**方式三**：任意静态服务器指向本目录即可（如 `npx serve`、Python `http.server`）。
注意：因使用 ES Modules，`file://` 直接双击 index.html 无法运行，需通过 HTTP 访问。

## 目录结构

- `index.html` — 单页入口（HTML + CSS + JS ES Modules）
- `data.js` — 唯一内容配置：姓名 / 简介 / 六个作品 / 社交 / 邮箱，改这一个文件即可换内容
- `server.js` — 零依赖静态服务器（`node server.js [--port 7100]`）
- `vendor/` — GSAP / ScrollTrigger / Draggable / InertiaPlugin / Lenis / Three.js 本地副本
- `fonts/` — Space Mono / Caveat 字体本地副本（woff2 + fonts.css）

## 内容维护

所有文案与作品数据集中在 `data.js`，每个作品含胶带色（red/yellow/blue）、
手绘装饰框（circle/brackets/corners/wavy/double/arrow）、程序化插画（tree/blocks/film/terminal/swatches/loop），
替换时沿用这些 id 即可，无需改动 index.html。

## 隐私说明

邮箱与社交账号当前为占位信息，正式发布前请在 `data.js` 中替换为真实联系方式。
