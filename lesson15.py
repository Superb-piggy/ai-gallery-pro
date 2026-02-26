import streamlit as st
import os
import requests
from db_manager import GalleryDB
import voice_manager
from llm_manager import LocalBrain

# 1. 初始化 Session State
if 'prompt_text' not in st.session_state:
    st.session_state['prompt_text'] = ""


# 2. 缓存资源
@st.cache_resource
def get_manager():
    return GalleryDB(), LocalBrain()


db, llm = get_manager()

st.set_page_config(page_title="AI 创意画廊 Pro", page_icon="🎨", layout="wide")
st.title("🤖 AI 创意画廊 (语音 Pro 版)")

col_gen, col_hist = st.columns([1, 1])

# === 左侧：生成区 ===
with col_gen:
    st.subheader("🎨 创作工坊")

    col_mic, col_input = st.columns([1, 5])

    # --- 麦克风部分 (逻辑没问题) ---
    with col_mic:
        st.write("")
        st.write("")
        if st.button("🎙️", help="点击录音"):
            with st.spinner("👂 听写中..."):
                try:
                    new_text = voice_manager.listen_smart()
                    if new_text:
                        st.session_state['prompt_text'] = new_text
                        st.success("已识别")
                        st.rerun()
                    else:
                        st.warning("没听清")
                except Exception as e:
                    st.error(f"出错: {e}")

    with col_input:
        prompt_input = st.text_area(
            "提示词",
            height=100,
            value=st.session_state['prompt_text']
        )

    # --- 按钮区域 (修复点 2：拆分功能) ---
    col_btn1, col_btn2 = st.columns([1, 1])

    # 按钮 A：AI 润色 (解决死循环问题，改为点击触发)
    with col_btn1:
        if st.button("✨ AI 润色提示词", use_container_width=True):
            if not prompt_input:
                st.warning("请先输入一些关键词")
            else:
                with st.status("🧠 本地大脑正在思考...", expanded=True) as status:
                    st.write("正在构建 Prompt 模板...")
                    # 定义 Prompt 模板
                    system_prompt = f"""
Role: You are a professional Image Prompt Engineer and Art Director. Your goal is to convert simple user descriptions into high-quality, detailed text-to-image prompts optimized for AI generation.
Instruction:
1. Analyze the user's input to understand the core subject and intent.
2. Expand the description using the "Universal Formula":
[Subject Description] + [Environment/Context] + [Art Style/Medium] + [Lighting/Atmosphere] + [Color Palette] + [Composition/Camera Angle] + [Quality Modifiers]
3. Translate everything into English if the input is in another language.
4. Output ONLY the optimized English prompt, nothing else.
Guidelines for Expansion:
- Subject: Add details about appearance, clothing, pose, and expression.
- Art Style: Specify if it's photography, 3D render (Octane render, Unreal Engine 5), oil painting, anime (Studio Ghibli), etc.
- Lighting: Use terms like volumetric lighting, cinematic lighting, golden hour, soft studio light, bioluminescence.
- Quality: Add keywords like 8k resolution, highly detailed, masterpiece, sharp focus, trending on ArtStation.
Example:
Input: "A cat in the rain"
Output: A close-up shot of a fluffy ginger cat sitting on a wet cobblestone street, rain falling heavily, reflection in puddles, cinematic lighting, cyberpunk neon lights in the background, blue and orange color grade, realistic photography, 8k, highly detailed, sharp focus.
User Input: {prompt_input}
"""
                    st.write("正在推理...")
                    # 调用 LLM
                    think, content = llm.chat_with_thinking(system_prompt)

                    # 展示思考过程
                    with st.expander("👀 查看思考过程"):
                        st.write(think)

                    # 更新状态
                    st.session_state['prompt_text'] = content
                    status.update(label="润色完成！", state="complete", expanded=False)
                    st.rerun()  # 刷新以在输入框显示新文字

    # 按钮 B：生成图片
    with col_btn2:
        if st.button("🎨 立即生成", type="primary", use_container_width=True):
            if not prompt_input:
                st.warning("提示词不能为空！")
            else:
                with st.spinner("🚀 AI 正在绘图..."):
                    try:
                        # 发送给 FastAPI 后端
                        payload = {"text": prompt_input, "num": 1}
                        response = requests.post("http://127.0.0.1:8080/draw", json=payload)

                        if response.status_code == 200:
                            st.success("✨ 生成完成！")
                            st.rerun()
                        else:
                            st.error(f"生成失败: {response.text}")
                    except Exception as e:
                        st.error(f"连接后端失败: {e}")

# === 右侧：历史记录 (保持不变) ===
with col_hist:
    st.subheader("📜 历史记录")
    search_txt = st.text_input("🔍 搜索历史记录")
    if search_txt:
        records = db.search_records(search_txt)
    else:
        records = db.get_all_records()

    if not records:
        st.info("暂无记录")
    else:
        for record in records:
            r_id, r_prompt, r_path, r_time = record
            # 截断显示
            display_text = r_prompt[:30] + "..." if len(r_prompt) > 30 else r_prompt
            with st.expander(f"🕒 {r_time[5:-3]} - {display_text}"):
                st.write(r_prompt)
                if os.path.exists(r_path):
                    st.image(r_path, use_container_width=True)
                else:
                    st.error("图片文件不存在")