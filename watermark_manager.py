import cv2
import numpy as np


def _make_watermark_mask(rows, cols, text):
    """
    内部函数：生成中心对称的水印掩膜（黑底白字，单通道）

    【核心原理】为什么需要中心对称？
    因为自然图像的傅里叶频谱具有共轭对称性（Hermitian symmetry）。
    为了保证逆傅里叶变换后得到的图像仍然是纯实数矩阵（不产生虚部失真），
    我们在频域添加的水印信号也必须是严格中心对称的。
    """
    # 1. 创建一个与原图尺寸相同的全黑掩膜
    watermark = np.zeros((rows, cols), dtype=np.uint8)

    # 2. 根据图像尺寸动态调整字体大小和粗细，确保水印不至于太小看不清
    font_scale = max(rows / 400, 0.8)
    thickness = max(int(font_scale * 2), 2)

    # 4. 【关键位置选择】将文字偏移到左上角 (例如宽高各 15% 的位置)
    # 原因 A: 远离正中心（低频区），防止被原图巨大的低频能量（DC分量）掩盖，导致看不见。
    # 原因 B: 远离正中心，保证后面的翻转操作后，原字和倒影分别在左上和右下，绝对不会重叠变成乱码。
    x = int(cols * 0.15)
    y = int(rows * 0.15)

    # 5. 在全黑背景上绘制白色水印文字
    cv2.putText(watermark, text, (x, y),
                cv2.FONT_HERSHEY_COMPLEX, font_scale, 255, thickness)

    # 6. 生成中心对称图像：原图 + 旋转180度的翻转图 (cv2.flip(..., -1))
    # 转换为 float64 是因为后续频域计算涉及到浮点数矩阵叠加
    return (watermark + cv2.flip(watermark, -1)).astype(np.float64)


def _embed_channel(channel, watermark_mask, alpha):
    """
    内部函数：对单个灰度通道做频域水印嵌入
    """
    # 1. 执行二维快速傅里叶变换 (FFT)，将图像从空间域转换到频率域
    f = np.fft.fft2(channel.astype(np.float64))

    # 2. 频移操作：将零频分量（低频的亮斑）移动到频谱中心，方便基于中心做处理
    fshift = np.fft.fftshift(f)

    # 3. 嵌入水印：将准备好的对称水印掩膜乘上强度系数 alpha，直接叠加到频谱上
    fshift_wm = fshift + alpha * watermark_mask

    # 4. 逆频移操作：将零频分量移回原处（左上角），为逆变换做准备
    f_ishift = np.fft.ifftshift(fshift_wm)

    # 5. 执行二维逆快速傅里叶变换 (IFFT)，将图像从频率域转换回空间域
    img_back = np.fft.ifft2(f_ishift)

    # 6. 取实部（理想情况下虚部接近0），并将像素值截断限制在 0~255 的有效范围内，最后转回 uint8
    return np.clip(np.real(img_back), 0, 255).astype(np.uint8)


def embed_invisible_watermark(input_path, text, output_path, alpha=20):
    """
    利用傅里叶变换添加隐形水印（频域操作），保留原图色彩。

    :param input_path:  原图路径
    :param text:        水印文字 (需为英文字符，OpenCV 默认不支持中文)
    :param output_path: 嵌入水印后的输出路径
    :param alpha:       嵌入强度。值越大，提取的水印越清晰，但原图可能出现可见的波纹状噪点（画质下降）。
    """
    # 1. 以彩色模式读取图片（BGR）
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"无法读取图片：{input_path}")

    rows, cols = img.shape[:2]

    # 2. 生成中心对称的水印掩膜（只需生成一次，三个通道共用）
    wm_mask = _make_watermark_mask(rows, cols, text)

    # 3. 拆分 B、G、R 三个色彩通道
    channels = cv2.split(img)

    # 4. 列表推导式：对三个通道分别调用 _embed_channel 进行频域水印嵌入
    watermarked_channels = [_embed_channel(ch, wm_mask, alpha) for ch in channels]

    # 5. 将处理后的三个通道重新合并为一张彩色图像
    result = cv2.merge(watermarked_channels)

    # 6. 保存带有隐形水印的图片
    cv2.imwrite(output_path, result)
    print(f"🕵️  隐形水印已嵌入：{output_path}")


def extract_invisible_watermark(input_path, output_path):
    """
    从带有隐形水印的图像中提取并保存频谱图，以进行版权验证。
    """
    # 1. 读取包含水印的图片
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"无法读取图片：{input_path}")

    # 2. 提取单通道进行频谱分析
    # 嵌入时 B、G、R 三个通道都加了水印，理论上取任何一个都可以验证。这里提取 B 通道（索引0）。
    b_channel = cv2.split(img)[0]

    # 3. 对该通道执行二维快速傅里叶变换
    f = np.fft.fft2(b_channel.astype(np.float64))

    # 4. 将零频分量移到中心，此时真正的频谱图结构显现
    fshift = np.fft.fftshift(f)

    # 5. 计算频谱的幅度谱（Magnitude Spectrum）
    # 傅里叶变换的结果是复数，我们使用绝对值计算幅度。
    # 因为中心低频和边缘高频的幅度差异极其巨大，直接显示会是一片黑（中间一个白点）。
    # 使用对数变换公式 $20 \log(|F| + 1)$ 压缩动态范围，使人眼能看清楚高频区域（我们嵌入水印的地方）。
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)

    # 6. 对比度拉伸（归一化）
    # 将对数变换后的幅度值线性映射到 0~255 的标准灰度图像范围内，方便保存和肉眼观察。
    magnitude_spectrum = cv2.normalize(
        magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
    )

    # 7. 保存提取出的频谱图，里面将浮现出我们嵌入的对称文字
    cv2.imwrite(output_path, magnitude_spectrum)
    print(f"🔍 频谱图已提取：{output_path}")


# --- 测试 ---
if __name__ == "__main__":
    # 第一步：嵌入肉眼不可见的水印（注意：Alpha=30 表示较强的嵌入强度，方便测试时看清）
    embed_invisible_watermark("draw_1770572250.jpg", "MY WATERMARK", "test_invisible.jpg", alpha=30)

    # 第二步：提取频谱图进行版权验证（打开 proof.jpg 查看左上角和右下角）
    extract_invisible_watermark("test_invisible.jpg", "proof.jpg")