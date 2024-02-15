import json
import os
import asyncio
import subprocess
import httpx
from telegram import Bot, InputFile
from tenacity import retry, stop_after_attempt, wait_fixed
import requests
import io
from datetime import datetime, timedelta
from telegram.error import RetryAfter

# Constants
CONFIG_FILE = "telegram_config.json"
CHAT_FOLDER = "chats"
DOWNLOAD_DURATION_SECONDS = 20

def display_header():
    header = """
    \033[91mY88b   d88P 88888888888                                    
    \033[91m Y88b d88P      888                                        
    \033[91m  Y88o88P       888                                        
    \033[91m   Y888P        888 \033[35m d8b \033[35m .d88b.  888  888  .d88b.\033[34m        
    \033[91m    888         888  \033[35mY8P\033[35m d8P  Y8b 888  888 d8P  Y8b\033[34m       
    \033[91m    888         888      88888888 888  888 88888888 \033[37m888888 ─ \033[37m
    \033[91m    888         888  \033[35md8b\033[35m Y8b.     Y88b 888 Y8b.\033[34m         
    \033[91m    888         888  \033[35m88P\033[35m  "Y8888   "Y88888  "Y8888\033[34m         
    \033[94m                     \033[35m8P \033[35m               888\033[34m                 
    \033[94m                    \033[35m "  \033[35m          Y8b d88P\033[34m                 
    \033[94m                                   "Y88P"\033[34m  
    \033[37m----------------------------------------------------------\033[37m                
    \033[92m    ➤ Tool For OSINT;\033[0m            ➤ \033[91mVersion: 1.0;
    \033[92m    ➤ Author: @CyberWo9f;\033[0m    ➤ An eye on YT;chat✅;
    \033[37m----------------------------------------------------------\033[37m
    """
    print(header)

