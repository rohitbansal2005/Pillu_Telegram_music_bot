import os
import asyncio
from typing import Dict, List, Tuple
from youtubesearchpython.__future__ import VideosSearch, Video
from yt_dlp import YoutubeDL

def get_yt_info_sync(query: str) -> dict:
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'nocheckcertificate': True,
        }
        
        # Bypass YouTube Bot Protection using cookies
        # Important: The user MUST provide cookies.txt via Render Secret Files
        if os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = "cookies.txt"
            
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            except Exception:
                info = ydl.extract_info(query, download=False)
            
            if not info:
                return None
                
            return {
                'id': info.get('id', 'N/A'),
                'title': info.get('title', query),
                'duration': info.get('duration', 0),
                'url': info.get('url'),
                'thumbnail': info.get('thumbnail', ''),
            }
    except Exception as e:
        print(f"YouTube Extraction Error: {e}")
        return None

async def get_yt_info(query: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_yt_info_sync, query)

async def search_youtube(query: str, limit: int = 1) -> List[Dict]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()
    return result['result']
