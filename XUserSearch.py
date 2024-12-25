import asyncio
import random
from twikit.errors import TooManyRequests
from twikit import Client
import csv
import json

visited_users = set()  # 避免重复访问
delay_time = 5  # 初始延迟时间
OUTPUT_FILE = "users_data.csv"  # 存储数据的文件名

# 配置参数
CONFIG = {
    "follow_limit": 20,  # 每次获取粉丝/关注者的数量
    "depth_limit": 2,  # 递归深度
    "delay_min": 5,  # 随机延迟最小时间
    "delay_max": 10,  # 随机延迟最大时间
}

client = Client('en-US')

# 随机延迟函数
async def random_delay():
    await asyncio.sleep(random.uniform(CONFIG["delay_min"], CONFIG["delay_max"]))


# 动态延迟处理速率限制
async def handle_rate_limit():
    global delay_time
    print(f"触发速率限制，等待 {delay_time} 秒...")
    await asyncio.sleep(delay_time)
    delay_time = min(delay_time * 2, 60)  # 每次翻倍延迟，最大 60 秒

# 包装一个重试机制，用于获取用户信息
async def get_user_with_retry(client, user_screen_name, retries=3):
    global delay_time

    for attempt in range(retries):
        try:
            # 延迟请求以降低速率
            await random_delay()
            print(f"获取用户 {user_screen_name} 的信息...")
            return await client.get_user_by_screen_name(user_screen_name)
        except TooManyRequests:
            print(f"触发速率限制 (429)，尝试重试 {attempt + 1}/{retries}...")
            await handle_rate_limit()
        except Exception as e:
            print(f"获取用户 {user_screen_name} 时出错: {e}")
            if attempt == retries - 1:
                raise  # 如果多次尝试后仍失败，则抛出异常
    raise TooManyRequests(f"获取用户 {user_screen_name} 多次重试后仍失败")



# 初始化 CSV 文件，添加表头
def init_csv():
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Display Name", "Description", "Profile Image URL"])

# 写入用户数据到 CSV 文件
def write_to_csv(data):
    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

# 递归查找用户
async def find_users(user, depth):
    if depth == 0 or user.screen_name in visited_users:
        return

    visited_users.add(user.screen_name)
    print(f"[处理用户] 用户名: {user.screen_name}, 姓名: {user.name}")
    user_data = [
        user.screen_name,
        user.name,
        user.description,
        user.profile_image_url
    ]
    write_to_csv(user_data)

    try:
        # 延迟降低速率
        await random_delay()

        # 获取用户的关注者和粉丝
        followings = await user.get_following(CONFIG["follow_limit"])
        # print(f"获取用户 {user.screen_name} 的关注者: {[f.screen_name for f in followings]}")
        followers = await user.get_followers(CONFIG["follow_limit"])
        # print(f"获取用户 {user.screen_name} 的粉丝: {[f.screen_name for f in followers]}")

        for following in followings:
            if following:
                # print(f"开始递归处理关注者用户: {following.screen_name}")
                await find_users(following, depth - 1)
                # print(f"完成递归处理关注者用户: {following.screen_name}")
        for follower in followers:
            if follower:
                # print(f"开始递归处理关注者用户: {follower.screen_name}")
                await find_users(follower, depth - 1)
                # print(f"完成递归处理关注者用户: {follower.screen_name}")

    except TooManyRequests:
        await handle_rate_limit()
    except Exception as e:
        print(f"处理用户 {user.screen_name} 时出错: {e}")



# 主函数
async def main():
    client.load_cookies('cookies.json')  # 确保加载有效的 Cookies

    init_csv()  # 初始化 CSV 文件
    USER_SCREEN_NAMES = ['elonmusk', 'BillGates', 'BarackObama', 'realDonaldTrump', 'narendramodi']

    for user_screen_name in USER_SCREEN_NAMES:
        try:
            user = await get_user_with_retry(client, user_screen_name)
            await find_users(user, CONFIG["depth_limit"])
        except TooManyRequests:
            print(f"用户 {user_screen_name} 的请求触发速率限制，多次重试后失败")
        except Exception as e:
            print(f"处理用户 {user_screen_name} 时出错: {e}")


# 执行主协程
asyncio.run(main())
