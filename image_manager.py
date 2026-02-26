import os
import base64
import mimetypes
import dashscope
import requests
import time
from db_manager import GalleryDB
from dashscope import MultiModalConversation
from test.config import API_KEY
from watermark_manager import embed_invisible_watermark

dashscope.api_key = API_KEY
db = GalleryDB()

# ============================================================
# 水印配置（按需修改）
# ============================================================
WATERMARK_TEXT = "AI GALLERY PRO"   # 水印文字（仅支持英文）
WATERMARK_ALPHA = 20                 # 嵌入强度：20~40 为推荐范围
# ============================================================


def generate_and_save(text, num=1):
    print(f"⚙️ [后台] 收到任务：'{text}'，数量：{num}")

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": "qwen-image-max",
        "input": {
            "messages": [{"role": "user", "content": [{"text": text}]}]
        },
        "parameters": {"size": "1664*928", "n": num}
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)

        if resp.status_code == 200:
            result = resp.json()
            if 'output' in result and 'choices' in result['output']:
                img_url = result['output']['choices'][0]['message']['content'][0]['image']

                # 下载保存
                save_name = f"draw_{int(time.time())}.jpg"
                img_data = requests.get(img_url).content
                with open(save_name, "wb") as f:
                    f.write(img_data)
                print(f"✅ 图片已下载：{save_name}")

                # ---- 新增：嵌入隐形水印（原地覆盖） ----
                try:
                    embed_invisible_watermark(
                        input_path=save_name,
                        text=WATERMARK_TEXT,
                        output_path=save_name,
                        alpha=WATERMARK_ALPHA
                    )
                except Exception as wm_err:
                    print(f"⚠️ 水印嵌入失败（不影响保存）：{wm_err}")
                # ----------------------------------------

                print("图片保存成功，开始写入数据库...")
                db.add_record(text, save_name)

                return f"成功！图片已保存为 {save_name}"
            else:
                return "失败：API 返回结构异常"
        else:
            return f"失败：状态码 {resp.status_code}"

    except Exception as e:
        return f"出错：{str(e)}"


def encode_image_to_base64(file_path):
    """
    辅助函数：将本地图片文件转换为 Base64 编码字符串
    这是 qwen-image-edit 模型接收本地图片的要求格式
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件: {file_path}")

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"

    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"❌ 图片转码失败: {e}")
        return None


def save_uploaded_file(uploaded_file):
    """保存 Streamlit 上传的文件到本地"""
    try:
        temp_filename = "temp_ref_image.png"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.abspath(temp_filename)
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return None


def generate_image_with_ref(prompt, ref_image_path):
    """
    使用 qwen-image-edit-max 进行图生图/图像编辑
    """
    print(f"🚀 正在调用 Qwen-Image-Edit...")
    print(f"📄 参考图: {ref_image_path}")

    base64_image = encode_image_to_base64(ref_image_path)
    if not base64_image:
        return None

    messages = [
        {
            "role": "user",
            "content": [
                {"image": base64_image},
                {"text": prompt}
            ]
        }
    ]

    try:
        response = MultiModalConversation.call(
            api_key=dashscope.api_key,
            model="qwen-image-edit-max",
            messages=messages,
            stream=False,
            n=1,
            size="1024*1024",
            prompt_extend=True
        )

        if response.status_code == 200:
            content_list = response.output.choices[0].message.content

            img_url = None
            for item in content_list:
                if 'image' in item:
                    img_url = item['image']
                    break

            if img_url:
                # 下载保存
                save_name = f"draw_{int(time.time())}.jpg"
                img_data = requests.get(img_url).content
                with open(save_name, "wb") as f:
                    f.write(img_data)
                print(f"✅ 图片已下载：{save_name}")

                # ---- 新增：嵌入隐形水印（原地覆盖） ----
                try:
                    embed_invisible_watermark(
                        input_path=save_name,
                        text=WATERMARK_TEXT,
                        output_path=save_name,
                        alpha=WATERMARK_ALPHA
                    )
                except Exception as wm_err:
                    print(f"⚠️ 水印嵌入失败（不影响保存）：{wm_err}")
                # ----------------------------------------

                print("图片保存成功，开始写入数据库...")
                db.add_record(prompt, save_name)
                print(f"✅ 生成成功！URL: {img_url}")
                return img_url
            else:
                print("❌ 未找到图片链接")
                return None
        else:
            print(f"❌ API 报错: Code={response.code}, Message={response.message}")
            return None

    except Exception as e:
        print(f"💥 SDK 调用异常: {e}")
        return None