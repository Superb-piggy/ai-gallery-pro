# main.py (升级版)
import gen_image as ai_tools

# 定义“大师级”后缀 (Magic Suffix)
magic_suffix = ", 8k resolution, highly detailed, cinematic lighting, masterpiece, trending on artstation"

print("=== AI 艺术工作室 (Pro版) ===")

prompt = input("你想画什么：")
style = input("风格 (1.赛博 2.油画)：")

# --- 这里体现了 Prompt 工程 ---
# 1. 主体
final_prompt = prompt

# 2. 风格 (Example Mapping)
if style == "1":
    final_prompt += ", cyberpunk style, neon lights"
elif style == "2":
    final_prompt += ", oil painting, van gogh style"

# 3. 质量修饰 (CoT 的结果应用：我们预设了好的光影和细节)
final_prompt += magic_suffix

print(f"🪄 优化后的咒语：{final_prompt}")

# 调用工具
ai_tools.generate_and_save(final_prompt,1)