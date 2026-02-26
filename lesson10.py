import streamlit as st
import requests

# --- 1. 页面配置 ---
st.set_page_config(page_title="AI 创意画廊", page_icon="🎨")

# --- 2. 侧边栏：风格控制 ---
st.sidebar.header("🎨 风格调色板")
style_option = st.sidebar.selectbox(
    "请选择一种艺术风格：",
    ("无风格 (默认)", "赛博朋克 (Cyberpunk)", "吉卜力动漫 (Ghibli)", "梵高油画 (Oil Painting)",
     "3D 渲染 (Unreal Engine)")
)

# 简单的 Prompt 工程逻辑
style_suffix = ""
if "赛博朋克" in style_option:
    style_suffix = ", cyberpunk, neon lights, futuristic city"
elif "吉卜力" in style_option:
    style_suffix = ", studio ghibli style, anime, vivid colors"
elif "梵高" in style_option:
    style_suffix = ", starry night style, oil painting, thick strokes"
elif "3D" in style_option:
    style_suffix = ", 3d render, unreal engine 5, 8k, c4d"

# --- 3. 主界面 ---
st.title("🤖 AI 创意画廊")
st.markdown("输入你的灵感，AI 将为你绘制专属画作。")

# 输入框
prompt_text = st.text_area("你想画什么？", height=100, placeholder="例如：一只在太空弹吉他的猫...")
final_prompt = prompt_text + style_suffix
# --- 4. 核心逻辑 ---
if st.button("🎨 立即生成"):
    with st.spinner("正在请求后端服务..."):
        # 构造请求数据
        payload = {"text": final_prompt, "num": 1}

        try:
            # 发送请求给 FastAPI (确保 server.py 正在运行)
            response = requests.post("http://127.0.0.1:8080/draw", json=payload)

            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    st.success("后端返回成功！")
                    # 这里可以通过 st.image 展示 data["data"] (如果是URL)
                    st.write(data["data"])
                else:
                    st.error(f"后端报错：{data['message']}")
            else:
                st.error("无法连接到后端服务")

        except Exception as e:
            st.error(f"网络错误：{e}")
