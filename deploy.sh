#!/bin/bash

set -e

echo "=========================================="
echo "Stock AI Assistant 部署脚本"
echo "=========================================="

if [ ! -f ".env" ]; then
    echo "错误: .env 文件不存在"
    echo "请复制 .env.example 为 .env 并填写配置"
    echo "  cp .env.example .env"
    exit 1
fi

echo ""
echo "1. 检查Docker环境..."
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo "Docker 环境检查通过"

echo ""
echo "2. 创建日志目录..."
mkdir -p logs/ai-service logs/java-backend

echo ""
echo "3. 停止旧容器..."
docker-compose down 2>/dev/null || true

echo ""
echo "4. 构建镜像..."
docker-compose build --no-cache

echo ""
echo "5. 启动服务..."
docker-compose up -d

echo ""
echo "6. 等待服务启动..."
sleep 10

echo ""
echo "7. 检查服务状态..."
docker-compose ps

echo ""
echo "8. 健康检查..."
AI_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "failed")
if [ "$AI_HEALTH" != "failed" ]; then
    echo "AI服务: 运行正常"
else
    echo "AI服务: 启动中或启动失败，请检查日志"
fi

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo ""
echo "服务地址:"
echo "  - AI服务: http://localhost:8000"
echo "  - Java后端: http://localhost:8080"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
