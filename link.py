import subprocess
import os
from googleapiclient.discovery import build

def read_api_keys_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            api_keys = [line.strip() for line in file.readlines()]
        return api_keys
    except FileNotFoundError:
        print(f"[!]Error: File '{file_path}' not found.")
        return []

def get_valid_api_key(api_keys):
    for api_key in api_keys:
        youtube = build('youtube', 'v3', developerKey=api_key)
        try:
            youtube.search().list(q='test', part='id', maxResults=1).execute()
            return api_key  # API key is valid
        except Exception as e:
            print(f"[!]Invalid API key: {api_key}")
            continue
    print("[!]No valid API keys found.")
    return None

def get_keywords():
    print("[!] Enter your search keywords, one per line. Press Enter on an empty line to finish:")
    keywords = []
    while True:
        keyword = input().strip()
        if not keyword:
            break
        keywords.append(keyword)
    return keywords

def youtube_search(api_key, query, max_results=5):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        q=query,
        type='video',
        eventType='live',
        part='id',
        maxResults=max_results
    )

    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    return video_ids

def save_video_ids_to_file(video_ids):
    with open('ids.txt', 'w') as file:
        for video_id in video_ids:
            file.write(f"{video_id}\n")

def display_header():
    header = """
\033[91m Y88b   d88P 88888888888                    d8b \033[0m
\033[91m  Y88b d88P      888                        Y8P \033[0m
\033[91m   Y88o88P       888                            \033[0m
\033[91m    Y888P        888  d8b  8888b.  88888b.  888 \033[0m
\033[91m     888         888  Y8P     "88b 888 "88b 888 \033[0m
\033[91m     888         888      .d888888 888  888 888 \033[0m
\033[91m     888         888  d8b 888  888 888 d88P 888 \033[0m
\033[91m     888         888  88P "Y888888 88888P"  888 \033[0m
\033[91m                      8P           888          \033[0m
\033[91m                      "            888          \033[0m

\033[37m----------------------------------------------------------\033[0m
    \033[92m➤ Tool For OSINT;            ➤ Version: 1.0;\033[0m
    \033[92m➤ Author: @CyberWo9f;        ➤ An eye on YT;chat✅;\033[0m
\033[37m----------------------------------------------------------\033[0m
"""
    print(header)

if __name__ == "__main__":
    # Display the header
    display_header()

    # Keep prompting until a valid API keys file path is provided
    while True:
        api_keys_file_path = input("➤ Enter the path to your API keys file: ")

        # Read and validate API keys
        api_keys = read_api_keys_from_file(api_keys_file_path)

        if api_keys:
            # Get a valid API key
            valid_api_key = get_valid_api_key(api_keys)

            if valid_api_key:
                # Get keywords interactively
                keywords = get_keywords()

                all_video_ids = []

                for search_query in keywords:
                    video_ids = youtube_search(valid_api_key, search_query)
                    all_video_ids.extend(video_ids)

                    if video_ids:
                        print(f"[!]Live stream video IDs for '{search_query}':")
                        print(video_ids)
                    else:
                        print(f"[!]No live streams found for '{search_query}'.")

                # Save all video IDs to 'ids.txt' file
                save_video_ids_to_file(all_video_ids)
                print("[!]Live stream video IDs saved to 'ids.txt'.")

                # Execute another Python script (replace 'yteye6.py' with the actual filename)
                subprocess.run(["python", "yteye6.py"])
                break  # Exit the loop if everything is successful
            else:
                print("[!]Try again with a different API key.")
        else:
            print("[!]Try again with a different file path.")
