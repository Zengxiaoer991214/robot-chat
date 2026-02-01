#!/bin/bash
set -e

# 配置变量
USERNAME="chatrobot"
KEY_COMMENT="github-actions-deploy"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
  echo "请以 root 用户运行此脚本 (使用 sudo)"
  exit 1
fi

echo "开始配置部署用户: $USERNAME"

# 1. 创建用户 (如果不存在)
if id "$USERNAME" &>/dev/null; then
    echo "✅ 用户 $USERNAME 已存在"
else
    useradd -m -s /bin/bash "$USERNAME"
    echo "✅ 用户 $USERNAME 已创建"
fi

# 2. 配置 Docker 权限
# 检查 docker 组是否存在
if getent group docker > /dev/null; then
    # 将用户添加到 docker 组，使其能运行 docker 命令而无需 sudo
    usermod -aG docker "$USERNAME"
    echo "✅ 用户 $USERNAME 已添加到 docker 组"
else
    echo "⚠️ 警告: docker 组不存在。请确保已安装 Docker。"
    echo "您可以稍后运行: sudo usermod -aG docker $USERNAME"
fi

# 3. 设置 SSH 密钥
USER_HOME="/home/$USERNAME"
SSH_DIR="$USER_HOME/.ssh"
PRIVATE_KEY="$SSH_DIR/id_ed25519"
PUBLIC_KEY="$SSH_DIR/id_ed25519.pub"

# 创建 .ssh 目录
mkdir -p "$SSH_DIR"

# 生成密钥对 (如果不存在)
if [ -f "$PRIVATE_KEY" ]; then
    echo "ℹ️ SSH 密钥对已存在，跳过生成"
else
    # 生成 ed25519 密钥，无密码
    ssh-keygen -t ed25519 -C "$KEY_COMMENT" -f "$PRIVATE_KEY" -N ""
    echo "✅ SSH 密钥对已生成"
fi

# 4. 配置授权 (Authorized Keys)
# 将公钥添加到 authorized_keys，这样拥有私钥的人(GitHub)就可以登录
cat "$PUBLIC_KEY" > "$SSH_DIR/authorized_keys"

# 5. 修复权限 (至关重要)
# SSH 对权限非常敏感
chmod 700 "$SSH_DIR"
chmod 600 "$SSH_DIR/authorized_keys"
chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"

# 确保所有文件属于 chatrobot 用户
chown -R "$USERNAME:$USERNAME" "$SSH_DIR"

echo "✅ 权限已修复"

# 6. 输出结果
echo ""
echo "======================================================================"
echo "🎉 配置成功！请执行以下步骤完成 GitHub 设置："
echo "======================================================================"
echo ""
echo "1. 复制下面的【私钥内容】到 GitHub Secrets:"
echo "   - Name:  SSH_PRIVATE_KEY"
echo "   - Value: (复制下方所有内容，包含 BEGIN 和 END 行)"
echo ""
echo "------------------- [ 复制起始行 ] -------------------"
cat "$PRIVATE_KEY"
echo "------------------- [ 复制结束行 ] -------------------"
echo ""
echo "2. 设置 GitHub Secret:"
echo "   - Name:  SERVER_USER"
echo "   - Value: $USERNAME"
echo ""
echo "3. (可选) 验证 Docker 权限:"
echo "   您可以在服务器上切换到该用户测试: su - $USERNAME -c 'docker ps'"
echo "======================================================================"
