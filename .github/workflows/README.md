# GitHub Actions CI/CD 配置指南

本项目的 CI/CD 使用 GitHub Actions 实现，包含以下工作流：

## 工作流说明

### 1. CI 工作流 (`ci.yml`)

**触发条件：**
- 推送到 `main` 或 `develop` 分支
- Pull Request 到 `main` 分支

**执行内容：**
- Java 后端编译和测试
- Python AI 服务依赖安装和检查
- Docker 镜像构建和推送（仅 main 分支）

### 2. 部署工作流 (`deploy.yml`)

**触发条件：**
- 手动触发（workflow_dispatch）

**执行内容：**
- SSH 连接到服务器
- 拉取最新代码
- 重启 Docker 容器
- 健康检查

### 3. 定时任务工作流 (`scheduled.yml`)

**触发条件：**
- 每个工作日 18:00 (UTC+8 10:00)
- 手动触发

**执行内容：**
- 运行股票分析
- 发送邮件通知

---

## 必需的 GitHub Secrets 配置

在 GitHub 仓库的 `Settings` -> `Secrets and variables` -> `Actions` 中配置以下密钥：

### Docker Hub 配置（用于推送镜像）

| Secret 名称 | 说明 |
|------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码或 Access Token |

### 服务器配置（用于部署）

| Secret 名称 | 说明 |
|------------|------|
| `SERVER_HOST` | 服务器 IP 地址或域名 |
| `SERVER_USER` | SSH 用户名 |
| `SERVER_PORT` | SSH 端口（默认 22） |
| `SSH_PRIVATE_KEY` | SSH 私钥 |
| `DEPLOY_PATH` | 服务器上的项目路径 |

### 应用配置

| Secret 名称 | 说明 |
|------------|------|
| `DASHSCOPE_API_KEY` | 通义千问 API 密钥 |
| `MAIL_USERNAME` | 发件人邮箱 |
| `MAIL_PASSWORD` | SMTP 授权码 |
| `RECEIVER_EMAIL` | 收件人邮箱 |

---

## 配置步骤

### 1. 配置 Docker Hub

1. 注册 [Docker Hub](https://hub.docker.com/) 账号
2. 创建 Access Token：Account Settings -> Security -> New Access Token
3. 在 GitHub Secrets 中添加 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD`

### 2. 配置服务器 SSH

```bash
# 在本地生成 SSH 密钥（如果没有）
ssh-keygen -t ed25519 -C "github-actions" -f github-actions-key

# 将公钥添加到服务器
ssh-copy-id -i github-actions-key.pub user@your-server

# 将私钥内容添加到 GitHub Secrets (SSH_PRIVATE_KEY)
cat github-actions-key
```

### 3. 配置服务器环境

在服务器上执行：

```bash
# 克隆项目
git clone https://github.com/lukangyu/stock-ai-assistant.git
cd stock-ai-assistant

# 创建 .env 文件
cp .env.example .env
nano .env  # 填写配置

# 创建日志目录
mkdir -p logs/ai-service logs/java-backend
```

### 4. 测试部署

1. 在 GitHub 仓库页面，点击 `Actions`
2. 选择 `Deploy` 工作流
3. 点击 `Run workflow`
4. 选择环境（production/staging）
5. 点击 `Run workflow` 按钮

---

## 工作流状态徽章

在 README.md 中添加徽章：

```markdown
[![CI](https://github.com/lukangyu/stock-ai-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/lukangyu/stock-ai-assistant/actions/workflows/ci.yml)
[![Deploy](https://github.com/lukangyu/stock-ai-assistant/actions/workflows/deploy.yml/badge.svg)](https://github.com/lukangyu/stock-ai-assistant/actions/workflows/deploy.yml)
```

---

## 常见问题

### Q: Docker 推送失败？

检查 Docker Hub 密码是否正确，建议使用 Access Token 而非密码。

### Q: SSH 连接失败？

1. 确认服务器防火墙放行 SSH 端口
2. 检查 SSH 私钥格式（需要完整包含 BEGIN 和 END 行）
3. 确认服务器用户有 sudo 权限

### Q: 健康检查失败？

1. 检查服务是否正常启动
2. 确认端口 8000 和 8080 已开放
3. 查看 Docker 日志：`docker-compose logs`
