import random
import time
import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from bot.config import settings

def encrypt(text, key):
    iv = get_random_bytes(12)
    iv_base64 = base64.b64encode(iv).decode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv_base64[:16].encode("utf-8"))

    def pad(s):
        block_size = AES.block_size
        return s + (block_size - len(s) % block_size) * chr(
            block_size - len(s) % block_size
        )

    padded_text = pad(text).encode("utf-8")
    encrypted = cipher.encrypt(padded_text)
    encrypted_base64 = base64.b64encode(encrypted).decode("utf-8")

    return iv_base64 + encrypted_base64


def generate_game_data(game: dict):
    start_time = int(time.time() * 1000)
    end_time = start_time + 45000  # 45 seconds in milliseconds
    game_tag = game["data"]["gameTag"]
    item_settings = game["data"]["cryptoMinerConfig"]["itemSettingList"]

    current_time = start_time
    score = 100
    game_events = []

    while current_time < end_time:
        # Generate random time increment
        time_increment = random.randint(1500, 2500)
        current_time += time_increment

        if current_time >= end_time:
            break

        # Generate random hook positions and angles
        hook_pos_x = round(random.uniform(75, 275), 3)
        hook_pos_y = round(random.uniform(199, 251), 3)
        hook_shot_angle = round(random.uniform(-1, 1), 3)
        hook_hit_x = round(random.uniform(100, 400), 3)
        hook_hit_y = round(random.uniform(250, 700), 3)

        # Determine item type, size, and points
        item_type, item_size, points = 0, 0, 0
        random_value = random.random()

        if random_value < 0.6:
            # Select a reward item
            reward_items = [item for item in item_settings if item["type"] == "REWARD"]
            selected_reward = random.choice(reward_items)
            item_type = 1
            item_size = selected_reward["size"]
            points = min(selected_reward["rewardValueList"][0], 10)
            score = min(score + points, settings.MAX_GAME_POINTS)
        elif random_value < 0.8:
            # Select a trap item
            trap_items = [item for item in item_settings if item["type"] == "TRAP"]
            selected_trap = random.choice(trap_items)
            item_type = 1
            item_size = selected_trap["size"]
            points = min(abs(selected_trap["rewardValueList"][0]), 20)
            score = max(100, score - points)
        else:
            # Select a bonus item
            bonus_item = next(
                (item for item in item_settings if item["type"] == "BONUS"), None
            )
            if bonus_item:
                item_type = 2
                item_size = bonus_item["size"]
                points = min(bonus_item["rewardValueList"][0], 15)
                score = min(score + points, settings.MAX_GAME_POINTS)

        # Create event data string
        event_data = f"{current_time}|{hook_pos_x}|{hook_pos_y}|{hook_shot_angle}|{hook_hit_x}|{hook_hit_y}|{item_type}|{item_size}|{points}"
        game_events.append(event_data)

    payload = ";".join(game_events)
    encrypted_payload = encrypt(payload, game_tag.encode("utf-8"))

    return {
        'log': score,
        'payload': encrypted_payload
    }