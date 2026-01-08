#!/bin/bash

# ===== 配置区域 =====
REMOTE_USER="root"
REMOTE_HOST="101.126.38.65"
REMOTE_DIR="/root/tera/RealEgo"
SSH_KEY="/Users/bytedance/baiwan-key.pem"
SYNC_INTERVAL=10  # 同步间隔（秒）

# 跳板机配置
JUMP_HOST="jumpecs-hl.byted.org"  # 跳板机地址
USE_JUMP_HOST=""  # 是否使用跳板机（自动检测）

# 本地目录（脚本所在目录）
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"

LOG_FILE="${LOCAL_DIR}/sync.log"

# ===== 颜色输出 =====
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ===== 日志函数 =====
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# ===== 检查依赖 =====
check_dependencies() {
    if ! command -v rsync &> /dev/null; then
        log_error "rsync 未安装，请先安装: brew install rsync"
        exit 1
    fi
    
    if [ ! -f "$SSH_KEY" ]; then
        log_error "SSH密钥文件不存在: $SSH_KEY"
        exit 1
    fi
    
    # 检查密钥权限
    chmod 600 "$SSH_KEY" 2>/dev/null
}

# ===== 检测跳板机 =====
check_jump_host() {
    log_info "检测跳板机连通性: $JUMP_HOST"
    
    # 使用 ping 测试跳板机是否可达（发送1个包，超时3秒）
    if ping -c 1 -W 3 "$JUMP_HOST" &>/dev/null; then
        log "✓ 跳板机可达，将使用跳板机连接"
        USE_JUMP_HOST="yes"
        return 0
    else
        log_warn "跳板机不可达，将直接连接目标服务器"
        USE_JUMP_HOST="no"
        return 1
    fi
}

# ===== 测试连接 =====
test_connection() {
    log_info "测试远程服务器连接..."
    
    # 构建SSH命令选项
    local ssh_opts=""
    if [ "$USE_JUMP_HOST" = "yes" ]; then
        ssh_opts="-J $JUMP_HOST"
    fi
    
    # 构建完整命令
    local full_cmd="ssh -i \"$SSH_KEY\" -o ConnectTimeout=5 -o StrictHostKeyChecking=no $ssh_opts \"${REMOTE_USER}@${REMOTE_HOST}\" \"echo '连接成功'\""
    
    # 打印实际执行的命令
    echo ""
    echo "=========================================="
    echo "实际执行的SSH命令："
    echo "$full_cmd"
    echo "=========================================="
    echo ""
    
    # 尝试连接
    log_info "尝试连接中..."
    if [ "$USE_JUMP_HOST" = "yes" ]; then
        if ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
            -J "$JUMP_HOST" \
            "${REMOTE_USER}@${REMOTE_HOST}" "echo '连接成功'" &>/dev/null; then
            log "✓ 远程服务器连接正常（通过跳板机）"
            return 0
        else
            log_error "无法连接到远程服务器（通过跳板机）"
            return 1
        fi
    else
        if ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
            "${REMOTE_USER}@${REMOTE_HOST}" "echo '连接成功'" &>/dev/null; then
            log "✓ 远程服务器连接正常（直接连接）"
            return 0
        else
            log_error "无法连接到远程服务器（直接连接）"
            return 1
        fi
    fi
}

# ===== 同步函数 =====
sync_files() {
    local sync_start_time=$(date +%s)
    
    # 构建SSH命令选项
    local ssh_cmd="ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no"
    if [ "$USE_JUMP_HOST" = "yes" ]; then
        ssh_cmd="$ssh_cmd -J $JUMP_HOST"
    fi
    
    # 使用rsync同步
    # -a: 归档模式 (递归 + 保留权限/时间等)
    # -v: 详细输出
    # -z: 压缩
    # --delete: 删除远程有多余的文件
    
    local rsync_output="/tmp/rsync_output_$$"
    
    # 捕获输出以判断是否有更新
    # 增加过滤：
    # --exclude='.env'  : 排除环境配置文件
    # --exclude='*.log' : 排除所有日志文件
    # --exclude='server_id' : 排除可能存在的服务器标识文件
    rsync -avz --delete \
        --exclude='.git/' \
        --exclude='.DS_Store' \
        --exclude='sync.log' \
        --exclude='.sync_state' \
        --exclude='*.swp' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='node_modules/' \
        --exclude='.env' \
        --exclude='*.log' \
        --exclude='server.id' \
        --include='*/' \
        --include='*.py' \
        --include='*.js' \
        --include='*.html' \
        --include='*.css' \
        --include='*.sh' \
        --include='*.md' \
        --include='*.json' \
        --include='*.yaml' \
        --include='*.yml' \
        --include='*.txt' \
        --include='*.pem' \
        --exclude='*' \
        -e "$ssh_cmd" \
        "${LOCAL_DIR}/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/" \
        > "$rsync_output" 2>&1
    
    local rsync_status=$?
    
    if [ $rsync_status -eq 0 ]; then
        # 简单判断：过滤掉rsync的标准统计信息，看是否还有其他输出（即文件列表）
        local updates=$(grep -vE "^sending incremental file list|^sent .* bytes|^total size is|^$|^building file list" "$rsync_output")
        
        if [ -n "$updates" ]; then
             echo -e "${GREEN}✓ 同步成功${NC}"
             echo -e "${MAGENTA}变化的文件：${NC}"
             echo "$updates" | head -n 20
             if [ $(echo "$updates" | wc -l) -gt 20 ]; then
                 echo "... (更多文件)"
             fi
        else
             # 没有文件更新，仅显示简短提示，不刷屏
             echo -e "${CYAN}✓ [$(date '+%H:%M:%S')] 远程已是最新，无文件变更${NC}"
        fi
    else
        log_error "同步失败"
        cat "$rsync_output"
    fi
    
    rm -f "$rsync_output"
    return $rsync_status
}

# ===== 主循环 =====
main() {
    echo "=========================================="
    echo "  🚀 实时强力同步脚本 (RSYNC)"
    echo "=========================================="
    log_info "本地目录: ${LOCAL_DIR}"
    log_info "远程目录: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
    log_info "跳板机: ${JUMP_HOST}"
    log_info "同步间隔: ${SYNC_INTERVAL} 秒"
    log_info "同步策略: 递归比对，差异同步 (覆盖远程)"
    echo "=========================================="
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 检测跳板机
    check_jump_host
    echo ""
    
    # 测试连接
    if ! test_connection; then
        log_error "初始连接测试失败，退出"
        exit 1
    fi
    
    echo ""
    log "🎯 开始同步循环..."
    log_info "按 Ctrl+C 停止同步"
    echo ""
    
    # 循环检测和同步
    local sync_count=0
    while true; do
        sync_count=$((sync_count + 1))
        # 仅在有更新或每隔一段时间打印一次分隔符，避免日志刷屏太快
        # 这里选择简单打印
        # echo -e "\n${BLUE}[第 ${sync_count} 次检查 - $(date '+%H:%M:%S')]${NC}"
        
        sync_files
        
        sleep "$SYNC_INTERVAL"
    done
}

# ===== 信号处理 =====
cleanup() {
    echo ""
    log "收到中断信号，正在清理..."
    rm -f /tmp/rsync_output_$$ 2>/dev/null
    log "已停止同步"
    exit 0
}

trap cleanup INT TERM

# ===== 启动脚本 =====
main
