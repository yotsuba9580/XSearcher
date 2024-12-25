import asyncio
from twikit import Client
from configparser import ConfigParser
import random
import csv

# # Enter your account information
USERNAME = 'XXX'
EMAIL = 'XXX'
PASSWORD = 'XXX'


client = Client('en-US')

async def main():
    await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )

    client.save_cookies('cookies.json')

asyncio.run(main())