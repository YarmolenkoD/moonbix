from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def base64_encode(data):
    return base64.b64encode(data).decode('utf-8')

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours} hours, {minutes} mins, {remaining_seconds} secs"

def encrypt(self, text, key):
    iv = get_random_bytes(12)
    iv_base64 = base64_encode(iv)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv_base64[:16].encode('utf-8'))
    ciphertext = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    ciphertext_base64 = base64_encode(ciphertext)
    return iv_base64 + ciphertext_base64