async def send_messages_to_telegram(bot, chat_id, messages):
    for message in messages:
        author_name = message['author']['name']
        message_content = message['message']
        message_time = message['timestamp']

        if 'images' in message['author'] and any(image.get('id') == '64x64' for image in message['author']['images']):
            image_url = next(image['url'] for image in message['author']['images'] if image.get('id') == '64x64')
            image_data = requests.get(image_url).content

            image_file = InputFile(io.BytesIO(image_data), filename=f"{author_name}_image.jpg")

            caption = f'👤 | 𝗡𝗮𝗺𝗲: "{author_name}"\n'
            caption += f'🕘 | 𝐓𝐢𝐦𝐞: {message_time}\n'
            caption += f'⚙️ | 𝐒𝐩𝐨𝐭𝐭𝐞𝐝 𝐛𝐲: @YTeye_bot\n'
            caption += f'✉️ | 𝐌𝐞𝐬𝐬𝐚𝐠𝐞: "{message_content}" ✅\n'

            loop = asyncio.get_event_loop()

            try:
                await loop.run_in_executor(None, bot.send_photo, chat_id, image_file, caption)  # Await here
                print(f"[✅]Sent message to Telegram for user {author_name}")

            except RetryAfter as e:
                print(f"[⚠️]Telegram flood control exceeded. Retrying in {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)

        else:
            print(f"[🚫]No 32x32 image found for user {author_name}")

async def send_ready_message(bot, chat_id):
    ready_message = "🚀 Ready to fly! 🚀"
    await bot.send_message(chat_id=chat_id, text=ready_message)  # Await here
    print("[✅]Sent 'Ready to fly!' message to Telegram bot.")

def download_chat(video_id, target_user_ids):
    command = f"chat_downloader {video_id} --output {CHAT_FOLDER}/chat_{video_id}.json --timeout {DOWNLOAD_DURATION_SECONDS}"
    subprocess.run(command, shell=True)

    chat_filename = f"{CHAT_FOLDER}/chat_{video_id}.json"
    with open(chat_filename, 'r', encoding='utf-8') as chat_file:
        chat_data = json.load(chat_file)

        user_messages = []
        for message in chat_data:
            if 'author' in message and 'id' in message['author'] and message['author']['id'] in target_user_ids:
                user_messages.append(message)
                print(f"[✅]Target user ID {message['author']['id']} found in the chat for video ID {video_id}")

        # Convert timestamps to the expected format, handling errors
        for message in user_messages:
            if 'timestamp' in message:
                try:
                    if isinstance(message['timestamp'], int):
                        message['timestamp'] = datetime.utcfromtimestamp(message['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    print(f"[❌]Error processing timestamp for message: {message}. Error: {e}. Skipping message.")
                    continue
        
        return user_messages

    print(f"[🚫]Target user IDs {target_user_ids} not found in the chat for video ID {video_id}")
    return None

def delete_unwanted_chat_files():
    for filename in os.listdir(CHAT_FOLDER):
        if filename.endswith(".json") and not filename.startswith("chat_"):
            os.remove(os.path.join(CHAT_FOLDER, filename))
            print(f"Deleted: {filename}")

from datetime import datetime

def user_is_online(user_messages):
    # Check if there are new messages in the last two minutes
    if user_messages:
        current_time = datetime.utcnow()
        for message in user_messages:
            if 'timestamp' in message:
                timestamp = message['timestamp']
                if isinstance(timestamp, int):
                    # Handle extremely large timestamps
                    if timestamp > 2**31:
                        print(f"[❌]Error processing timestamp for message: {message}. Timestamp too large. Skipping message.")
                        continue
                    else:
                        try:
                            last_message_time = datetime.utcfromtimestamp(timestamp)
                        except OverflowError:
                            print(f"[❌]Error processing timestamp for message: {message}. Timestamp out of range. Skipping message.")
                            continue
                elif isinstance(timestamp, str):
                    try:
                        last_message_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"[❌]Error processing timestamp for message: {message}. Invalid timestamp format. Skipping message.")
                        continue
                else:
                    print(f"[❌]Error processing timestamp for message: {message}. Invalid timestamp format. Skipping message.")
                    continue

                time_difference = current_time - last_message_time
                if time_difference.total_seconds() < 120:  # 2 minutes
                    return True
    return False

async def main():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            config_data = json.load(config_file)
            telegram_token = config_data.get('telegram_token')
            telegram_chat_id = config_data.get('telegram_chat_id')
            target_user_ids = config_data.get('target_user_ids', [])

            if not (telegram_token and telegram_chat_id and target_user_ids):
                telegram_token, telegram_chat_id, target_user_ids = await setup_telegram()
                print("[!]Telegram configuration updated.")
                await send_ready_message(Bot(token=telegram_token), telegram_chat_id)
    else:
        telegram_token, telegram_chat_id, target_user_ids = await setup_telegram()
        print("[✅]Telegram configuration set.")
        await send_ready_message(Bot(token=telegram_token), telegram_chat_id)

    bot = Bot(token=telegram_token)

    video_ids_filename = input("➤ Enter the filename containing live stream video ID: ")
    with open(video_ids_filename, 'r') as file:
        live_stream_video_ids = [line.strip() for line in file if line.strip()]

    if not target_user_ids:
        num_users = int(input("➤ Enter the number of target YT users to monitor: "))
        for i in range(num_users):
            target_user_ids.append(input(f"➤ Enter target YT user ID {i+1}: "))
        
        # Save target_user_ids to config file
        save_config_data(telegram_token, telegram_chat_id, target_user_ids)

    # Dictionary to store user messages for each video ID
    user_messages_dict = {video_id: [] for video_id in live_stream_video_ids}

# Main loop
    while True:
        # Check user activity for each video
        for video_id in live_stream_video_ids:
            user_messages = download_chat(video_id, target_user_ids)
            user_messages_dict[video_id].extend(user_messages)

            if user_messages and user_is_online(user_messages):
                print(f"[!]User is online in video ID: {video_id}")
        
        # Send unique messages to Telegram
        unique_messages = set()
        for video_id, messages in user_messages_dict.items():
            for message in messages:
                unique_messages.add(json.dumps(message))
        
        unique_messages = [json.loads(message) for message in unique_messages]

        if unique_messages:
            await send_messages_to_telegram(bot, telegram_chat_id, unique_messages)

        # Clear user_messages_dict
        user_messages_dict = {video_id: [] for video_id in live_stream_video_ids}

        # Delete unwanted chat files
        delete_unwanted_chat_files()

        await asyncio.sleep(60)  # 60 seconds interval

async def setup_telegram():
    print("[!]Telegram Bot Setup")
    telegram_token = input("➤ Enter your Telegram bot token: ")
    telegram_chat_id = input("➤ Enter your Telegram chat ID: ")
    
    target_user_ids = []
    num_users = int(input("➤ Enter the number of target YT users to monitor: "))
    for i in range(num_users):
        target_user_ids.append(input(f"➤ Enter target YT user ID {i+1}: "))

    save_config_data(telegram_token, telegram_chat_id, target_user_ids)

    return telegram_token, telegram_chat_id, target_user_ids

def save_config_data(telegram_token, telegram_chat_id, target_user_ids):
    config_data = {
        'telegram_token': telegram_token,
        'telegram_chat_id': telegram_chat_id,
        'target_user_ids': target_user_ids
    }
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config_data, config_file)

# Display the header
display_header()

# Run the asyncio event loop
asyncio.run(main())
