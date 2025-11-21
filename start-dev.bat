chcp 65001 >nul

@echo off
REM 智能代码助手平台 - Windows开发环境启动脚本
REM 使用方法: 双击运行或在命令行执行 start-dev.bat

echo ==========================================
echo 🚀 启动智能代码助手平台开发环境
echo ==========================================
echo.

REM 1. 检查Docker
echo 📋 [1/4] 检查Docker服务...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker服务正常
echo.

REM 2. 启动后端服务
echo 🐳 [2/4] 启动后端服务...
docker-compose up -d
echo.

REM 3. 等待服务启动
echo ⏳ [3/4] 等待服务启动（30秒）...
timeout /t 30 /nobreak >nul
echo ✅ 服务启动完成
echo.

REM 4. 显示服务状态
echo 📊 [4/4] 服务状态:
docker-compose ps
echo.

echo ==========================================
echo ✨ 后端启动完成！
echo ==========================================
echo.
echo 📚 后端服务:
echo    • User Service:   http://localhost:8080
echo    • Agent Service:  http://localhost:8000
echo    • Swagger文档:    http://localhost:8080/swagger-ui/
echo    • API文档:        http://localhost:8000/docs
echo.
echo 🌐 前端开发:
echo    【请在新命令行窗口执行】
echo    cd web-client
echo    npm run dev
echo    访问: http://localhost:5173
echo.
echo 🔍 实用命令:
echo    查看日志:  docker-compose logs -f [service-name]
echo    停止服务:  docker-compose down
echo.
echo ==========================================
pause
