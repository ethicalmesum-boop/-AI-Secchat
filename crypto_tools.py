# ============================================
# Crypto Tools - Hash + Encryption + Decryption
# CrackStation-style toolkit
# ============================================

import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


# ============================================
# HASH GENERATOR
# ============================================
def generate_hashes(text):
    """Text ke saare common hashes generate karta hai"""
    if isinstance(text, str):
        text = text.encode()
    
    return {
        "MD5": hashlib.md5(text).hexdigest(),
        "SHA1": hashlib.sha1(text).hexdigest(),
        "SHA256": hashlib.sha256(text).hexdigest(),
        "SHA512": hashlib.sha512(text).hexdigest(),
        "SHA3-256": hashlib.sha3_256(text).hexdigest(),
        "BLAKE2b": hashlib.blake2b(text).hexdigest(),
    }


def hash_file(file_bytes):
    """File ka hash generate karta hai"""
    return generate_hashes(file_bytes)


# ============================================
# HASH CRACKER (Dictionary Attack)
# ============================================
# Common passwords ki wordlist (CrackStation-style)
COMMON_PASSWORDS = [
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    "123123", "baseball", "abc123", "football", "monkey",
    "letmein", "shadow", "master", "666666", "qwertyuiop",
    "123321", "mustang", "1234567890", "michael", "654321",
    "superman", "1qaz2wsx", "7777777", "121212", "000000",
    "qazwsx", "123qwe", "killer", "trustno1", "jordan",
    "jennifer", "zxcvbnm", "asdfgh", "hunter", "buster",
    "soccer", "harley", "batman", "andrew", "tigger",
    "sunshine", "iloveyou", "2000", "charlie", "robert",
    "thomas", "hockey", "ranger", "daniel", "starwars",
    "klaster", "112233", "george", "computer", "michelle",
    "jessica", "pepper", "1111", "zxcvbn", "555555",
    "11111111", "131313", "freedom", "777777", "pass",
    "maggie", "159753", "aaaaaa", "ginger", "princess",
    "joshua", "cheese", "amanda", "summer", "love",
    "ashley", "nicole", "chelsea", "biteme", "matthew",
    "access", "yankees", "987654321", "dallas", "austin",
    "thunder", "taylor", "matrix", "admin", "admin123",
    "root", "toor", "test", "guest", "hello",
    "welcome", "login", "user", "passw0rd", "p@ssw0rd",
]


def crack_hash(target_hash, algorithm="md5"):
    """
    Dictionary attack se hash crack karta hai.
    Common passwords try karta hai.
    """
    target_hash = target_hash.lower().strip()
    
    # Algorithm choose karo
    if algorithm.lower() == "md5":
        hash_func = lambda x: hashlib.md5(x.encode()).hexdigest()
    elif algorithm.lower() == "sha1":
        hash_func = lambda x: hashlib.sha1(x.encode()).hexdigest()
    elif algorithm.lower() == "sha256":
        hash_func = lambda x: hashlib.sha256(x.encode()).hexdigest()
    elif algorithm.lower() == "sha512":
        hash_func = lambda x: hashlib.sha512(x.encode()).hexdigest()
    else:
        return None
    
    # Dictionary attack
    for password in COMMON_PASSWORDS:
        if hash_func(password) == target_hash:
            return password
    
    # Number brute force (0-9999)
    for i in range(10000):
        if hash_func(str(i)) == target_hash:
            return str(i)
    
    return None


def identify_hash(hash_string):
    """Hash type identify karta hai (length se)"""
    hash_string = hash_string.strip()
    length = len(hash_string)
    
    hash_types = {
        32: "MD5",
        40: "SHA1",
        56: "SHA224",
        64: "SHA256",
        96: "SHA384",
        128: "SHA512",
    }
    
    # Check hex
    try:
        int(hash_string, 16)
        return hash_types.get(length, "Unknown")
    except:
        return "Not a valid hash"


# ============================================
# ENCRYPTION
# ============================================
def caesar_encrypt(text, shift=3):
    """Caesar cipher encryption"""
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result


def caesar_decrypt(text, shift=3):
    """Caesar cipher decryption"""
    return caesar_encrypt(text, -shift)


def base64_encrypt(text):
    """Base64 encoding"""
    return base64.b64encode(text.encode()).decode()


def base64_decrypt(text):
    """Base64 decoding"""
    try:
        return base64.b64decode(text.encode()).decode()
    except:
        return "❌ Invalid Base64 string"


def aes_encrypt(text, password):
    """AES encryption with password"""
    # Password se key derive karo
    salt = b'fixed_salt_12345'  # Demo ke liye fixed
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()


def aes_decrypt(encrypted_text, password):
    """AES decryption with password"""
    try:
        salt = b'fixed_salt_12345'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        return f.decrypt(encrypted_text.encode()).decode()
    except:
        return "❌ Wrong password or invalid ciphertext"


# ============================================
# REVERSE + ROT13 + HEX
# ============================================
def reverse_text(text):
    return text[::-1]


def rot13(text):
    return caesar_encrypt(text, 13)


def hex_encode(text):
    return text.encode().hex()


def hex_decode(text):
    try:
        return bytes.fromhex(text).decode()
    except:
        return "❌ Invalid hex string"