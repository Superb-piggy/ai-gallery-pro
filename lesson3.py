import  random
def draw_card():
    rand_num = random.randint(1,100)
    if rand_num > 90:
        print("金色传说")
    elif rand_num > 60:
        print("紫色史诗")
    else:
        print("白色普通")
    return

for i in range(10):
    draw_card()