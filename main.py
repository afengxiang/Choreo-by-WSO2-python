import os, subprocess, threading, urllib.request, tarfile
from flask import Flask

# 环境变量读取
UUID = os.getenv("UUID")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

def download_and_run():
    try:
        if not os.path.exists("./web_app"):
            print("📥 正在后台准备核心组件...")
            
            # 1. 下载并提取 sing-box (精准处理嵌套目录)
            s_url = "https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz"
            urllib.request.urlretrieve(s_url, "s.tar.gz")
            with tarfile.open("s.tar.gz", "r:gz") as tar:
                for member in tar.getmembers():
                    # 只要是名为 sing-box 的文件，不管在哪层文件夹，都抓出来改名
                    if member.name.endswith("/sing-box") or member.name == "sing-box":
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=".")
                        os.rename("sing-box", "web_app")
            
            # 2. 下载 cloudflared
            c_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            urllib.request.urlretrieve(c_url, "tunnel_app")
            print("✅ 组件准备就绪")

        # 3. 授权并起飞
        os.system("chmod +x ./web_app ./tunnel_app")
        
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                c = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
            with open("config.json", "w") as f: f.write(c)

        print("🚀 正在点火连接隧道...")
        subprocess.Popen(["./web_app", "run", "-c", "config.json"])
        subprocess.Popen(["./tunnel_app", "tunnel", "--no-autoupdate", "--protocol", "http2", "run", "--token", ARGO_TOKEN])
        
    except Exception as e:
        print(f"❌ 运行报错: {e}")

app = Flask(__name__)
@app.route('/')
def status(): return "System Online"

if __name__ == "__main__":
    print(f"--- 科技共享 2026 避坑版启动 ---")
    # 异步下载，防止 Choreo 健康检查超时
    threading.Thread(target=download_and_run, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
