# =============================================================================
# Gunicorn 配置文件 — 云水禅心后端服务
# 项目路径: /var/www/zenfortune/backend
# 使用方式: gunicorn -c deploy/gunicorn.conf.py main:app
# =============================================================================

import multiprocessing

# ── 绑定地址 ──────────────────────────────────────────────────────────────────
# 监听本地 9000 端口，由 Nginx 反向代理对外暴露
bind = "127.0.0.1:9000"

# ── Worker 配置 ───────────────────────────────────────────────────────────────
# 使用 UvicornWorker 以支持 FastAPI 的异步特性
worker_class = "uvicorn.workers.UvicornWorker"

# Worker 数量：推荐值为 CPU 核心数 × 2 + 1，此处固定为 4
workers = 4

# 每个 Worker 的线程数（UvicornWorker 为异步模式，线程数保持 1 即可）
threads = 1

# ── 超时配置 ──────────────────────────────────────────────────────────────────
# Worker 超时时间（秒）。AI 分析接口耗时较长，设为 120 秒
timeout = 120

# 优雅关闭超时时间（秒）
graceful_timeout = 30

# Keep-Alive 连接保持时间（秒）
keepalive = 5

# ── 日志配置 ──────────────────────────────────────────────────────────────────
# 访问日志路径（- 表示输出到 stdout，由 systemd 接管）
accesslog = "-"

# 错误日志路径
errorlog = "-"

# 日志级别：debug / info / warning / error / critical
loglevel = "info"

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# ── 进程配置 ──────────────────────────────────────────────────────────────────
# PID 文件路径
pidfile = "/var/www/zenfortune/backend/gunicorn.pid"

# 是否以守护进程运行（systemd 管理时设为 False）
daemon = False

# ── 性能调优 ──────────────────────────────────────────────────────────────────
# 最大并发连接数
worker_connections = 1000

# 请求最大数量，超过后 Worker 自动重启（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 预加载应用（节省内存，但不兼容某些异步框架的 lifespan，如有问题可设为 False）
preload_app = False
