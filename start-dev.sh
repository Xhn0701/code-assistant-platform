#!/bin/bash
# 智能代码助手平台 - 开发环境启动脚本
# 使用方法: bash start-dev.sh

set -e

echo "=========================================="
echo "🚀 启动智能代码助手平台开发环境"
echo "=========================================="
echo ""

# 1. 检查Docker是否运行
echo "📋 [1/5] 检查Docker服务..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi
echo "✅ Docker服务正常"
echo ""

# 2. 启动后端服务
echo "🐳 [2/5] 启动后端服务..."
docker-compose up -d
echo ""

# 3. 等待服务健康
echo "⏳ [3/5] 等待服务启动（预计30秒）..."
sleep 10

for i in {1..6}; do
    echo "   检查中... ($i/6)"

    # 检查所有服务健康状态
    UNHEALTHY=$(docker-compose ps | grep -c "unhealthy" || true)
    STARTING=$(docker-compose ps | grep -c "starting" || true)

    if [ "$UNHEALTHY" -eq 0 ] && [ "$STARTING" -eq 0 ]; then
        echo "✅ 所有服务已就绪"
        break
    fi

    if [ $i -eq 6 ]; then
        echo "⚠️  部分服务可能未完全启动，查看详情:"
        docker-compose ps
    fi

    sleep 5
done
echo ""

# 4. 显示服务状态
echo "📊 [4/5] 服务状态:"
docker-compose ps
echo ""

# 5. 提供访问信息
echo "=========================================="
echo "✨ 启动完成！"
echo "=========================================="
echo ""
echo "📚 后端服务:"
echo "   • User Service:   http://localhost:8080"
echo "   • Agent Service:  http://localhost:8000"
echo "   • Swagger文档:    http://localhost:8080/swagger-ui/"
echo "   • API文档:        http://localhost:8000/docs"
echo ""
echo "🌐 前端开发:"
echo "   请在新终端执行:"
echo "   cd web-client"
echo "   npm run dev"
echo "   访问: http://localhost:5173"
echo ""
echo "🔍 实用命令:"
echo "   查看日志:  docker-compose logs -f [service-name]"
echo "   停止服务:  docker-compose down"
echo "   重启服务:  docker-compose restart [service-name]"
echo ""
echo "=========================================="
