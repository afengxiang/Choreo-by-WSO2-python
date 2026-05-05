import os
import subprocess
import time
import requests
import tarfile

# 从 Choreo 环境变量读取
UUID = os.getenv("UUID", "你的默认UUID")
ARGO_TOKEN = os.getenv("ARGO_TOKEN", "")
PORT = int(os.getenv("PORT", "8080"))

def setup_binaries():
    print("正在准备系统组件...")
    # 1. 下载 sing-box (示例版本)
    sb_url = "https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz"
    r = requests.get(sb_url)
    with open("sb.tar.gz", "wb") as f:
        f.write(r.content)
    
    # 解压并重命名为伪装名称
    with tarfile.open("sb.tar.gz", "r:gz") as tar:
        for member in tar.getmembers():
            if "sing-box" in member.name and member.isfile():
                member.name = os.path.basename(member.name)
                tar.extract(member, path=".")
                os.rename("sing-box", "web_engine")
    
    # 2. 下载 cloudflared
    cf_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    r = requests.get(cf_url)
    with open("tunnel_engine", "wb") as f:
        f.write(r.content)
    
    # 赋权
    os.chmod("web_engine", 0o755)
    os.chmod("tunnel_engine", 0o755)
    print("组件准备就绪。")

def start_services():
    # 修改 config.json 中的 UUID
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            content = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
        with open("config.json", "w") as f:
            f.write(content)

    # 启动进程
    subprocess.Popen(["./web_engine", "run", "-c", "config.json"])
    subprocess.Popen(["./tunnel_engine", "tunnel", "--no-autoupdate", "run", "--token", ARGO_TOKEN])
    print("服务已在后台启动。")

# 启动 Flask 伪装网页
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "System Status: Operational"

if __name__ == "__main__":
    setup_binaries()
    start_services()
    # Choreo 需要监听环境变量中的 PORT
    app.run(host='0.0.0.0', port=PORT)
