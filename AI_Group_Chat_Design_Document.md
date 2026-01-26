# AI 群聊系统设计文档

**版本**: 1.0  
**日期**: 2023-10-27  
**描述**: 本文档旨在指导开发一个基于 Web 的 AI 群聊系统。系统允许用户创建聊天室，设定主题，并邀请集成不同大模型（LLM）的 AI Agent 进行自主对话。

---

## 1. 系统概述

### 1.1 核心功能
*   **多模型集成**: 支持 OpenAI (GPT), Anthropic (Claude), DeepSeek, 以及本地模型 (Ollama) 等。
*   **群聊管理**: 用户可以创建房间，设定“群聊主题”和“最大发言轮数”。
*   **自主对话**: AI Agent 根据上下文和人设，自动进行多轮对话，无需人类干预，直到达到限制。
*   **实时观看**: 前端界面实时展示 AI 之间的对话内容。

### 1.2 技术栈
*   **前端**: Vue.3 + TypeScript + TailwindCSS (推荐) 或 React。
*   **后端**: Python 3.10+ (FastAPI 框架，因其异步特性适合高并发 AI 请求)。
*   **数据库**: PostgreSQL (存储房间、Agent、消息记录)。
*   **异步/队列**: Redis + Celery 或 Python `asyncio` Task (用于管理对话循环)。
*   **实时通信**: WebSocket (用于向前端推送实时消息)。

---

## 2. 系统架构设计

```mermaid
graph TD
    User[用户 (Web Frontend)] -->|HTTP/WebSocket| API_Gateway[FastAPI Backend]
    API_Gateway -->|读写| DB[(PostgreSQL)]
    API_Gateway -->|触发| Orchestrator[对话编排引擎]
    Orchestrator -->|调用| Model_Adapter[模型适配层]
    Model_Adapter -->|API Request| OpenAI[OpenAI API]
    Model_Adapter -->|API Request| Claude[Claude API]
    Model_Adapter -->|API Request| Local[Local LLM]
    Orchestrator -->|推送消息| API_Gateway
```

---

## 3. 数据库设计 (PostgreSQL)

### 3.1 ER 图概念
*   **User**: 系统用户。
*   **Agent**: AI 角色配置（人设、模型参数）。
*   **Room**: 聊天室配置（主题、状态）。
*   **RoomAgent**: 房间与 Agent 的多对多关联。
*   **Message**: 聊天记录。

### 3.2 表结构定义 (SQL)

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Agent 配置表
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,          -- 例如 "苏格拉底", "鲁迅"
    avatar_url TEXT,                     -- 头像
    provider VARCHAR(50) NOT NULL,       -- 例如 "openai", "deepseek", "ollama"
    model_name VARCHAR(100) NOT NULL,    -- 例如 "gpt-4", "llama3"
    system_prompt TEXT NOT NULL,         -- 人设 Prompt
    api_key_config TEXT,                 -- (可选) 加密存储的特定key，若为空则用系统默认
    temperature FLOAT DEFAULT 0.7
);

-- 聊天室表
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    topic TEXT NOT NULL,                 -- 群聊主题，例如 "讨论量子力学的未来"
    max_rounds INT DEFAULT 20,           -- 最大发言次数限制
    current_rounds INT DEFAULT 0,        -- 当前发言次数
    status VARCHAR(20) DEFAULT 'idle',   -- idle, running, finished
    creator_id INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 房间成员关联表 (多对多)
CREATE TABLE room_agents (
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    agent_id INT REFERENCES agents(id) ON DELETE CASCADE,
    PRIMARY KEY (room_id, agent_id)
);

-- 消息记录表
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    agent_id INT REFERENCES agents(id),  -- 若为 NULL 则代表系统消息或用户插嘴
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,           -- user, assistant, system
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. 后端设计 (Python/FastAPI)

### 4.1 核心 API 接口

| 方法 | 路径 | 描述 |
| :--- | :--- | :--- |
| POST | `/api/agents` | 创建新的 AI 角色 (设置人设、模型) |
| GET | `/api/agents` | 获取所有可用 AI 角色 |
| POST | `/api/rooms` | 创建聊天室 (设置主题、最大轮数) |
| POST | `/api/rooms/{id}/join` | 将 Agent 加入房间 |
| POST | `/api/rooms/{id}/start` | **开始群聊** (触发后台任务) |
| POST | `/api/rooms/{id}/stop` | 强制停止群聊 |
| GET | `/api/rooms/{id}/messages` | 获取历史消息 |
| WS | `/ws/rooms/{id}` | WebSocket 连接，推送实时消息 |

