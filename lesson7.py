import requests
import json
import time  # 新增：引入时间模块，用来给文件起名，防止重名

# --- 1. 配置信息 ---
# 阿里云 DashScope API 地址 (通义万相 - 视觉生成大模型)
submit_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

# 【重要】请替换为你自己的阿里云 API Key
api_key = "sk-ccbda20087af4eb5ba80769c26213425"

# --- 2. 准备身份 (Headers) ---
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

user_para = input("请输入你想要描绘的图片内容和生成数量，用|分隔")
print(user_para)
prompt , num = user_para.split('|')
# --- 3. 准备订单 (Body) ---
num = int(num)
data = {
    "model": "qwen-image-max",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ]
    },
    "parameters": {
        # 阿里云不同模型支持的尺寸不一样，这里用一个标准的正方形测试
        "size": "1664*928",
        "n": num
    }
}

print(f"🚀 正在提交绘画任务：【{prompt}】\n⏳ 请耐心等待生成 (约10-30秒)...")

# --- 4. 发送 POST 请求 ---
try:
    # 设置 60 秒超时，防止生成慢导致报错
    response = requests.post(submit_url, headers=headers, json=data, timeout=60)

    # --- 5. 处理结果 ---
    if response.status_code == 200:
        result = response.json()

        # 解析 JSON，提取图片链接
        if 'output' in result and 'choices' in result['output'] and len(result['output']['choices']) > 0:
            image_info = result['output']['choices'][0]
            # 根据通义万相的结构提取 URL
            image_url = image_info['message']['content'][0]['image']

            print("\n🎉 API 生成成功！")
            print(f"🔗 云端链接：{image_url}")
            print("-" * 30)

            # ==========================================
            # NEW: 新增下载和保存部分
            # ==========================================
            print("⬇️ 准备开始下载图片...")

            # 1. 给文件起个名
            # 使用当前时间戳，确保每次运行文件名都不一样，比如 image_170988888.jpg
            timestamp = int(time.time())
            file_name = f"ai_image_{timestamp}.jpg"

            # 2. 发起第二次请求，这次是去 GET 图片数据
            # 注意：这里不需要 headers 里的 API Key 了，因为图片链接通常是公开的
            image_resp = requests.get(image_url, timeout=30)

            if image_resp.status_code == 200:
                # 3. 核心步骤：保存文件
                # "wb" 模式：Write Binary (以二进制格式写入)
                # 图片、音频、视频等非文本文件，都必须用 wb
                with open(file_name, "wb") as f:
                    # 注意：这里写入的是 .content (二进制数据)，而不是 .text
                    f.write(image_resp.content)

                print(f"✅ 图片已成功保存到本地文件夹！")
                print(f"📁 文件名：{file_name}")
            else:
                print(f"❌ 图片下载失败，状态码：{image_resp.status_code}")
            # ==========================================

        else:
            print(f"❌ 生成失败，API返回数据结构异常：{result}")

    else:
        print(f"❌ 网络请求失败，状态码：{response.status_code}")
        print(f"错误详情：{response.text}")

except Exception as e:
    # 捕获所有可能的异常（比如断网、超时）
    print(f"💥 发生了错误：{e}")

print("\n🏁 程序结束。")