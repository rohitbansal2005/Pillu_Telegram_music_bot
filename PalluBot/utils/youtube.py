import asyncio
from typing import Dict, List, Tuple
from yt_dlp import YoutubeDL
from youtubesearchpython.__future__ import VideosSearch

import os

def get_yt_info_sync(query: str) -> dict:
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {'youtube': ['player_client=android']},
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }
    
    # Bypass YouTube Bot Protection using cookies
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        except Exception:
            info = ydl.extract_info(query, download=False)
    return info

async def get_yt_info(query: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_yt_info_sync, query)

async def search_youtube(query: str, limit: int = 1) -> List[Dict]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()
    return result['result']
