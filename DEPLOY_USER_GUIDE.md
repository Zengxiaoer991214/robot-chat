# 部署用户配置指南 (Setup Deploy User)

本指南将帮助您在服务器上自动创建一个权限受限的专用用户 (`chatrobot`)，并配置 SSH 密钥，以便 GitHub Actions 可以安全地进行自动部署。

## 方案优势
*   **权限隔离**：使用 `chatrobot` 而不是 `root`，降低安全风险。
*   **最小权限**：该用户仅拥有 `docker` 执行权限（属于 `docker` 用户组），无需 `sudo` 密码。
*   **自动化配置**：通过脚本一次性解决用户创建、权限设置、密钥生成等繁琐步骤，避免手动操作错误。

---

## 操作步骤

### 1. 将脚本上传到服务器
在您的本地项目根目录下，有一个名为 `setup_chatrobot.sh` 的文件。您可以打开它复制全部内容。

然后登录您的服务器（使用 root 或有 sudo 权限的用户）：
```bash
# 在服务器上创建一个新文件
nano setup_chatrobot.sh
```
*   将复制的内容**粘贴**进去。
*   按 `Ctrl+O` 保存，`Enter` 确认。
*   按 `Ctrl+X` 退出。

### 2. 运行配置脚本
在服务器上运行以下命令：

```bash
# 添加执行权限
chmod +x setup_chatrobot.sh

# 运行脚本 (必须使用 sudo 或 root)
sudo ./setup_chatrobot.sh
```

### 3. 配置 GitHub Secrets
脚本运行结束后，会在终端显示**私钥内容**和后续指引。请回到 GitHub 仓库页面：

1.  进入 **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**。
2.  **添加 `SSH_PRIVATE_KEY`**:
    *   **Name**: `SSH_PRIVATE_KEY`
    *   **Value**: 复制脚本输出的私钥内容（从 `-----BEGIN OPENSSH PRIVATE KEY-----` 到 `-----END OPENSSH PRIVATE KEY-----`，包括这两行）。
3.  **添加 `SERVER_USER`**:
    *   **Name**: `SERVER_USER`
    *   **Value**: `chatrobot`
    *(注意：如果您之前设置过 SERVER_USER 为 root，请点击 Update 更新为 chatrobot)*

---

## 验证
配置完成后，您可以手动触发一次 GitHub Action (Workflow Dispatch) 或提交代码，检查 Deploy 步骤是否成功。

如果脚本提示 `docker: command not found` 或类似错误，请确保您的服务器上已经安装了 Docker。
