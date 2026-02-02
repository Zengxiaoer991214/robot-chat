# 升级计划：持久化历史记录与多模态支持

为了实现类似 ChatGPT 的完整聊天体验，我将对系统进行以下升级：

## 1. 数据库与后端核心 (持久化存储)
### 新增数据模型 (`app/models`)
*   **`ChatSession` (会话表)**: 用于存储左侧的“对话列表”。
    *   字段: `title` (标题), `agent_id`, `role_id`, `created_at`, `updated_at`
*   **`ChatSessionMessage` (消息表)**: 用于存储具体的对话内容。
    *   字段: `role` (user/assistant), `content` (文本), `image_data` (图片Base64/URL), `message_type` (text/image)

### API 升级 (`app/api/chat.py`)
*   **新增接口**:
    *   `GET /api/chat/sessions`: 获取历史会话列表
    *   `GET /api/chat/sessions/{id}/messages`: 获取某个会话的详细记录
    *   `DELETE /api/chat/sessions/{id}`: 删除会话
*   **升级 `chat_completion`**:
    *   支持自动创建会话（如果未提供 `session_id`）。
    *   自动将用户发送的消息和 AI 回复保存到数据库。

## 2. 多模态与 LLM 适配器
### LLM 适配器升级 (`app/services/llm_adapter.py`)
*   **DashScope Adapter (通义千问)**:
    *   适配 `qwen-vl-max` 和 `qwen-vl-plus` 视觉模型。
    *   支持图文混合输入格式：`[{"type": "text", ...}, {"type": "image_url", ...}]`。

### Agent 配置
*   在 `AgentManagement.vue` 的模型下拉菜单中添加 VL (视觉) 模型选项。

## 3. 前端界面升级 (`Playground.vue`)
### 布局重构 (Sidebar + Chat)
*   **左侧侧边栏**: 显示历史会话列表，支持点击切换、新建对话。
*   **主聊天区**: 保持现有的流式输出和 Markdown 渲染。

### 图片上传功能
*   **输入框升级**: 添加“回形针”图标，支持选择图片。
*   **预览与发送**: 图片选择后显示缩略图，发送时自动转换为 Base64 传给后端。

---
**确认后，我将按顺序执行这些变更。**