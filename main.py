import os, subprocess, threading, urllib.request, tarfile
from flask import Flask

# 强制转换类型，防止 None 导致报错
UUID = str(os.getenv("UUID", ""))
ARGO_TOKEN = str(os.getenv("ARGO_TOKEN", ""))
PORT = int(os.getenv("PORT", "8080"))

def download_and_run():
    try:
        # 1. 只有文件不存在才下载
        if not os.path.exists("./web_app"):
            print("📥 后台线程：正在悄悄准备核心组件...")
            s_url = "https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz"
            urllib.request.urlretrieve(s_url, "s.tar.gz")
            with tarfile.open("s.tar.gz", "r:gz") as tar:
                for member in tar.getmembers():
                    if member.name.endswith("/sing-box") or member.name == "sing-box":
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=".")
                        os.rename("sing-box", "web_app")
            
            c_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            urllib.request.urlretrieve(c_url, "tunnel_app")
            print("✅ 后台线程：组件下载完成！")

        os.system("chmod +x ./web_app ./tunnel_app")
        
        # 2. 替换配置
        if os.path.exists("config.json") and UUID:
            with open("config.json", "r") as f:
                content = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
            with open("config.json", "w") as f:
                f.write(content)

        # 3. 启动隧道（强制 http2）
        if ARGO_TOKEN:
            print("🚀 后台线程：正在连接隧道 (http2)...")
            subprocess.Popen(["./web_app", "run", "-c", "config.json"])
            subprocess.Popen(["./tunnel_app", "tunnel", "--no-autoupdate", "--protocol", "http2", "run", "--token", ARGO_TOKEN])
            
    except Exception as e:
        print(f"❌ 后台报错: {e}")

app = Flask(__name__)

@app.route('/')
def status():
    return "2026 Choreo Service Online"

if __name__ == "__main__":
    # 核心：先开后台线程，再运行 Flask
    print("--- 科技共享 2026 终极避坑版点火 ---")
    threading.Thread(target=download_and_run, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
