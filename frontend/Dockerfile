# Build Stage
FROM node:18-alpine as build-stage

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .
RUN npm run build

# Production Stage
FROM nginx:stable-alpine as production-stage

# 复制构建产物到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
