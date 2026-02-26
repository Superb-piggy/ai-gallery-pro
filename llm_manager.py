from transformers import AutoModelForCausalLM, AutoTokenizer

class LocalBrain:
    def __init__(self):
        print("🧠 正在初始化本地大脑...")
        print("📥 正在加载模型权重...")
        self.tokenizer = AutoTokenizer.from_pretrained('Qwen3-0.6B')
        self.model = AutoModelForCausalLM.from_pretrained(
            'Qwen3-0.6B',
            torch_dtype="auto",  # 自动选择精度 (float16 或 float32)
            device_map="auto"  # 有显卡用显卡，没显卡用 CPU
        )
        print("✅ 本地大脑已就绪！")

    def chat_with_thinking(self, prompt):
        """
        发送提示词，并返回 (思考过程, 最终回答)
        """
        # 构造消息
        messages = [{"role": "user", "content": prompt}]

        # 应用聊天模板
        # 注意：enable_thinking 参数取决于模型是否支持思维链
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # 转为 Tensor
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        # 开始推理 (Generate)
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512,  # 最大生成长度
            temperature=0.7  # 创意度
        )

        # 提取新生成的 token (去掉输入的 prompt 部分)
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

        # 尝试寻找思维链结束标记 </think> (Token ID: 151668)
        # 注意：不同模型的特殊 Token ID 可能不同，这里为了通用性，我们用字符串匹配兜底
        try:
            # 151668 是 Qwen 系列 </think> 的常见 ID，但如果模型没输出这个 token，会报错
            index = len(output_ids) - output_ids[::-1].index(151668)

            # 解码
            thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip()
            content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip()

        except ValueError:
            # 如果没找到 </think>，说明模型直接输出了结果，没有显式思考过程
            thinking_content = "（模型直接输出了结果，未检测到显式思考过程）"
            content = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        return thinking_content, content


# --- 单元测试 ---
if __name__ == "__main__":
    brain = LocalBrain()
    think, ans = brain.chat_with_thinking("请简短介绍一下什么是大语言模型。")
    print(f"🤔 思考过程:\n{think}")
    print(f"🗣️ 最终回答:\n{ans}")