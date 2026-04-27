#!/bin/bash
# Rong_AIAgent 一键部署脚本
# 用于 Openclaw 开发机 10.37.211.108

# 配置
PROJECT_DIR="/opt/Rong_TraeStart"
SERVICE_NAME="rong-agent"
PYTHON_VERSION="python3"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 打印带颜色的日志
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否是 root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_error "请使用 sudo 运行此脚本"
        exit 1
    fi
}

# 步骤 1: 环境准备
prepare_environment() {
    log_info "=== 步骤 1: 准备环境..."

    if ! command -v "$PYTHON_VERSION" &> /dev/null; then
        log_warning "$PYTHON_VERSION 未找到，尝试安装..."
        apt-get update
        apt-get install -y python3 python3-pip python3-venv -y
    fi

    if [ $? -ne 0 ]; then
        log_error "环境准备失败"
        exit 1
    fi

    log_info "环境准备完成"
}

# 步骤 2: 创建虚拟环境
setup_venv() {
    log_info "=== 步骤 2: 设置虚拟环境..."

    cd "$PROJECT_DIR" || exit 1

    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
    fi

    source venv/bin/activate
    log_info "虚拟环境已激活"
    log_info "安装依赖..."

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        pip install requests apscheduler
    fi

    log_info "虚拟环境设置完成"
}

# 步骤 3: 创建 systemd 服务
create_systemd_service() {
    log_info "=== 步骤 3: 创建 systemd 服务..."

    cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=Rong AI Agent Scheduler
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/src/scheduler/start_scheduler.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/$SERVICE_NAME.log
StandardError=append:/var/log/$SERVICE_NAME-error.log

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    log_info "systemd 服务创建完成"
}

# 步骤 4: 启动服务
start_service() {
    log_info "=== 步骤 4: 启动服务..."

    systemctl restart $SERVICE_NAME
    sleep 2

    if systemctl is-active --quiet $SERVICE_NAME; then
        log_info "服务已成功启动！"
        log_info "查看服务状态: systemctl status $SERVICE_NAME"
        log_info "查看日志: journalctl -u $SERVICE_NAME -f"
    else
        log_error "服务启动失败！"
        log_info "查看详细日志: journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
}

# 主函数
main() {
    log_info "========================================="
    log_info "🚀 Rong AI Agent 部署脚本"
    log_info "========================================="

    check_root

    prepare_environment
    setup_venv
    create_systemd_service
    start_service

    log_info ""
    log_info "🎉 部署完成！"
    log_info ""
    log_info "常用操作命令："
    log_info "  查看服务状态:  sudo systemctl status $SERVICE_NAME"
    log_info "  停止服务:      sudo systemctl stop $SERVICE_NAME"
    log_info "  启动服务:      sudo systemctl start $SERVICE_NAME"
    log_info "  重启服务:      sudo systemctl restart $SERVICE_NAME"
    log_info "  查看实时日志:  sudo journalctl -u $SERVICE_NAME -f"
}

# 运行主函数
main
