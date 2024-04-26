from utils.globals import BOT
from handlers import command_handler
import json

if __name__ == '__main__':
    BOT.polling()

    from utils.globals import LOGGED_IN, CHAT_ID, CURRENT_USER
    print(f"Leállítás...\nLOGGED_IN = {LOGGED_IN}\nCHAT_ID = {CHAT_ID}")

    if LOGGED_IN:
        with open("session_dump.json", "w") as f:
            session_info = {
                    "chat_id": CHAT_ID,
                    "user_id": CURRENT_USER.user_id
            }
            json.dump(session_info, f, indent=4)