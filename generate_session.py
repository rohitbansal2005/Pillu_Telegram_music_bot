import asyncio
from pyrogram import Client

async def generate():
    print("Welcome to Pallu Music Bot Session Generator!")
    print("---------------------------------------------")
    
    try:
        api_id = int(input("Enter your API_ID: "))
        api_hash = input("Enter your API_HASH: ")
        
        print("\nGenerating session... (You will receive an OTP on Telegram)")
        
        async with Client("assistant_session", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
            session_string = await app.export_session_string()
            print("\n✅ Successfully Generated Session String!")
            print("=====================================================")
            print(session_string)
            print("=====================================================")
            print("⚠️ DO NOT share this string with anyone. Paste it in your .env file as SESSION_STRING.")
            
            # Optionally send it to saved messages
            try:
                await app.send_message("me", f"**Pallu Music Assistant Session String:**\n\n`{session_string}`\n\n⚠️ DO NOT SHARE THIS WITH ANYONE.")
                print("\n(The session string has also been sent to your Telegram Saved Messages!)")
            except Exception:
                pass
                
    except ValueError:
        print("\n❌ Error: API_ID must be a number!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(generate())
