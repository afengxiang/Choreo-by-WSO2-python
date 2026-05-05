import os, subprocess, threading, time, requests, tarfile
from flask import Flask

UUID = os.getenv("UUID")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

def download_and_run():
    # 1. 检查并下载组件 (如果本地没有)
    if not os.path.exists("./web_app"):
        print("📥 正在后台下载核心引擎...")
        # 下载 sing-box
        s_url = "https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz"
        r = requests.get(s_url); open("s.tar.gz", "wb").write(r.content)
        with tarfile.open("s.tar.gz", "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("sing-box"):
                    member.name = "web_app"
                    tar.extract(member, path=".")
        # 下载 cloudflared
        c_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        r = requests.get(c_url); open("tunnel_app", "wb").write(r.content)
        
    # 2. 准备配置并起飞
    os.system("chmod +x ./web_app ./tunnel_app")
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            content = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
        with open("config.json", "w") as f: f.write(content)

    print("🚀 核心组件已就绪，正在点火...")
    subprocess.Popen(["./web_app", "run", "-c", "config.json"])
    subprocess.Popen(["./tunnel_app", "tunnel", "--no-autoupdate", "run", "--token", ARGO_TOKEN])

app = Flask(__name__)
@app.route('/')
def status(): return "System Status: Online"

if __name__ == "__main__":
    # 在后台线程运行下载和节点启动逻辑，不阻塞 Flask
    threading.Thread(target=download_and_run, daemon=True).start()
    print(f"✅ 健康检查接口已在端口 {PORT} 开启")
    app.run(host='0.0.0.0', port=PORT)
