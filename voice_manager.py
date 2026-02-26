import os
import sys
import time
import audioop  # <--- 新增：用于计算音量
import dashscope
import pyaudio
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
from test import config

# 配置 API Key
dashscope.api_key = config.API_KEY

# 全局变量
final_text = ""


# --- 1. 回调类 (保持不变) ---
class MyCallback(RecognitionCallback):
    def on_open(self) -> None:
        print('🎤 连接建立，开始说话...')

    def on_close(self) -> None:
        print('⛔ 连接关闭。')

    def on_event(self, result: RecognitionResult) -> None:
        global final_text
        sentence = result.get_sentence()
        if 'text' in sentence:
            if RecognitionResult.is_sentence_end(sentence):
                final_text += sentence['text']
                # 打印出来方便调试
                print(f"\r📝 已识别: {final_text}", end="")

    def on_error(self, message) -> None:
        print('❌ 识别出错:', message.message)


# --- 2. 智能录音函数 (核心修改) ---
def listen_smart(silence_threshold=500, max_seconds=60):
    """
    智能录音：检测到静音自动停止
    :param silence_threshold: 静音阈值 (根据麦克风灵敏度调整，通常 300-800 之间)
    :param max_seconds: 最长录音时间 (防止死循环，默认60秒)
    """
    global final_text
    final_text = ""

    # 录音参数
    sample_rate = 16000
    format_pcm = 'pcm'
    block_size = 3200  # 每次读取 0.2 秒的数据

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16,
                      channels=1,
                      rate=sample_rate,
                      input=True)

    callback = MyCallback()
    recognition = Recognition(
        model='paraformer-realtime-v1',
        format=format_pcm,
        sample_rate=sample_rate,
        callback=callback
    )

    print(f"🎙️ 请说话 (检测到静音会自动停止)...")
    recognition.start()

    # --- 智能检测逻辑 ---
    start_time = time.time()
    last_active_time = time.time()  # 上一次听到声音的时间

    try:
        while True:
            # 1. 读取音频数据
            data = stream.read(block_size, exception_on_overflow=False)

            # 2. 发送给阿里云
            recognition.send_audio_frame(data)

            # 3. 计算音量 (RMS: Root Mean Square)
            # data 是二进制流，width=2 表示 16-bit 音频
            rms = audioop.rms(data, 2)

            # 调试：打印当前音量，方便你调整阈值
            # print(f"当前音量: {rms}")

            # 4. 判断逻辑
            if rms > silence_threshold:
                # 声音很大，说明还在说话，重置计时器
                last_active_time = time.time()
            else:
                # 声音很小（静音）
                # 计算静音持续了多久
                silence_duration = time.time() - last_active_time

                # 如果静音超过 1.5 秒，认为话说完了
                if silence_duration > 1.5:
                    print("\n🛑 检测到静音，停止录音。")
                    break

            # 5. 兜底逻辑：防止录太久
            if (time.time() - start_time) > max_seconds:
                print("\n⏰ 达到最大时长，强制停止。")
                break

    except Exception as e:
        print(f"\n❌ 录音出错: {e}")
    finally:
        # 清理工作
        recognition.stop()
        stream.stop_stream()
        stream.close()
        mic.terminate()

    return final_text


# --- 单元测试 ---
if __name__ == '__main__':
    print("开始测试...")
    res = listen_smart(silence_threshold=300)
    print(f"\n🎉 最终结果: {res}")