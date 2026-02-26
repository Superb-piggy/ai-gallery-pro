import asyncio  # 引入大堂经理
import time


# async def 表示这是一个可以被经理调度的“异步员工”
async def fetch_data(id):
    print(f"[{id}] 员工发起网络请求...")

    # 【await 的作用】：员工在这里对经理喊：“我要等网速，你先去管别人！”
    # 经理拿到控制权，立刻去启动下一个 fetch_data
    await asyncio.sleep(2)  # 模拟网络延迟 2 秒

    print(f"[{id}] 数据拿到了！")


async def main():
    start = time.time()

    # 【asyncio 的作用】：经理发话：“这 3 个任务，同时扔进池子里跑！”
    tasks = [fetch_data(1), fetch_data(2), fetch_data(3)]
    await asyncio.gather(*tasks)

    print(f"总耗时: {time.time() - start:.1f} 秒")


# 【asyncio 的作用】：启动整个事件循环引擎
asyncio.run(main())