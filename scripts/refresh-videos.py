#!/usr/bin/env python3
"""
自动刷新飞书视频/图片临时链接
每 20 小时运行一次，推送到 GitHub
"""

import json
import os
import subprocess
import time
from datetime import datetime

# 飞书应用凭据
APP_ID = "cli_a95e5f9bf2785cce"
APP_SECRET = "oiHkkTg9r8CgqrcrMZG9bbhmZVZGjZkh"

# GitHub 配置
GH_USER = "XingZengJi"
REPO_NAME = "zuopinji"
PROJECT_DIR = "/Users/xingzengji/Documents/Code/zhiboxx/portfolio"

# 所有需要刷新链接的 file_token（从飞书表格提取）
ALL_TOKENS = [
    "TeNwbothNoPl0xxvsIocCcRqnoe",  # 视频封面
    "AAQ9bUMxQogyx2x0t48chPqtnKb", # 图片封面
    "ZbWIbQJ8FonY2kxVPVXcFbqrnZc", # 视频
    "BoFjbHYGLocw3wxFqHPc4HRAnMg",  # 图片
]

def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    import urllib.request
    import urllib.parse

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode('utf-8')

    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    if result.get("code") != 0:
        raise Exception(f"获取 token 失败: {result}")

    return result["tenant_access_token"]


def get_tmp_url(token, access_token):
    """获取单个临时下载链接"""
    import urllib.request
    import urllib.parse

    url = f"https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url?file_tokens={token}"

    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {access_token}')

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    data = result.get("data", {}).get("tmp_download_urls", [])
    if data:
        return data[0]
    return None


def refresh_all_links():
    """刷新所有链接"""
    print(f"[{datetime.now()}] 开始刷新链接...")

    access_token = get_tenant_access_token()
    print(f"  获取到 token: {access_token[:20]}...")

    all_results = []

    # 逐个获取（飞书批量接口有时不稳定）
    for i, token in enumerate(ALL_TOKENS):
        print(f"  处理 {i+1}/{len(ALL_TOKENS)}: {token}")

        result = get_tmp_url(token, access_token)
        if result:
            all_results.append(result)
        else:
            print(f"    警告: 获取 {token} 失败")

        time.sleep(0.5)  # 避免请求过快

    print(f"  获取到 {len(all_results)} 个链接")

    # 写入 videos.json
    videos_data = [
        {"token": r["file_token"], "url": r["tmp_download_url"]}
        for r in all_results
    ]

    videos_path = os.path.join(PROJECT_DIR, "api", "videos.json")
    with open(videos_path, "w") as f:
        json.dump(videos_data, f, indent=2)

    print(f"  写入 {len(videos_data)} 个链接到 videos.json")

    # Git 提交并推送
    os.chdir(PROJECT_DIR)

    subprocess.run(["git", "add", "api/videos.json"], check=True)
    result = subprocess.run(["git", "commit", "-m", f"refresh: 更新视频链接 {datetime.now().strftime('%Y-%m-%d %H:%M')}"], capture_output=True)

    if result.returncode != 0:
        if b"nothing to commit" not in result.stderr:
            print(f"  提交失败: {result.stderr.decode()}")
            return
        else:
            print("  没有新链接需要提交")

    subprocess.run(["git", "push", "origin", "main"], check=True)

    print(f"  已推送到 GitHub")
    print(f"[{datetime.now()}] 完成！")


if __name__ == "__main__":
    try:
        refresh_all_links()
    except Exception as e:
        print(f"错误: {e}")
        # 写入错误日志
        log_path = os.path.expanduser("~/.logs/refresh-videos.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now()}] 错误: {e}\n")
