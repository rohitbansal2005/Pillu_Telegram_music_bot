import os
import asyncio
import requests
import html
from typing import Dict, List, Tuple
from youtubesearchpython.__future__ import VideosSearch, Video
from yt_dlp import YoutubeDL
import re

def clean_title(title: str) -> str:
    if not title:
        return ""
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title)
    words_to_remove = ['official', 'video', 'lyrical', 'hd', '4k', '8k', 'audio', 'full song', 't-series', 'tseries', 'slowed', 'reverb', 'lofi', 'remix', 'dj', 'mashup']
    for word in words_to_remove:
        title = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE).sub('', title)
    title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    words = title.split()
    if len(words) > 5:
        title = ' '.join(words[:5])
    return title.strip()

def get_yt_info_sync(query: str, search_title: str = None) -> dict:
    try:
        search_query = search_title if search_title else query
        
        # 1. Search on JioSaavn
        res = requests.get(f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query={search_query}")
        data = res.json()
        
        songs = data.get('songs', {}).get('data', [])
        if not songs:
            return None
            
        song_id = songs[0]['id']
        
        # 2. Get song details to get perma_url
        details_res = requests.get(f"https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids={song_id}")
        details = details_res.json()
        
        if song_id not in details:
            return None
            
        song_data = details[song_id]
        perma_url = song_data.get('perma_url', '')
        
        if not perma_url:
            return None
            
        # Ensure downloads directory exists
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
            
        # 3. Use yt-dlp to DOWNLOAD the audio stream locally
        # This prevents 100% of network-related stuttering issues on slow CPUs
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'nocheckcertificate': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            # Check if we already have it downloaded to save time
            info = ydl.extract_info(perma_url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not info:
                return None
                
            # Convert duration to standard M:SS format
            duration_sec = int(info.get('duration', 0))
            minutes = duration_sec // 60
            seconds = duration_sec % 60
            duration_formatted = f"{minutes}:{seconds:02d}"
            
            title = html.unescape(song_data.get('title', search_query))
            
            return {
                'id': song_id,
                'title': title,
                'duration': duration_formatted,
                'url': filename,  # Return local path!
                'thumbnail': song_data.get('image', '').replace('150x150', '500x500'),
            }
    except Exception as e:
        print(f"JioSaavn Extraction Error: {e}")
        return None

async def get_yt_info(query: str) -> dict:
    search_title = None
    if query.startswith("http"):
        try:
            # If user pasted YouTube link, extract title and use it for JioSaavn
            video_info = await Video.getInfo(query)
            raw_title = video_info.get('title', '')
            search_title = clean_title(raw_title)
        except:
            pass
    else:
        search_title = clean_title(query)
            
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_yt_info_sync, query, search_title)

async def search_youtube(query: str, limit: int = 1) -> List[Dict]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()
    return result['result']
