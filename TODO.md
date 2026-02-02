# 当前任务清单 (To-Do List)

> 本文档用于跟踪短期内的具体开发任务，源自 `ROADMAP.md` 的规划。

## 🚀 Priority 1: RAG 知识库系统 (Phase 2)
> 目标：让 Agent 能够基于上传的文档回答问题。

- [ ] **技术调研与选型**
    - [ ] 确认 PostgreSQL 版本是否支持 `pgvector` (目前使用 `postgres:17-alpine`，需确认是否包含或需要更换镜像)。
    - [ ] 调研 Python 端的向量库客户端 (SQLAlchemy 扩展 vs 独立库)。
- [ ] **后端开发**
    - [ ] 数据库迁移：添加 `files` 表 (存储文件元数据) 和 `embeddings` 表 (存储向量)。
    - [ ] API 接口：实现 `/api/files/upload` (上传 PDF/TXT)。
    - [ ] 后台任务：实现文件解析 (LangChain/LlamaIndex) + 向量化 (OpenAI Embedding) + 存入 PG。
    - [ ] 检索逻辑：在 `chat.py` 中增加上下文检索逻辑 (Similarity Search)。
- [ ] **前端开发**
    - [ ] 知识库管理界面：上传文件列表、删除文件。
    - [ ] 聊天设置：选择开启/关闭“关联知识库”。

## 🚀 Priority 2: 可观测性集成 (Phase 3)
> 目标：看清楚 Agent 到底在想什么，消耗了多少 Token。

- [ ] **LangFuse 集成**
    - [ ] 注册 LangFuse (Cloud 或本地部署)。
    - [ ] 后端集成 `langfuse-python` SDK。
    - [ ] 装饰器覆盖核心 Chat 接口，记录 Trace。

## 🐛 已知待优化项
- [ ] **移动端体验**: 虽然 UI 已优化，但输入框在部分安卓机型上可能遮挡内容。
- [ ] **代理配置**: 确认生产环境 Docker 容器内的代理配置在所有场景下生效。
