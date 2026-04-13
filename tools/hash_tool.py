import hashlib
import os

def generate_hashes(text):
    return {
        "MD5": hashlib.md5(text.encode()).hexdigest(),
        "SHA1": hashlib.sha1(text.encode()).hexdigest(),
        "SHA256": hashlib.sha256(text.encode()).hexdigest()
    }


def detect_hash_type(hash_value):
    length = len(hash_value)

    if length == 32:
        return "MD5"
    elif length == 40:
        return "SHA1"
    elif length == 64:
        return "SHA256"
    return "Unknown"


def crack_hash(hash_value):
    try:
        wordlist_path = os.path.join(os.path.dirname(__file__), "wordlist.txt")
        hash_type = detect_hash_type(hash_value)

        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as file:
            for word in file:
                word = word.strip()

                if hash_type == "MD5":
                    if hashlib.md5(word.encode()).hexdigest() == hash_value:
                        return f"[CRACKED] MD5 → {word}"

                elif hash_type == "SHA1":
                    if hashlib.sha1(word.encode()).hexdigest() == hash_value:
                        return f"[CRACKED] SHA1 → {word}"

                elif hash_type == "SHA256":
                    if hashlib.sha256(word.encode()).hexdigest() == hash_value:
                        return f"[CRACKED] SHA256 → {word}"

        return f"[!] Not found in wordlist (Type: {hash_type})"

    except Exception as e:
        return str(e)