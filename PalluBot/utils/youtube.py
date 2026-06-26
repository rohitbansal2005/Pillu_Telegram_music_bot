import os
import asyncio
from typing import Dict, List, Tuple
from youtubesearchpython.__future__ import VideosSearch, Video
from yt_dlp import YoutubeDL

def get_yt_info_sync(query: str, search_title: str = None) -> dict:
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        
        # We use SoundCloud to completely bypass YouTube's datacenter ban
        search_query = search_title if search_title else query
        
        with YoutubeDL(ydl_opts) as ydl:
            # scsearch1 returns the top 1 result from SoundCloud
            info = ydl.extract_info(f"scsearch1:{search_query}", download=False)
            
            if not info or 'entries' not in info or not info['entries']:
                return None
                
            track = info['entries'][0]
            
            return {
                'id': track.get('id', 'N/A'),
                'title': track.get('title', search_query),
                'duration': track.get('duration', 0),
                'url': track.get('url'),
                'thumbnail': track.get('thumbnail', ''),
            }
    except Exception as e:
        print(f"SoundCloud Extraction Error: {e}")
        return None

async def get_yt_info(query: str) -> dict:
    search_title = None
    if query.startswith("http"):
        try:
            # Get the title from YouTube first, then search it on SoundCloud
            video_info = await Video.getInfo(query)
            search_title = video_info.get('title', '')
        except:
            pass

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_yt_info_sync, query, search_title)

async def search_youtube(query: str, limit: int = 1) -> List[Dict]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()
    return result['result']
