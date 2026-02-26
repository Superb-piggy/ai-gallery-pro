# server.py
from fastapi import FastAPI
from pydantic import BaseModel
import image_manager
import asyncio
from llm_manager import LocalBrain
app = FastAPI()
brain = LocalBrain()
import time
class DrawRequest(BaseModel):
    text: str
    num: int = 1

class Image2Image(BaseModel):
    text: str
    temp_path:str
class Chat(BaseModel):
    text: str

@app.post("/draw")
async def generate_image(request: DrawRequest):
    print(f"🔔 收到新订单！内容：{request.text}, 数量：{request.num}")
    try:
        result = image_manager.generate_and_save(request.text, request.num)
        return {
            "status": "success",
            "message": "生成成功",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"生成失败：{str(e)}"
        }

@app.post("/image_2_image")
async def image_2_image(request: Image2Image):
    print(f"🔔 收到新订单！内容：{request.text}")
    try:
        result = image_manager.generate_image_with_ref(request.text, request.temp_path)
        return {
            "status": "success",
            "message": "生成成功",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"生成失败：{str(e)}"
        }

@app.post("/chat")
async def chat(request:Chat):
    print(time.time())
    think, ans = await asyncio.to_thread(brain.chat_with_thinking, request.text)
    print(time.time())
    return {"response": ans}

@app.get("/")
async def root():
    return {"message": "欢迎来到 AI 画廊服务中心！"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "lesson9:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )