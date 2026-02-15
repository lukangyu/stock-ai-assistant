# 📈 Stock AI Assistant - 个人股票分析AI助手

一款基于 AI 的个人股票分析助手，专为 A 股市场设计，提供智能分析、投资建议和邮件推送功能。

## 📋 目录

- [项目概述](#项目概述)
- [主要功能](#主要功能)
- [技术栈](#技术栈)
- [环境要求](#环境要求)
- [安装部署](#安装部署)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [联系方式](#联系方式)

---

## 项目概述

Stock AI Assistant 是一款面向个人投资者的股票分析工具，通过整合技术指标分析、新闻情绪分析和通义千问 AI 大模型，为用户提供专业、易懂的投资建议。

### 设计目标

- 🎯 **新手友好**: 所有分析结果都用大白话解释，避免专业术语
- 🤖 **AI 驱动**: 基于通义千问大模型，提供智能投资建议
- 📊 **全面分析**: 整合 50+ 技术指标、新闻情绪、市场环境
- 📧 **邮件推送**: 定时发送分析报告到邮箱
- 🔒 **安全可靠**: 本地部署，数据安全可控

---

## 主要功能

### 🔍 股票分析

- **技术指标分析**: MA、MACD、RSI、KDJ、布林带、ATR、ADX 等 50+ 指标
- **支撑位/阻力位**: 自动识别关键价格位置
- **趋势判断**: 上涨/下跌/横盘震荡趋势识别
- **买卖信号**: 基于多指标综合判断

### 📝 投资建议

- **仓位建议**: 新手友好的仓位比例建议（5%-10%）
- **分档止盈**: 10%/20%/30% 三档止盈策略
- **止损策略**: 初始止损 + 移动止损 + 强制清仓条件
- **风险提示**: 详细的风险因素列表和应对方法

### 📰 新闻分析

- **热点新闻**: 自动获取财经热点新闻
- **情绪分析**: 分析新闻对股价的影响
- **板块关联**: 识别受影响的行业板块

### 📧 邮件推送

- **定时报告**: 每日收盘后自动发送分析报告
- **HTML 邮件**: 精美的邮件模板
- **自定义配置**: 支持自定义推送时间和股票列表

---

## 技术栈

### 后端服务

| 技术 | 版本 | 说明 |
|------|------|------|
| Java | 17 | 主要开发语言 |
| Spring Boot | 3.2.0 | 后端框架 |
| Spring Mail | - | 邮件服务 |
| Thymeleaf | - | 模板引擎 |
| WebFlux | - | 响应式 HTTP 客户端 |

### AI 服务

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | AI 服务开发语言 |
| FastAPI | 0.104.0+ | Web 框架 |
| AKShare | 1.12.0+ | A 股数据源 |
| DashScope | 1.14.0+ | 通义千问 SDK |
| Pandas | 2.0.0+ | 数据处理 |
| Plotly | 5.18.0+ | 可视化图表 |

### 部署运维

| 技术 | 说明 |
|------|------|
| Docker | 容器化部署 |
| Docker Compose | 服务编排 |
| Nginx | 反向代理（可选） |

---

## 环境要求

### 开发环境

- **JDK**: 17+
- **Python**: 3.11+
- **Maven**: 3.8+
- **Node.js**: 18+ (可选，用于前端开发)

### 生产环境

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 7+)
- **内存**: 至少 2GB
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

---

## 安装部署

### 方式一：Docker 部署（推荐）

#### 1. 克隆项目

```bash
git clone https://github.com/lukangyu/stock-ai-assistant.git
cd stock-ai-assistant
```

#### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 通义千问 API 密钥（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx

# 邮件配置（必填）
MAIL_USERNAME=your_email@qq.com
MAIL_PASSWORD=your_smtp_password
RECEIVER_EMAIL=your_email@example.com
```

#### 3. 一键部署

```bash
chmod +x deploy.sh
./deploy.sh
```

#### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 方式二：本地开发

#### 1. 安装依赖

**Python AI 服务：**

```bash
cd ai-service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

**Java 后端：**

```bash
mvn clean install
```

#### 2. 配置环境

创建 `ai-service/.env` 文件：

```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx
```

#### 3. 启动服务

**启动 AI 服务：**

```bash
cd ai-service
python main.py
# 或
uvicorn main:app --host 0.0.0.0 --port 8000
```

**启动 Java 后端：**

```bash
mvn spring-boot:run
```

#### 4. 访问服务

- AI 服务: http://localhost:8000
- Java 后端: http://localhost:8080
- API 文档: http://localhost:8000/docs

---

## 使用指南

### 基本操作

#### 1. 分析单只股票

```bash
# API 请求
curl http://localhost:8000/api/analyze/stock/600519
```

#### 2. 批量分析股票

```bash
curl -X POST http://localhost:8000/api/analyze/stocks \
  -H "Content-Type: application/json" \
  -d '{"codes": ["600519", "000858", "000001"]}'
```

#### 3. 发送分析报告邮件

```bash
curl -X POST http://localhost:8080/api/report/send
```

#### 4. AI 对话

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "贵州茅台现在适合买入吗？"}'
```

### 定时任务

在 `application.yml` 中配置定时任务：

```yaml
stock:
  schedule:
    cron: "0 0 18 * * MON-FRI"  # 每个工作日 18:00
```

---

## 项目结构

```
stock-ai-assistant/
├── ai-service/                    # Python AI 服务
│   ├── services/                  # 服务模块
│   │   ├── tongyi_service.py      # 通义千问 AI 服务
│   │   ├── stock_data.py          # 股票数据服务
│   │   ├── news_service.py        # 新闻服务
│   │   ├── technical_analysis.py  # 技术分析服务
│   │   ├── feature_engineering/   # 特征工程
│   │   │   └── technical_indicators.py  # 技术指标
│   │   └── visualization/         # 可视化
│   │       └── chart_builder.py   # 图表构建
│   ├── main.py                    # FastAPI 主入口
│   ├── requirements.txt           # Python 依赖
│   └── Dockerfile                 # AI 服务镜像
│
├── src/main/java/com/personal/stock/  # Java 后端
│   ├── controller/                # 控制器
│   │   └── StockController.java
│   ├── service/                   # 服务层
│   │   ├── StockDataService.java
│   │   ├── EmailService.java
│   │   ├── DailyReportService.java
│   │   └── client/
│   │       └── PythonServiceClient.java
│   ├── dto/                       # 数据传输对象
│   │   ├── StockInfo.java
│   │   ├── StockAnalysisResult.java
│   │   └── DailyReport.java
│   └── config/                    # 配置类
│       ├── StockEmailConfig.java
│       └── PythonServiceConfig.java
│
├── src/main/resources/
│   ├── templates/                 # 邮件模板
│   │   └── alert.html
│   └── application.yml            # 应用配置
│
├── docker-compose.yml             # Docker 编排
├── Dockerfile                     # Java 后端镜像
├── nginx.conf                     # Nginx 配置
├── deploy.sh                      # 部署脚本
├── pom.xml                        # Maven 配置
└── README.md                      # 项目文档
```

---

## API 文档

### AI 服务 API (Port 8000)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/analyze/stock/{code}` | 分析单只股票 |
| POST | `/api/analyze/stocks` | 批量分析股票 |
| GET | `/api/features/technical/{code}` | 获取技术指标 |
| GET | `/api/visualization/chart/{code}` | 获取股票图表 |
| POST | `/api/chat` | AI 对话 |
| GET | `/api/news/hot` | 获取热点新闻 |
| GET | `/api/news/analyze` | 分析新闻影响 |
| GET | `/api/market/summary` | 获取市场概况 |

### Java 后端 API (Port 8080)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/report/send` | 发送每日报告 |
| GET | `/api/analyze/{code}` | 分析并发送股票报告 |

### 交互式文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 配置说明

### 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | ✅ | 通义千问 API 密钥 |
| `MAIL_USERNAME` | ✅ | 发件人邮箱 |
| `MAIL_PASSWORD` | ✅ | SMTP 授权码 |
| `RECEIVER_EMAIL` | ✅ | 收件人邮箱 |

### 获取 API 密钥

1. **通义千问 API**
   - 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
   - 开通服务并创建 API Key

2. **QQ 邮箱 SMTP**
   - 登录 QQ 邮箱 → 设置 → 账户
   - 开启 POP3/SMTP 服务
   - 生成授权码

---

## 贡献指南

### 代码规范

- **Java**: 遵循 Google Java Style Guide
- **Python**: 遵循 PEP 8 规范
- 使用有意义的变量名和函数名
- 添加必要的注释

### 提交规范

使用 Conventional Commits：

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

### PR 流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 常见问题

### Q: AI 服务启动失败？

检查 `.env` 文件中的 `DASHSCOPE_API_KEY` 是否正确配置。

### Q: 邮件发送失败？

1. 确认邮箱 SMTP 服务已开启
2. 使用授权码而非邮箱密码
3. 检查防火墙是否放行 SMTP 端口

### Q: 股票数据获取失败？

AKShare 数据源可能不稳定，建议：
1. 检查网络连接
2. 稍后重试
3. 考虑添加备用数据源

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- **作者**: Your Name
- **邮箱**: your.email@example.com
- **GitHub**: [@your-username](https://github.com/your-username)

---

## 致谢

- [AKShare](https://github.com/akfamily/akshare) - 优秀的 A 股数据接口
- [通义千问](https://tongyi.aliyun.com/) - 阿里云大语言模型
- [Spring Boot](https://spring.io/projects/spring-boot) - 强大的 Java 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
