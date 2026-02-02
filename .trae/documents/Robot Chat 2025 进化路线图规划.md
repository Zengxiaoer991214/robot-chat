# 🚀 Robot Chat 2025 进化路线图 (Roadmap)

这份规划旨在将本项目打造为一个**全栈 AI 工程师的旗舰作品**。不仅覆盖技术深度，还兼顾产品化和变现潜力，直接对标高级 AI 工程师/全栈工程师的技能要求。

---

## 📅 Phase 1: 工程化与架构基石 (已完成/维护中)
> **目标**：打造生产级稳固地基，体现优秀的软件工程素养（这是大厂面试的敲门砖）。

- [x] **容器化部署**: Docker Compose 拆分前后端，Nginx 代理。
- [x] **CI/CD 流水线**: GitHub Actions 自动化构建与部署。
- [x] **鉴权系统**: OAuth2 + JWT 完善的用户隔离。
- [ ] **可观测性 (Observability)**: *[新]*
    - 集成 **LangFuse** 或 **LangSmith**：追踪 Token 消耗、延迟、Prompt 版本管理。（**面试加分项**：展示你懂得如何监控 AI 应用）。
    - 接入 Sentry 进行错误监控。

---

## 🧠 Phase 2: 智能内核升级 - RAG 与 记忆 (核心竞争力)
> **目标**：掌握目前最主流的 RAG 技术栈，解决 LLM "幻觉" 和 "无状态" 问题。

- [ ] **知识库 (RAG) 系统**:
    - **技术栈**: `pgvector` (利用现有的 Postgres) 或 `ChromaDB`。
    - **功能**: 用户上传 PDF/Markdown 文档，Agent 可以基于文档回答问题。
    - **进阶**: 实现 "Hybrid Search" (关键词+向量) 和 "Rerank" (重排序) 机制。
- [ ] **长期记忆 (Long-term Memory)**:
    - 实现类似 `Mem0` 的机制，自动提取用户画像（如“用户喜欢 Python”），存入数据库，下次对话自动调取。
- [ ] **工具调用 (Function Calling)**:
    - 让 Agent 拥有“手”：集成 **Google Search (Serper)** 联网搜索、**Python 代码解释器** (执行数据分析)。

---

## 🤝 Phase 3: 高级 Agent 编排 (差异化竞争)
> **目标**：跳出简单的 Chat，实现复杂的任务自动化（Agentic Workflow）。

- [ ] **工作流引擎 (Workflow Engine)**:
    - 引入 **LangGraph** 或自研简单的图编排。
    - 实现 **"Plan-and-Solve"** 模式：Agent 先生成计划，再一步步执行。
- [ ] **多 Agent 协作模式**:
    - **辩论模式**: 正反方自动辩论，裁判总结（优化现有功能）。
    - **协同开发**: 产品经理 Agent -> 程序员 Agent -> 测试 Agent 流水线。

---

## 💰 Phase 4: 产品化与变现 (SaaS 能力)
> **目标**：验证商业模式，增加被动收入潜力。

- [ ] **计费与限流**:
    - 实现 Token 消耗统计。
    - 集成 **Stripe** 或 **微信支付** (个人开发者方案)。
    - 每日免费额度 + 会员订阅制。
- [ ] **分享与传播**:
    - 允许将有趣的 Agent 或 对话记录生成 **公开链接** 分享给他人（SEO 引流）。
- [ ] **PWA / 移动端优化**:
    - 进一步打磨移动端体验，使其接近原生 App（类似现在的 Apple 风格）。

---

## 🎙️ Phase 5: 多模态与前沿交互 (趣味性)
> **目标**：增加项目的“好玩”程度，保持技术热度。

- [ ] **实时语音通话**: 集成 OpenAI Realtime API 或 "ASR + LLM + TTS" 链路，实现打电话般的体验。
- [ ] **视觉理解**: 允许上传图片，让 Agent 分析图表或识别物体。

---

## 🛠️ 技术栈升级计划

| 领域 | 当前技术 | **升级目标** | **职场竞争力价值** |
| :--- | :--- | :--- | :--- |
| **Backend** | FastAPI | **FastAPI + LangGraph** | 掌握复杂的 Agent 状态管理 |
| **DB** | PostgreSQL | **PG + pgvector** | 掌握向量数据库与 RAG |
| **LLM Ops** | Log | **LangFuse / OpenTelemetry** | 具备 AI 生产环境监控能力 |
| **Frontend** | Vue3 | **Vue3 + WebSocket深度优化** | 掌握高实时性前端交互 |

---

## 🚀 下一步建议 (Immediate Next Steps)

建议先从 **Phase 2 (RAG & 记忆)** 开始，这是目前最实用且技术含量最高的模块。

1.  **新建 `ROADMAP_2025.md`**：将此规划固化到代码仓库。
2.  **技术选型**: 确认是否直接使用 `pgvector` 扩展现有的 Postgres 数据库。
3.  **原型开发**: 实现一个简单的 "文件上传 + 向量化" 接口。