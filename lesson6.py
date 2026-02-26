import requests
from PIL import Image,ImageFilter

import random

urls = [
    "https://picsum.photos/400/300",
    "https://picsum.photos/400/300",
    "https://picsum.photos/400/300"
]

filters = [
    ImageFilter.BLUR,
    ImageFilter.CONTOUR,
    ImageFilter.DETAIL,
    ImageFilter.EDGE_ENHANCE,
    ImageFilter.EDGE_ENHANCE_MORE,
    ImageFilter.EMBOSS,
    ImageFilter.FIND_EDGES,
    ImageFilter.SMOOTH,
    ImageFilter.SMOOTH_MORE,
    ImageFilter.SHARPEN
]

for i,url in enumerate(urls):
    filename = f"img_{i+1}.jpg"
    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)

    filter = random.choice(filters)
    print(filter)
    im = Image.open(filename)
    filename = filename.replace(".jpg","_filter.jpg")
    im = im.filter(filter)
    im.save(filename)

print("结束")