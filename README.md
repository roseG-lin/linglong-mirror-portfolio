# www.remifei.cn — 林润基作品集（静态站）

深色「个人宇宙」首页 + 9 个可交互案例页 + RemiOS 桌面模式。零后端、零外部 CDN：
字体、视频、截图全在仓内，任意静态服务器指向本目录即可跑。

## 本地预览

```bash
python -m http.server 8790 --bind 127.0.0.1
# 打开 http://127.0.0.1:8790/
```

页面用到 ES Module，必须走 HTTP，`file://` 双击打不开。

## 目录

| 路径 | 说明 |
|---|---|
| `index.html` | 首页（HTML + 内联 CSS/JS）。`CONTENT` 对象是文案与案例卡的唯一来源 |
| `case/` | 9 个案例页，页内 DEMO 可直接点；`case.css` 是样式单一源，`case.js` 只做渐进增强 |
| `os/` | RemiOS 桌面模式；壁纸视频按网络/动效偏好条件加载 |
| `folio/` | 纸上手绘版单页（只从 404 页留了入口） |
| `data/site-facts.json` | 对外口径单一源（薪资 / 产品数 / 联系方式…），由 `scripts/sync_facts.py` 同步进各页 |
| `llms.txt`、`llms-full.txt` | 给 AI 抓取用的结构化自述 |
| `sitemap.xml`、`robots.txt`、`indexnow-key.txt` | 收录与推送 |
| `tools/` | `cover.py` 封面图规格化；`evidence.py` 真截图 → 案例页证据图（含脱敏） |
| `tests/` | 契约测试 |
| `project-*.html` | 历史项目页（现役演示已迁到 `case/`，保留链接兼容） |

## 改内容

1. **数字 / 联系方式**：改 `data/site-facts.json` → `python scripts/sync_facts.py` → 跑测试。
   不要直接在各页手改数字，`--check` 会抓出漂移。
2. **首页文案与案例卡**：改 `index.html` 里的 `CONTENT`。
3. **案例页**：改 `case/*.html`。

## 图片规范

- **首页卡片封面**：912×608（3:2）。`python tools/cover.py 原图 输出.jpg` 一把过；
  `.case-thumb` 用 `aspect-ratio` 渲染，尺寸不符会被二次裁切（`tests/test_media_geometry.py` 有硬锁）。
- **案例页证据图**：真截图，`python tools/evidence.py 原图 --slug 01-huodai --no 01 --op … --num …`
  自动去 EXIF、压到宽 1400、可 `--redact` 打码；跑完直接打印 `<figure class="evidence">` 段落。

## 口径纪律

- **零虚构**：每个数字都要能现场复跑。首页卡片是概念封面，证据在案例页的交互 DEMO 与截图里。
- **涉密必脱敏**：湛江项目相关的截图与材料，不得出现客户名、真实订单号、手机号、内网地址；
  `tools/evidence.py --confidential` 没打码也没 `--checked` 会直接拒绝执行。
- **AI 标识保留**：AI 生成的封面/壁纸，画面自带的「AI 生成」字样属于合规标识，不得裁掉。

## 测试

```bash
python -m pytest tests/ -q
```

覆盖：对外口径单一源、站内死链、图片几何、证据图工具（规格/打码/保密门）、设计系统、内容去重。
