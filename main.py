import os, subprocess, threading, urllib.request, tarfile, shutil
from flask import Flask

# 获取环境变量
UUID = os.getenv("UUID")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

def download_and_run():
    try:
        if not os.path.exists("./web_app"):
            print("📥 正在从官方镜像拉取核心引擎...")
            
            # 1. 下载并提取 sing-box (处理嵌套文件夹)
            s_url = "https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz"
            urllib.request.urlretrieve(s_url, "s.tar.gz")
            with tarfile.open("s.tar.gz", "r:gz") as tar:
                for member in tar.getmembers():
                    if member.name.endswith("/sing-box") or member.name == "sing-box":
                        # 重点：打破文件夹限制，直接提取到当前目录并改名
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=".")
                        os.rename("sing-box", "web_app")
                        print("✅ sing-box 提取成功")

            # 2. 下载 cloudflared
            c_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            urllib.request.urlretrieve(c_url, "tunnel_app")
            print("✅ cloudflared 下载成功")

        # 3. 授权并启动
        os.system("chmod +x ./web_app ./tunnel_app")
        
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                c = f.read().replace("PASTE_YOUR_UUID_HERE", UUID)
            with open("config.json", "w") as f: f.write(c)

        print("🚀 节点已在后台点火，正在连接隧道...")
        subprocess.Popen(["./web_app", "run", "-c", "config.json"])
        subprocess.Popen(["./tunnel_app", "tunnel", "--no-autoupdate", "run", "--token", ARGO_TOKEN])
        
    except Exception as e:
        print(f"❌ 运行中发生错误: {e}")

app = Flask(__name__)
@app.route('/')
def status(): return "System Status: Online"

if __name__ == "__main__":
    print(f"--- 科技共享 2026 特供版启动 ---")
    print(f"监听端口: {PORT}")
    
    # 启动后台任务
    threading.Thread(target=download_and_run, daemon=True).start()
    
    # 立即启动 Web 服务响应 Choreo 健康检查
    app.run(host='0.0.0.0', port=PORT)
