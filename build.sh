#!/bin/bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 下载并解压 sing-box
curl -L https://github.com/SagerNet/sing-box/releases/download/v1.8.5/sing-box-1.8.5-linux-amd64.tar.gz | tar xz
mv sing-box-*/sing-box web_app

# 3. 下载 cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o tunnel_app

# 4. 赋予执行权限
chmod +x web_app tunnel_app
