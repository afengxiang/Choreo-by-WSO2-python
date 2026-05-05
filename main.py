import os
import subprocess
from flask import Flask

# 从 Choreo 环境变量读取
UUID = os.getenv("UUID")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

def start_services():
    print("正在启动系统组件...")
    
    # 1. 自动替换 config.json 里的 UUID
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            content = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
        with open("config.json", "w") as f:
            f.write(content)
        print("UUID 替换完成。")

    # 2. 赋予执行权限 (直传的文件通常需要这一步)
    os.system("chmod +x ./web_app ./tunnel_app")

    # 3. 启动后台进程
    print("正在开启核心引擎...")
    subprocess.Popen(["./web_app", "run", "-c", "config.json"])
    
    print("正在建立隧道连接...")
    subprocess.Popen(["./tunnel_app", "tunnel", "--no-autoupdate", "run", "--token", ARGO_TOKEN])

# 保持一个 Flask 网页运行，用于健康检查
app = Flask(__name__)

@app.route('/')
def hello():
    return "System Status: Running"

if __name__ == "__main__":
    start_services()
    print(f"Web 控制台已就绪，端口: {PORT}")
    app.run(host='0.0.0.0', port=PORT)
