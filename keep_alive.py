from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Pallu Music Bot is Alive and Running on Render!"

def run():
    # Render assigns a PORT dynamically, we default to 8080 if not found
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
