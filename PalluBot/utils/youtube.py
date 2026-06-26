import asyncio
from typing import Dict, List, Tuple
from pytubefix import YouTube, Search
from youtubesearchpython.__future__ import VideosSearch

def get_yt_info_sync(query: str) -> dict:
    try:
        if query.startswith("http"):
            yt = YouTube(query, client='WEB')
        else:
            search = Search(query)
            if not search.videos:
                return None
            yt = search.videos[0]
            
        audio_stream = yt.streams.get_audio_only()
        if not audio_stream:
            return None
            
        return {
            'id': yt.video_id,
            'title': yt.title,
            'duration': yt.length,
            'url': audio_stream.url,
            'thumbnail': yt.thumbnail_url,
        }
    except Exception as e:
        print(f"PyTubeFix Error: {e}")
        return None

async def get_yt_info(query: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_yt_info_sync, query)

async def search_youtube(query: str, limit: int = 1) -> List[Dict]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()
    return result['result']
