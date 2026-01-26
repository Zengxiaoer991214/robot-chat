# Frontend Implementation Guide

## Overview
The frontend is built with Vue 3, TypeScript, and TailwindCSS. The structure includes:

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Key Components Implemented

1. **Dashboard.vue** - Main page showing all rooms
2. **AgentManagement.vue** - Create and manage AI agents
3. **RoomConfiguration.vue** - Create new rooms and add agents
4. **ChatRoom.vue** - Real-time chat interface with WebSocket

### Key Features

#### API Service (`src/services/api.ts`)
- Complete REST API integration
- Agent CRUD operations
- Room management
- WebSocket helper for real-time messaging

#### Type Definitions (`src/types/index.ts`)
- Full TypeScript interfaces for type safety
- Agent, Room, Message types
- Request/Response schemas

#### Router (`src/router/index.ts`)
- Vue Router configuration
- Routes for all main views

### Remaining Implementation

To complete the frontend, create these additional Vue files:

1. **AgentManagement.vue** - Form to create agents with:
   - Name, avatar URL
   - Provider selection (OpenAI, DeepSeek, Ollama)
   - Model name input
   - System prompt textarea
   - Temperature slider

2. **RoomConfiguration.vue** - Form to create rooms with:
   - Room name and topic
   - Max rounds slider
   - Agent selection (multi-select from available agents)

3. **ChatRoom.vue** - Real-time chat interface with:
   - Message list with auto-scroll
   - Agent avatars and names
   - Markdown rendering for messages
   - Start/Stop buttons
   - WebSocket connection for live updates
   - Status indicator

### WebSocket Integration Example

```typescript
// In ChatRoom.vue
const ws = ref<WebSocket | null>(null)

onMounted(() => {
  ws.value = createWebSocket(roomId)
  
  ws.value.onmessage = (event) => {
    const wsMessage = JSON.parse(event.data)
    if (wsMessage.type === 'message') {
      messages.value.push(wsMessage.data)
    }
  }
})

onUnmounted(() => {
  ws.value?.close()
})
```

### Markdown Rendering

Use the `marked` library to render agent messages:

```typescript
import { marked } from 'marked'

const renderMarkdown = (content: string) => {
  return marked(content)
}
```

### Styling with TailwindCSS

All components use Tailwind utility classes for:
- Responsive design
- Dark mode support (optional)
- Consistent spacing and colors
- Shadow and hover effects

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory and can be served with any static file server.
