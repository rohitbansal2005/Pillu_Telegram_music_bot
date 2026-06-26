# Simple in-memory queue management
# Keys are chat IDs, values are lists of dicts containing song info
import asyncio

music_queues = {}
active_progress_tasks = {}

def add_to_queue(chat_id: int, song_info: dict):
    if chat_id not in music_queues:
        music_queues[chat_id] = []
    music_queues[chat_id].append(song_info)

def get_queue(chat_id: int) -> list:
    return music_queues.get(chat_id, [])

def pop_from_queue(chat_id: int) -> dict:
    if chat_id in music_queues and len(music_queues[chat_id]) > 0:
        return music_queues[chat_id].pop(0)
    return None

def clear_queue(chat_id: int):
    if chat_id in music_queues:
        music_queues[chat_id] = []

def remove_from_queue(chat_id: int):
    if chat_id in music_queues:
        del music_queues[chat_id]
