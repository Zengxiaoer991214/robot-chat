# AI Group Chat - Frontend

Vue 3 + TypeScript + TailwindCSS frontend for the AI Group Chat system.

## Features

- **Dashboard**: View all chat rooms with status indicators
- **Agent Management**: Create and configure AI agents with different LLM providers
- **Room Configuration**: Set up chat rooms with topics and agent selection
- **Real-time Chat**: WebSocket-powered live conversation viewing
- **Markdown Support**: Rich text rendering for AI responses
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **Vue 3**: Modern reactive framework with Composition API
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first CSS framework
- **Vite**: Fast build tool and dev server
- **Vue Router**: Client-side routing
- **Pinia**: State management
- **Axios**: HTTP client for API requests
- **Marked**: Markdown parsing and rendering

## Quick Start

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable Vue components
│   ├── views/          # Page components
│   │   ├── Dashboard.vue
│   │   ├── AgentManagement.vue
│   │   ├── RoomConfiguration.vue
│   │   └── ChatRoom.vue
│   ├── router/         # Vue Router configuration
│   ├── services/       # API and WebSocket services
│   ├── stores/         # Pinia stores
│   ├── types/          # TypeScript type definitions
│   ├── App.vue         # Root component
│   ├── main.ts         # Application entry point
│   └── style.css       # Global styles
├── index.html          # HTML template
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript config
├── vite.config.ts      # Vite config
└── tailwind.config.js  # Tailwind config
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### API Proxy

The Vite dev server is configured to proxy API requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws': {
      target: 'ws://localhost:8000',
      ws: true,
    },
  },
}
```

## Development

### Type Safety

All components use TypeScript with full type definitions:

```typescript
import type { Agent, Room, Message } from '@/types'
```

### API Integration

The `src/services/api.ts` provides type-safe API methods:

```typescript
import { agentApi, roomApi } from '@/services/api'

// Get all agents
const agents = await agentApi.getAll()

// Create a room
const room = await roomApi.create({
  name: 'Philosophy Debate',
  topic: 'What is consciousness?',
  max_rounds: 10,
  agent_ids: [1, 2]
})

// Start conversation
await roomApi.start(room.id)
```

### WebSocket Usage

```typescript
import { createWebSocket } from '@/services/api'

const ws = createWebSocket(roomId)

ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  // Handle incoming messages
}

ws.onclose = () => {
  console.log('WebSocket closed')
}
```

## Component Examples

### Dashboard Component

Shows all rooms with status indicators:

```vue
<template>
  <div v-for="room in rooms" :key="room.id">
    <h3>{{ room.name }}</h3>
    <span :class="statusClass(room.status)">
      {{ room.status }}
    </span>
  </div>
</template>
```

### Agent Form

Create agents with validation:

```vue
<template>
  <form @submit.prevent="createAgent">
    <input v-model="form.name" required />
    <select v-model="form.provider" required>
      <option value="openai">OpenAI</option>
      <option value="deepseek">DeepSeek</option>
      <option value="ollama">Ollama</option>
    </select>
    <textarea v-model="form.system_prompt" required />
    <button type="submit">Create Agent</button>
  </form>
</template>
```

### Chat Interface

Real-time message display:

```vue
<template>
  <div class="messages" ref="messageContainer">
    <div v-for="msg in messages" :key="msg.id" class="message">
      <img :src="msg.agent?.avatar_url" />
      <div v-html="renderMarkdown(msg.content)" />
    </div>
  </div>
</template>

<script setup>
import { marked } from 'marked'

const renderMarkdown = (content) => marked(content)
</script>
```

## Styling

### TailwindCSS Classes

Common patterns used:

```html
<!-- Card -->
<div class="bg-white shadow rounded-lg p-6">

<!-- Button -->
<button class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">

<!-- Input -->
<input class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">

<!-- Status Badge -->
<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
```

## Testing

```bash
# Add testing framework
npm install -D vitest @vue/test-utils

# Run tests
npm run test
```

## Deployment

### Build Output

The production build creates optimized static files:

```bash
npm run build
# Output in dist/
```

### Serve Static Files

Use any static file server:

```bash
# Using Python
python -m http.server -d dist 8080

# Using serve
npx serve -s dist -p 8080
```

### Deploy to Nginx

```nginx
server {
    listen 80;
    server_name example.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

[Your License]
