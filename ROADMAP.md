# Robot Chat 产品演进路线图 (Roadmap)

本文档旨在规划 **Robot Chat** 项目的中长期发展方向，从基础架构完善到智能内核升级，最终实现多模态交互与生态开放。

> **状态说明**:
> - [ ] 待开始
> - [x] 已完成
> - [~] 进行中

---

## 🏁 Phase 1: 基础稳固与身份体系 (Foundation & Identity) - [短期 Q2 2026]
**核心目标**: 从“演示级 Demo”升级为“生产级应用”，确保数据安全与多用户隔离。

### 1.1 🔐 用户鉴权系统 (Authentication)
- [ ] **用户注册与登录**: 实现 `/register` 和 `/login` 接口，支持用户名/密码注册。
- [ ] **密码安全**: 使用 `bcrypt` 对用户密码进行哈希存储，杜绝明文保存。
- [ ] **JWT 鉴权**: 引入 JWT (JSON Web Token) 机制，保护后端 API 接口。
- [ ] **数据隔离**: 确保用户只能查看和管理属于自己的 Agent、聊天室和对话记录。

### 1.2 🛠️ 工程化完善
- [ ] **数据库迁移 (Migration)**: 引入 `Alembic` 管理数据库结构变更，替代手动 SQL 脚本。
- [ ] **Docker 编排优化**: 完善 `docker-compose.yml`，实现一键拉起 PostgreSQL + Backend + Frontend 环境。
- [ ] **配置管理**: 优化环境变量 (`.env`) 管理，区分开发、测试和生产环境配置。

### 1.3 ⚡ 基础体验优化
- [ ] **WebSocket 稳定性**: 增加心跳检测 (Heartbeat) 和断线自动重连机制。
- [ ] **消息状态同步**: 实现消息的“发送中”、“已发送”、“已读”状态同步。
- [ ] **移动端适配优化**: 进一步打磨移动端交互细节（如键盘弹出时的布局调整）。

---

## 🧠 Phase 2: 智能内核升级 (Intelligence & Memory) - [中短期 Q3 2026]
**核心目标**: 让 Agent 拥有“记忆”和“手脚”，不再是健忘的纯聊天机器人。

### 2.1 📚 RAG 与长期记忆 (Long-term Memory)
- [ ] **向量数据库集成**: 引入 **PGVector** (PostgreSQL 插件) 或 **ChromaDB** 存储向量数据。
- [ ] **Embeddings 生成**: 集成 OpenAI `text-embedding-3` 或本地模型生成文本向量。
- [ ] **自动记忆**: 实现对话内容的自动摘要与向量化存储，Agent 能回忆起历史对话细节。
- [ ] **知识库构建**: 支持用户上传 PDF/Markdown 文档，Agent 可基于文档内容回答问题 (RAG)。

### 2.2 🧰 工具调用 (Function Calling / Tool Use)
- [ ] **Tool Use 协议**: 实现标准的工具调用接口 (兼容 OpenAI Function Calling 格式)。
- [ ] **联网搜索 (Web Search)**: 集成 Google/Bing Search API，让 Agent 能获取实时新闻。
- [ ] **代码执行 (Code Interpreter)**: 允许 Agent 编写并执行 Python 代码，进行数学计算或数据分析。
- [ ] **时间感知**: 让 Agent 获取当前准确时间，能处理“明天提醒我”之类的请求。

---

## 👁️ Phase 3: 多模态交互 (Multimodal Experience) - [中期 Q3-Q4 2026]
**核心目标**: 突破纯文本限制，通过视觉与听觉提升沉浸感。

### 3.1 🖼️ 视觉能力 (Vision)
- [ ] **图片发送**: 支持用户在聊天框发送图片文件。
- [ ] **视觉理解**: 接入 GPT-4o / Claude-3.5 Vision 模型，让 Agent 能“看懂”图片内容。
- [ ] **图片生成**: Agent 可调用 DALL-E 3 或 Stable Diffusion API 生成配图。

### 3.2 🎙️ 语音对话 (Voice)
- [ ] **语音输入 (STT)**: 前端集成 Web Speech API 或 Whisper 模型，实现语音转文字输入。
- [ ] **语音合成 (TTS)**: 后端集成 TTS 服务，为不同角色配置独特声线 (如萝莉音、大叔音、新闻播报腔)。
- [ ] **实时通话模式**: 实现类似电话的实时双工语音对话界面。

---

## 🌍 Phase 4: 社区与生态 (Ecosystem) - [长期 2027+]
**核心目标**: 打造平台化能力，促进内容分享。

### 4.1 🏪 Agent 市场 (Marketplace)
- [ ] **Agent 分享**: 用户可以将自己调教好的 Agent (Prompt + 参数) 发布到公共市场。
- [ ] **社区互动**: 支持对公开 Agent 进行点赞、收藏和评论。
- [ ] **一键克隆**: 用户可将市场中的热门 Agent 一键复制到自己的工作区。

### 4.2 🔌 插件系统 (Plugin System)
- [ ] **插件标准**: 定义简单的 Python 插件接口。
- [ ] **开发者模式**: 允许高级用户编写自定义脚本挂载到 Agent 上，扩展其能力。
- [ ] **API 开放平台**: 提供标准 RESTful API，允许第三方应用接入 Robot Chat 系统。
