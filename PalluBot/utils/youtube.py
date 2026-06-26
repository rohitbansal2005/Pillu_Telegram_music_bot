import os
import asyncio
import requests
import base64
import html
from typing import Dict, List, Tuple
from youtubesearchpython.__future__ import VideosSearch, Video
from pyDes import des, ECB, PAD_PKCS5

def decrypt_jiosaavn_url(url: str) -> str:
    try:
        des_cipher = des(b'38346591', ECB, b'\0\0\0\0\0\0\0\0', pad=None, padmode=PAD_PKCS5)
        enc_url = base64.b64decode(url.strip())
        dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
        return dec_url.replace('_96.mp4', '_160.mp4')
    except Exception as e:
        print("Decryption Error:", e)
        return ""

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
        
        # 2. Get song details and encrypted URL
        details_res = requests.get(f"https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids={song_id}")
        details = details_res.json()
        
        if song_id not in details:
            return None
            
        song_data = details[song_id]
        enc_url = song_data.get('encrypted_media_url', '')
        
        if not enc_url:
            return None
            
        # 3. Decrypt the URL
        full_url = decrypt_jiosaavn_url(enc_url)
        
        # Convert duration to standard format if needed
        duration = song_data.get('duration', '0')
        title = html.unescape(song_data.get('title', search_query))
        
        return {
            'id': song_id,
            'title': title,
            'duration': duration,
            'url': full_url,
            'thumbnail': song_data.get('image', '').replace('150x150', '500x500'),
        }
    except Exception as e:
        print(f"JioSaavn Extraction Error: {e}")
        return None

import re

def clean_title(title: str) -> str:
    if not title:
        return ""
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title)
    words_to_remove = ['official', 'video', 'lyrical', 'hd', '4k', '8k', 'audio', 'full song', 't-series', 'tseries']
    for word in words_to_remove:
        title = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE).sub('', title)
    title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    words = title.split()
    if len(words) > 5:
        title = ' '.join(words[:5])
    return title.strip()

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
            
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_yt_info_sync, query, search_title)

async def search_youtube(query: str, limit: int = 1) -> List[Dict]:
    search = VideosSearch(query, limit=limit)
    result = await search.next()
    return result['result']
