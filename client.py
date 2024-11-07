# client.py
import socket
import threading
import json
import random
from datetime import datetime

class DiffieHellman:
    def __init__(self):
        self.base = 5
        self.prime = 23
        self.private_key = random.randint(1, 20)
        self.public_key = self.mod_exp(self.base, self.private_key, self.prime)
        self.shared_key = None

    def mod_exp(self, base, exp, mod):
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result

    def generate_shared_key(self, other_public_key):
        if not self.shared_key:
            self.shared_key = self.mod_exp(other_public_key, self.private_key, self.prime)
        return self.shared_key

    def encrypt(self, message):
        if not self.shared_key:
            self.generate_shared_key(self.public_key)
        return self.caesar_cipher(message, self.shared_key % 26)

    def decrypt(self, message, key=None):
        if key:
            self.shared_key = int(key)
        if not self.shared_key:
            self.generate_shared_key(self.public_key)
        return self.caesar_cipher(message, 26 - (self.shared_key % 26))

    def caesar_cipher(self, text, shift):
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
        print(f"\nCliente iniciado com:")
        print(f"Chave privada: {self.diffie_hellman.private_key}")
        print(f"Chave pública: {self.diffie_hellman.public_key}")

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
                    decrypted_msg = self.diffie_hellman.decrypt(
                        encrypted_msg, 
                        data.get('encryption_key')
                    )
                    print(f"\n[{timestamp}] Mensagem recebida:")
                    print(f"Mensagem cifrada: {encrypted_msg}")
                    print(f"Mensagem decifrada: {decrypted_msg}")
                    print(f"Chave compartilhada usada: {self.diffie_hellman.shared_key}")
            except Exception as e:
                print(f"Erro: {e}")
                break

    def send_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        encrypted = self.diffie_hellman.encrypt(message)
        data = {
            'content': encrypted,
            'encryption_key': str(self.diffie_hellman.shared_key)
        }
        
        self.socket.send(json.dumps(data).encode())
        print(f"\n[{timestamp}] Mensagem enviada:")
        print(f"Mensagem original: {message}")
        print(f"Mensagem cifrada: {encrypted}")
        print(f"Chave compartilhada usada: {self.diffie_hellman.shared_key}")

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