import streamlit as st
import os
import requests
from db_manager import GalleryDB
import voice_manager  # 导入你的语音管家


if 'prompt_text' not in st.session_state:
    st.session_state['prompt_text'] = "一只在太空弹吉他的猫"



@st.cache_resource
def get_db():
    return GalleryDB()


db = get_db()


st.set_page_config(page_title="AI 创意画廊 Pro", page_icon="🎨", layout="wide")
st.title("🤖 AI 创意画廊 (语音 Pro 版)")

col_gen, col_hist = st.columns([1, 1])

with col_gen:
    st.subheader("🎨 创作工坊")

    # --- 布局：左边按钮，右边输入框 ---
    col_mic, col_input = st.columns([1, 5])

    with col_mic:
        st.write("")  # 占位，为了垂直对齐
        st.write("")

        if st.button("🎙️", help="点击录音5秒"):
            with st.spinner("👂 听写中..."):
                try:
                    # 1. 录音并识别
                    new_text = voice_manager.listen_smart()

                    if new_text:
                        # 2. 【关键】直接修改 Session State 的值
                        st.session_state['prompt_text'] = new_text
                        st.success("已识别")
                        # 3. 强制重跑，Streamlit 会发现 'prompt_text' 变了，从而更新输入框
                        st.rerun()
                    else:
                        st.warning("没听清")
                except Exception as e:
                    st.error(f"出错: {e}")

    with col_input:
        final_prompt = st.text_area(
            "提示词",
            height=100,
            value=st.session_state.prompt_text
        )

    # use_container_width=True 让按钮填满宽度，更好看
    if st.button("🎨 立即生成", type="primary", use_container_width=True):
        if not final_prompt:
            st.warning("提示词不能为空！")
        else:
            with st.spinner("🚀 AI 正在绘图..."):
                try:
                    # 发送给 FastAPI 后端
                    # 注意：payload 用的是 final_prompt，也就是输入框里当前的字
                    payload = {"text": final_prompt, "num": 1}

                    # 请确保本地开启了 server.py (FastAPI)
                    # 如果你的端口是 8000 请改成 8000，如果是 8080 请改成 8080
                    response = requests.post("http://127.0.0.1:8080/draw", json=payload)

                    if response.status_code == 200:
                        st.success("✨ 生成完成！")
                        st.rerun()  # 刷新显示历史记录
                    else:
                        st.error(f"生成失败: {response.text}")
                except Exception as e:
                    st.error(f"连接后端失败: {e}")


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

            # 优化显示：只显示前 20 个字
            title_text = r_prompt[:20] + "..." if len(r_prompt) > 20 else r_prompt

            with st.expander(f"🕒 {r_time[5:-3]} - {title_text}"):
                st.write(r_prompt)
                if os.path.exists(r_path):
                    st.image(r_path, use_container_width=True)
                else:
                    st.error("图片文件不存在")