### 4.2 模块设计

#### A. 模型适配器模式 (Model Adapter Pattern)
用于统一不同厂商的 API 调用方式。

```python
class BaseLLMAdapter:
    async def generate(self, messages: list, system_prompt: str) -> str:
        raise NotImplementedError

class OpenAIAdapter(BaseLLMAdapter):
    async def generate(self, messages: list, system_prompt: str) -> str:
        # 调用 openai.ChatCompletion.create
        pass

class DeepSeekAdapter(BaseLLMAdapter):
    # DeepSeek 兼容 OpenAI 格式，但 Base URL 不同
    pass
```

#### B. 对话编排引擎 (Orchestrator)
这是系统的核心逻辑，负责决定“谁下一个发言”。

**逻辑流程**:
1.  **初始化**: 用户调用 `/start`，状态置为 `running`，系统发送一条 System Message 宣布主题：“本次群聊的主题是：{topic}，请大家开始讨论。”
2.  **循环 Loop**:
    *   检查 `current_rounds >= max_rounds` 或 状态 != `running` -> 退出循环，状态置为 `finished`。
    *   **选人策略**: 
        *   *简单策略*: 轮询 (Round Robin)。
        *   *智能策略*: 将当前对话历史发给一个轻量级 LLM (如 gpt-3.5)，让其判断“下一位最适合发言的是谁”。
    *   **生成回复**:
        *   获取被选中 Agent 的 `system_prompt`。
        *   获取最近 N 条 `messages` (Context Window)。
        *   调用 `Adapter.generate()`。
    *   **保存与推送**:
        *   存入 DB `messages` 表。
        *   通过 WebSocket 推送给前端。
        *   `current_rounds += 1`。
    *   **休眠**: `await asyncio.sleep(2)` (避免刷屏太快)。

---

## 5. 前端设计

### 5.1 页面规划
1.  **首页 (Dashboard)**:
    *   展示活跃房间列表。
    *   “新建房间”按钮。
    *   “Agent 管理”入口。
2.  **Agent 管理页**:
    *   表单：头像、名称、模型选择、System Prompt 编辑（例如：“你是一个暴躁的厨师...”）。
3.  **房间配置页**:
    *   输入：房间名、主题。
    *   选择器：从库中勾选 2-5 个 Agent 加入房间。
    *   设置：最大对话轮数。
4.  **聊天室详情页**:
    *   左侧：Agent 列表（高亮当前正在发言的 Agent）。
    *   中间：聊天气泡流（类似微信/Discord）。
    *   顶部：控制栏（开始、暂停、导出记录）。

### 5.2 交互细节
*   使用 WebSocket 监听 `message_received` 事件，收到新消息自动滚动到底部。
*   Markdown 渲染：AI 的回复可能包含代码块或列表，需支持 Markdown 显示。

---

## 6. 开发步骤指南

1.  **环境搭建**:
    *   安装 PostgreSQL，创建数据库 `ai_chat_db`。
    *   初始化 Python 虚拟环境，安装 `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2`, `openai`。
2.  **后端基础**:
    *   编写 SQLAlchemy Models (对应上述 DB 设计)。
    *   编写 Pydantic Schemas (API 请求/响应模型)。
    *   实现 CRUD 接口 (Agent 和 Room 的增删改查)。
3.  **核心逻辑实现**:
    *   实现 `LLMService`，封装 OpenAI 等接口调用。
    *   实现 `ChatOrchestrator`，编写后台异步循环逻辑。
4.  **前端开发**:
    *   搭建 Vue/React 脚手架。
    *   实现 Agent 创建页面。
    *   实现聊天室 WebSocket 连接。
5.  **联调与测试**:
    *   配置两个不同人设的 Agent（例如“唯物主义者” vs “唯心主义者”）。
    *   设定主题“意识的本质”，观察它们是否能自主辩论。

---

## 7. 扩展思考 (Bonus)
*   **打断机制**: 允许人类用户在 AI 聊天过程中发送消息，AI 需感知并回应。
*   **记忆压缩**: 当对话过长时，使用 LLM 总结之前的对话作为新的 Context，防止 Token 溢出。
*   **语音播报**: 集成 TTS (Text-to-Speech)，让 AI 的回复能被朗读出来。
