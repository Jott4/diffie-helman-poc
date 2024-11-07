# client.py
import socket
import threading
import json
import random
from datetime import datetime

class DiffieHellman:
    def __init__(self):
        self.generate_new_keys()

    def generate_new_keys(self):
        """Gera novos valores para cada mensagem"""
        self.prime = self.generate_prime()
        self.base = random.randint(2, self.prime-1)
        self.private_key = random.randint(1, self.prime-1)
        self.public_key = self.mod_exp(self.base, self.private_key, self.prime)
        self.shared_key = None

    def generate_prime(self, min_val=100, max_val=1000):
        """Gera um número primo aleatório"""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True

        while True:
            num = random.randint(min_val, max_val)
            if is_prime(num):
                return num

    def mod_exp(self, base, exp, mod):
        """Exponenciação modular rápida"""
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result

    def generate_shared_key(self, other_public_key):
        """Gera a chave compartilhada"""
        self.shared_key = self.mod_exp(other_public_key, self.private_key, self.prime)
        return self.shared_key

    def encrypt(self, message):
        """Encripta a mensagem usando César"""
        if not self.shared_key:
            self.generate_shared_key(self.public_key)
        return self.caesar_cipher(message, self.shared_key % 26)

    def decrypt(self, message, shared_key, prime):
        """Decripta a mensagem usando César"""
        self.shared_key = shared_key
        self.prime = prime
        return self.caesar_cipher(message, 26 - (self.shared_key % 26))

    def caesar_cipher(self, text, shift):
        """Implementação da cifra de César"""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - ascii_offset + shift) % 26
                result += chr(shifted + ascii_offset)
            else:
                result += char
        return result

class Client:
    def __init__(self, host='localhost', port=1235):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.diffie_hellman = DiffieHellman()

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                data = json.loads(message)
                
                if 'encryption_type' in data:
                    print("Conectado ao servidor com criptografia Diffie-Hellman")
                    continue

                if 'content' in data:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    encrypted_msg = data['content']
                    shared_key = int(data['shared_key'])
                    prime = int(data['prime'])
                    
                    decrypted_msg = self.diffie_hellman.decrypt(
                        encrypted_msg, 
                        shared_key,
                        prime
                    )
                    
                    print(f"\n[{timestamp}] Mensagem recebida:")
                    print(f"Mensagem cifrada: {encrypted_msg}")
                    print(f"Mensagem decifrada: {decrypted_msg}")
                    print(f"Base: {data['base']}")
                    print(f"Primo: {data['prime']}")
                    print(f"Chave compartilhada: {shared_key}")
            except Exception as e:
                print(f"Erro: {e}")
                break

    def send_message(self, message):
        # Gera novos valores para cada mensagem
        self.diffie_hellman.generate_new_keys()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        encrypted = self.diffie_hellman.encrypt(message)
        
        data = {
            'content': encrypted,
            'base': self.diffie_hellman.base,
            'prime': self.diffie_hellman.prime,
            'public_key': self.diffie_hellman.public_key,
            'shared_key': str(self.diffie_hellman.shared_key)
        }
        
        self.socket.send(json.dumps(data).encode())
        print(f"\n[{timestamp}] Mensagem enviada:")
        print(f"Mensagem original: {message}")
        print(f"Mensagem cifrada: {encrypted}")
        print(f"Base: {self.diffie_hellman.base}")
        print(f"Primo: {self.diffie_hellman.prime}")
        print(f"Chave privada: {self.diffie_hellman.private_key}")
        print(f"Chave pública: {self.diffie_hellman.public_key}")
        print(f"Chave compartilhada: {self.diffie_hellman.shared_key}")

    def start(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            message = input("\nDigite sua mensagem: ")
            if message.lower() == 'sair':
                break
            self.send_message(message)

if __name__ == "__main__":
    client = Client()
    client.start()