import json
from paybrobot.utils.globals import BOT
from paybrobot.main import top_level_commands


def main():
    BOT.polling()

    from paybrobot.utils.globals import LOGGED_IN, CHAT_ID, CURRENT_USER
    print(f"Leállítás...\nLOGGED_IN = {LOGGED_IN}\nCHAT_ID = {CHAT_ID}")

    if LOGGED_IN:
        with open("paybrobot/session_dump.json", "w", encoding='utf-8') as f:
            session_info = {
                "chat_id": CHAT_ID,
                "user_id": CURRENT_USER.user_id
            }
            json.dump(session_info, f, indent=4)
