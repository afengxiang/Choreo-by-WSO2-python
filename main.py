import os, subprocess, threading, time, urllib.request, tarfile
from flask import Flask

UUID = os.getenv("UUID")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

def download_and_run():
    try:
        if not os.path.exists("./web_app"):
            print("📥 检测到组件缺失，开始从标准库通道下载...")
            
            # 下载 sing-box (使用标准库 urllib)
            s_url = "https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz"
            urllib.request.urlretrieve(s_url, "s.tar.gz")
            with tarfile.open("s.tar.gz", "r:gz") as tar:
                for member in tar.getmembers():
                    if member.name.endswith("sing-box"):
                        member.name = "web_app"
                        tar.extract(member, path=".")
            
            # 下载 cloudflared
            c_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            urllib.request.urlretrieve(c_url, "tunnel_app")
            
            print("✅ 下载完成，准备启动...")

        os.system("chmod +x ./web_app ./tunnel_app")
        
        # 替换 UUID
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                c = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
            with open("config.json", "w") as f: f.write(c)

        subprocess.Popen(["./web_app", "run", "-c", "config.json"])
        subprocess.Popen(["./tunnel_app", "tunnel", "--no-autoupdate", "run", "--token", ARGO_TOKEN])
        print("🚀 节点已在后台点火！")
        
    except Exception as e:
        print(f"❌ 运行中发生错误: {e}")

app = Flask(__name__)
@app.route('/')
def status(): return "Operational"

if __name__ == "__main__":
    # 这里的打印信息会出现在 Application Logs 里
    print(f"--- 科技共享调试模式开启 ---")
    print(f"端口: {PORT} | 正在启动健康检查接口...")
    
    threading.Thread(target=download_and_run, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
