import random # 引入工具包
# 准备一个风格列表（List，用方括号）
style_list = ["赛博朋克", "水墨画", "吉卜力动漫", "凡高油画"]
# 随机抽一个
lucky_style = random.choice(style_list)
print(f"AI 为你推荐的风格是：{lucky_style}")