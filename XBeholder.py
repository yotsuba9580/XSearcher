import asyncio
import os
import random
from twikit.errors import TooManyRequests
from twikit import Client
import csv
from datetime import datetime, timezone

# 配置参数
CONFIG = {
    "delay_min": 3,  # 随机延迟最小时间
    "delay_max": 8,  # 随机延迟最大时间
    "max_tweets": 30,  # 搜索最大推文数
    "target_screen_name": "elonmusk",  # 目标用户 screen_name
    "check_interval": 60 * 5, # 检查新推文的时间间隔
    "check_offset": 30,  # 检查新推文的时间偏移
    "history_tweets": True,  # 是否获取历史推文
    "realtime_tweets": True,  # 是否获取实时推文
    "tweet_check_num": 10  # 检查新推文的数量，实时获取推文时每经过check_interval检查最新的推文数量，如果用户发布频率较高，可以适当增加
}

delay_time = 5  # 初始延迟时间
OUTPUT_FILE = f"{CONFIG['target_screen_name']}_tweets.csv"
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

# 初始化 CSV 文件，添加表头
def init_csv():
    # 如果文件不存在，创建文件并写入表头
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "text", "RT full text"])

# 写入用户数据到 CSV 文件
def write_to_csv(data):
    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)


async def main():
    # 初始化 Twikit 客户端
    client = Client(language='en-US')
    init_csv()

    # 用户登录（需要有效的凭据）
    try:
        client.load_cookies('cookies.json')  # 确保加载有效的 Cookies
        print("Logged in successfully!")
    except Exception as e:
        print(f"Error logging in: {e}")
        print("Please use the `login.py` script to log in first.")
        return

    # 通过用户 screen_name 获取用户 ID
    target_screen_name = CONFIG["target_screen_name"]
    user = await client.get_user_by_screen_name(target_screen_name)
    user_id = user.id
    print(f"Target User ID: {user_id}")

    # 处理分页
    tweets_fetched = 0
    cursor = None

    if CONFIG["history_tweets"]:
        # 爬取用户的所有推文
        print("Fetching all tweets...")
        while tweets_fetched < CONFIG["max_tweets"]:
            try:
                print("Fetching tweets...")
                await random_delay()
                tweets = await client.get_user_tweets(user_id, tweet_type='Tweets', count=20, cursor=cursor)
                if not tweets:
                    break
                for tweet in tweets:
                    # 第一个版本，区分转推与原创
                    data = [
                        tweet.id,
                        tweet.full_text.split(":", 1)[0] if tweet.retweeted_tweet else tweet.full_text,  # 如果是转推，只保留转推的信息，完整信息在下一列
                        tweet.retweeted_tweet.text if tweet.retweeted_tweet else None
                    ]

                    # # 第二个版本，不区分转推与原创
                    # data = [
                    #     tweet.id,
                    #     tweet.retweeted_tweet.text if tweet.retweeted_tweet else tweet.full_text
                    # ]

                    write_to_csv(data)
                    tweets_fetched += 1
                    if tweets_fetched >= CONFIG["max_tweets"]:
                        break
                print(f"Fetched {tweets_fetched}/{CONFIG['max_tweets']} tweets.")

                    # last_tweet = tweet.id
                if not tweets.next_cursor:
                    print('No more tweets to fetch.')
                    break

                cursor = tweets.next_cursor
            except TooManyRequests:
                await handle_rate_limit()
            except Exception as e:
                print(f"获取用户 {user_id} 时出错: {e}")

        print("Finished fetching tweets.")

    latest_timestamp = datetime.now(timezone.utc)

    if CONFIG["realtime_tweets"]:
        # 获取实时推文
        while (True):
            try:
                latest_tweets = await client.get_user_tweets(user_id, 'Tweets', count=CONFIG['tweet_check_num'])  # 获取最新的推文，用于检查新推文
                if latest_timestamp is not None:
                    new_tweets = [tweet for tweet in latest_tweets if tweet.created_at_datetime > latest_timestamp]
                else:
                    new_tweets = latest_tweets

                for tweet in new_tweets:
                    data = [
                        tweet.id,
                        tweet.full_text.split(":", 1)[0] if tweet.retweeted_tweet else tweet.full_text,  # 如果是转推，只保留转推的信息，完整信息在下一列
                        tweet.retweeted_tweet.text if tweet.retweeted_tweet else None
                    ]

                    # # 第二个版本，不区分转推与原创
                    # data = [
                    #     tweet.id,
                    #     tweet.retweeted_tweet.text if tweet.retweeted_tweet else tweet.full_text
                    # ]

                    write_to_csv(data)

                print(f"found {len(new_tweets)} new tweets")
                if new_tweets:
                    latest_timestamp = latest_timestamp = max(tweet.created_at_datetime for tweet in new_tweets)
            except TooManyRequests:
                await handle_rate_limit()
            except Exception as e:
                print(f"Error occureed: {e}")

            print(f"Sleeping for {CONFIG['check_interval']} seconds...")
            await asyncio.sleep(CONFIG["check_interval"])


# TODO: 目前获取单个用户的推文，比较稳定，可以通过运行多个python进程来获取多个用户的推文，每个进程使用不同的cookies.json文件，实现一个账号获取一个用户的推文。后续可以考虑加入并发处理，实现一个账号获取多个用户的推文，但稳定性难以保证
# 异步运行主函数
asyncio.run(main())
