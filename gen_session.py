import asyncio
from pyrogram import Client

async def generate_session():
    print("Welcome to the Pyrogram Session Generator!")
    print("You will need your API_ID and API_HASH from my.telegram.org\n")
    
    api_id = input("Enter your API_ID: ")
    api_hash = input("Enter your API_HASH: ")
    
    # We use in-memory session so it doesn't create a .session file, just prints the string
    app = Client("my_account", api_id=api_id, api_hash=api_hash, in_memory=True)
    
    await app.start()
    
    session_string = await app.export_session_string()
    
    print("\n\n✅ GENERATED SUCCESSFULLY ✅")
    print("Here is your Session String. Copy it and paste it in your .env file:")
    print("------------------------------------------------------------------")
    print(session_string)
    print("------------------------------------------------------------------")
    print("⚠️ DO NOT SHARE THIS STRING WITH ANYONE! ⚠️")
    
    await app.stop()

if __name__ == "__main__":
    asyncio.run(generate_session())
