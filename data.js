/* ============================================================
   玲珑镜面 · 作品集数据配置
   统一替换入口：改这里即可替换姓名、品牌、简介、作品、社交与邮箱
   内容来源：第二大脑 07-知识沉淀/求职/个人画像 v2.0（2026-09-09 数据时点）
   纪律：只写 [数据] 级可复现战绩；湛江项目零出现；不写英语能力
   ============================================================ */

export const SITE = {
  name: "Raymood LIN",
  brand: "玲珑镜面",
  brandEn: "MIRROR",
  role: "AI 售前 / 解决方案 · 玲珑产品矩阵独立作者",
  email: "raymood@linglong.dev",
  year: "2026",
  location: "SHENZHEN / GUANGZHOU",

  /* 首屏多组手绘字标 */
  heroTitle: [
    { text: "玲珑镜面", kind: "zh" },
    { text: "MIRROR", kind: "en" },
    { text: "PORTFOLIO — 作品集", kind: "sub" },
  ],
  heroKicker: "PAPER · INK · STICKERS",
  heroNote: "会造 AI 产品，也会把方案讲明白——两条手艺，同一个人。",

  /* ABOUT 个人介绍（进入视口时播放乱码解码动画） */
  aboutTitle: "关于我 / ABOUT",
  about: [
    "你好，我是 Raymood。过去两年我是音视频行业的售前工程师：累计为 1300+ 家公司做方案培训，推进 80+ 个项目向客户与甲方汇报，参与 20+ 个项目落地验收——把技术讲明白、把客户说服，是我的本职硬通货。",
    "现在我all in AI：用 AI Coding 独立构建玲珑产品矩阵（20+ 工程目录）——自建 RAG 全链路（119 文件 → 1529 向量点，724 秒建库，抽样 5 问 4 中）、电商客服 Agent（20 条评测风险零漏网）、求职托举流水线（392 项测试全绿）。我认为自己最稀缺的能力是学习速度：3 天从零跑通生产级 RAG 全链路。",
    "我做事有循证底线：每个论断都要有来源，每个战绩都要能复现。这个站本身也是作品——白纸、手绘黑线与贴纸构成的玲珑镜面，每条界面规则都说得出存在的理由。",
  ],
  aboutFacts: [
    { k: "FOCUS", v: "AI 售前 / 解决方案 / FDE" },
    { k: "STACK", v: "AI Coding · RAG · Agent 护栏" },
    { k: "PROOF", v: "全部战绩可复现" },
  ],

  /* 社交账号 */
  socials: [
    { label: "GitHub", handle: "@raymood-lin", url: "https://github.com/" },
    { label: "X / Twitter", handle: "@raymood_lin", url: "https://x.com/" },
    { label: "Bilibili", handle: "玲珑镜面", url: "https://www.bilibili.com/" },
    { label: "Juejin", handle: "@raymood", url: "https://juejin.cn/" },
  ],

  /* 六个作品项目
     tape: red | yellow | blue   frame: 手绘装饰框 id   art: 程序化插画 id */
  works: [
    {
      id: "mirror",
      title: "玲珑镜面 Mirror",
      category: "自适应界面设计引擎",
      year: "2026",
      tape: "red",
      frame: "circle",
      art: "tree",
      blurb: "Skill 声明数据与意图，自动长出可解释的前端界面。",
      desc: [
        "玲珑镜面是玲珑系列的通用展示层：Skill / 插件只需提供结构化数据与声明式配置，引擎即自动生成可交互界面——不硬编码任何单个 Skill 的逻辑。",
        "五层架构各层有论文依据：local-first 数据层、三层模式识别（内置约定 / mirror.yaml / AI 辅助草稿）、Vega-Lite 钻取层级树、多端适配、行为日志进化层。",
        "通用性已被实证：玲珑 X 光导出的安全审查数据被镜面提取器零适配改动直接消费，全量 171 项测试零回退。",
      ],
      tags: ["TypeScript", "Vega-Lite", "Local-first", "Design Engine"],
      link: { label: "仓库 README", url: "https://github.com/" },
    },
    {
      id: "longjob",
      title: "玲珑职举 LongJob",
      category: "求职托举流水线 L0–L5",
      year: "2026",
      tape: "yellow",
      frame: "brackets",
      art: "terminal",
      blurb: "输入目标 JD，产出定制简历 + 作品集内容包 + Demo 工厂 + 面试弹药。",
      desc: [
        "一条六段状态机流水线：JD 解析 → 能力命中映射 → 简历定制（保密红线自动执行）→ 内容包生成 → Demo 工厂（3-5 天学差冲刺）→ 面试弹药库。",
        "工程质量：392 项测试全绿（09-09 实测），v1.1 时点覆盖率 97%；简历工坊 6 版式 × 5 配色 = 30 组合，ATS 约束（字体栈 / 禁连字 / ASCII 日期）由测试逐模板锁定。",
        "学习闭环：岗位差距倒推课程（10 位教育专家心智模型），面试复盘缺口回流为课程——面试 → 复盘 → 课程 → 再面试，首尾相接。",
      ],
      tags: ["Python", "TDD", "Pipeline", "97% Coverage"],
      link: { label: "了解更多", url: "https://github.com/" },
    },
    {
      id: "rag",
      title: "货代知识库 · RAG 全链路",
      category: "生产级检索栈自建",
      year: "2026",
      tape: "blue",
      frame: "corners",
      art: "blocks",
      blurb: "119 文件 → 1529 向量点，724 秒建库，抽样 5 问 4 中。",
      desc: [
        "从零自建生产级检索栈：Qdrant 二进制 + BGE 本地向量模型，全程 CPU 实测延迟，不依赖任何云服务。",
        "战绩留档可复现：119 个文件切出 1527 块、写入 1529 个向量点，724 秒完成建库；检索抽样 5 问 4 中。脚本与终端输出全部保存，随时可重跑。",
        "这套链路后来成为玲珑职举 Demo 工厂的第一个候选产线——学习成果直接转化为可演示的作品集素材。",
      ],
      tags: ["RAG", "Qdrant", "BGE", "可复现证据"],
      link: { label: "了解更多", url: "https://github.com/" },
    },
    {
      id: "agent",
      title: "智能客服 Agent Demo",
      category: "LLM + 确定性护栏",
      year: "2026",
      tape: "red",
      frame: "wavy",
      art: "loop",
      blurb: "电商客服场景：风险类漏网 0/8、误拦 0，应转接 11/11 正确。",
      desc: [
        "架构范式由我亲自定调：LLM 内核写好 system prompt 承担主要能力，外面架三道确定性 harness 兜底——前置规则路由 / 转人工脚本 + 七要素决策卡 / 后置违禁承诺拦截；订单查询等工具层确定性实现，不进 LLM。",
        "质量证据：20 条电商客服评测中应转接 11 条全部判断正确，风险类漏网 0/8、误拦 0；29 项测试全绿（09-09 实测）；灵敏度三档（loose / standard / strict）扫档验证。",
        "这正是企业落地 Agent 的核心工程叙事：让 LLM 做它擅长的，让确定性逻辑守住底线。",
      ],
      tags: ["Agent", "LLM 护栏", "Eval", "客服场景"],
      link: { label: "了解更多", url: "https://github.com/" },
    },
    {
      id: "luban",
      title: "LUBAN 玲珑造物",
      category: "Skill 工坊 / Meta-skill",
      year: "2026",
      tape: "yellow",
      frame: "double",
      art: "swatches",
      blurb: "把想法、文件、仓库变成结构化 Skill 的八层设计框架。",
      desc: [
        "LUBAN 是玲珑系列的造器：一个设计其他 Skill 的 meta-skill，用八层框架（元数据 / 触发 / 流程 / 上下文 / 校验 / 进化 / 门控 / 兜底）指导完整的 Skill 设计流程。",
        "玲珑系列 20+ 工程都遵循 LUBAN 规范统一命名与架构；它产出结构化数据，镜面负责渲染界面——造 Skill 和看 Skill 数据形成闭环。",
      ],
      tags: ["Skill Design", "Meta-skill", "玲珑生态"],
      link: { label: "了解更多", url: "https://github.com/" },
    },
    {
      id: "workbench",
      title: "dsh 设计工作台",
      category: "L0–L3 设计流水线",
      year: "2026",
      tape: "blue",
      frame: "arrow",
      art: "film",
      blurb: "总览 / 筛选 / 风格配方 / 构建 / 预览 / 镜鉴视觉门，一条龙。",
      desc: [
        "dsh 工作台是镜面的产品化形态：从模块注册、风格配方 sandbox，到 token、dry-run plan、build、detect 与 preview，一条 L0–L3 的完整设计流水线。",
        "裸 Node CLI 单文件零依赖即可承载完整工作台，一行命令启动；纸上手作、墨韵赛博等九套主题经注册表治理，不合格的主题无法上线。",
      ],
      tags: ["Workbench", "CLI", "Design Pipeline"],
      link: { label: "了解更多", url: "https://github.com/" },
    },
  ],

  /* 结束区域超大句子（视觉主体） */
  endSentence: "lets explore new inspiration together",

  /* 设置面板 */
  settings: {
    dotsLabel: "鼠标墨点",
    bgmLabel: "背景音乐",
    onText: "已开启",
    offText: "已关闭",
  },
};
