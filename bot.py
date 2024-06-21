import asyncio
import aiohttp
import httpx
import sqlite3
from aiohttp import ClientSession
import xml.etree.ElementTree as ET
import os

DATABASE = 'medium_posts.db'
TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
TG_DESTINATION_CHAT_ID = os.getenv('CHAT_ID')
CHECKING_PERIOD = 60 # in minutes

def load_file_as_list(file_path):
    """
    Loads a text file and returns its lines as a list.

    :param file_path: Path to the text file.
    :return: List of lines in the text file.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # Strip newline characters from each line
        lines = [line.strip() for line in lines]
        return lines
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return []
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
        return []
      


async def send_message(bot_token: str, msg: str, chat_id: str):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': msg
    }
    
    async with aiohttp.ClientSession() as session:
        await asyncio.sleep(2)
        async with session.post(url, data=payload) as response:
            if response.status == 200:
                print(f"Message sent successfully to chat_id {chat_id}")
            else:
                print(f"Failed to send message. Status code: {response.status}")

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY, title TEXT, link TEXT)''')
    conn.commit()
    conn.close()

# Retrieve tags (for example, from a static list or an API)
def get_tags():
    return load_file_as_list("tags.txt")

def get_channel_ids():
    channel_id_links = load_file_as_list("youtube_channels.txt")
    final_channel_ids = []

    for string in channel_id_links:
        if "/" in string:
            parts = string.split("/")
            last_part = parts[-1]
            final_channel_ids.append(last_part)
        else:
            final_channel_ids.append(string)

    return final_channel_ids


# Search Medium for posts related to the given tags
async def search_medium(tag, session:httpx.AsyncClient):
    url = f"https://medium.com/feed/tag/{tag}"
    response = await session.get(url)
    
    xml_data = response.content
        
    # Parse the XML data
    root = ET.fromstring(xml_data)
    
    # Find and process each item in the RSS feed
    posts = []
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        link = item.find('guid').text

        # Print the extracted information
        posts.append({"title": title, "link": link})
    
    return posts

async def search_youtube(channel_id, session:httpx.AsyncClient):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    response = await session.get(url)
    
    xml_data = response.content
        
    # Parse the XML data
    root = ET.fromstring(xml_data)
    
    # Find and process each item in the RSS feed
    posts = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        video_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split(":")[-1]
        link = f"https://www.youtube.com/v/{video_id}"


        # Print the extracted information
        posts.append({"title": title, "link": link})
    
    return posts
    
# Save posts to the database
def save_posts(posts):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    new_posts = []
    for post in posts:
        c.execute("SELECT * FROM posts WHERE link=?", (post['link'],))
        if not c.fetchone():
            c.execute("INSERT INTO posts (title, link) VALUES (?, ?)", (post['title'], post['link']))
            new_posts.append(post)
    conn.commit()
    conn.close()
    return new_posts

# Notify about new posts
async def notify_new_posts(new_posts):
    if new_posts:
        async with ClientSession() as session:
            for post in new_posts:
                # Notify logic here (e.g., send an email, push notification, etc.)
                await send_message(TG_BOT_TOKEN, f"{post['title']} \n{post['link']}", TG_DESTINATION_CHAT_ID)
                print(f"New post found: {post['title']} - {post['link']}")

# Main async function to perform the search and save operations
async def main():
    while True:
        init_db()
        tags = get_tags()
        channel_ids = get_channel_ids()
        async with httpx.AsyncClient() as client:
            youtube_tasks = [search_youtube(channel_id, client) for channel_id in channel_ids]
            medium_tasks = [search_medium(tag, client) for tag in tags]
            tasks = youtube_tasks + medium_tasks
            results = await asyncio.gather(*tasks)
        
        all_posts = [post for result in results for post in result]
        new_posts = save_posts(all_posts)
        await notify_new_posts(new_posts)
        
        await asyncio.sleep(CHECKING_PERIOD * 60)  

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
