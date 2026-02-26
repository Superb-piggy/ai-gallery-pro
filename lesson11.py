import streamlit as st
from db_manager import GalleryDB
import os
import requests

# @st.cache_resource 确保数据库连接只创建一次
@st.cache_resource
def get_db():
    return GalleryDB()


db = get_db()

st.title("🖼️ AI 创意画廊 Pro")

# 分栏：左边生成，右边展示
col_gen, col_hist = st.columns([1, 1])

# --- 左侧：生成区 ---
with col_gen:
    st.subheader("🎨 创作工坊")
    prompt = st.text_input("提示词")
    if st.button("生成"):
        payload = {"text": prompt, "num": 1}
        response = requests.post("http://127.0.0.1:8080/draw", json=payload)
        if response.status_code == 200:
            st.success("生成完成！")
            st.rerun()  # 强制刷新页面

# --- 右侧：历史记录区 ---
with col_hist:
    st.subheader("📜 历史记录")

    search_txt = st.text_input("🔍 搜索")

    if search_txt:
        records = db.search_records(search_txt)
    else:
        records = db.get_all_records()

    if not records:
        st.info("暂无记录")
    else:
        for record in records:
            # 解包数据 (id, prompt, path, time)
            r_id, r_prompt, r_path, r_time = record

            with st.expander(f"{r_time} - {r_prompt[:5]}..."):
                st.write(r_prompt)
                if os.path.exists(r_path):
                    st.image(r_path)