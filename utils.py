# utils.py
import random

def is_prime(n):
    """Verifica se um número é primo"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_prime(min_value=100, max_value=1000):
    """Gera um número primo aleatório"""
    while True:
        num = random.randint(min_value, max_value)
        if is_prime(num):
            return num

def generate_base(prime):
    """Gera uma base aleatória menor que o primo"""
    return random.randint(2, prime-1)

def cesar_encrypt(message, key):
    """Cifra uma mensagem usando César"""
    encrypted = ""
    for char in message:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            encrypted += chr((ord(char) - ascii_offset + key) % 26 + ascii_offset)
        else:
            encrypted += char
    return encrypted

def cesar_decrypt(encrypted_message, key):
    """Decifra uma mensagem usando César"""
    return cesar_encrypt(encrypted_message, -key)