# server.py
import socket
import threading
import json

class Server:
    def __init__(self, host='localhost', port=1235):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients = []
        print(f"Servidor iniciado em {host}:{port}")

    def handle_client(self, client_socket, addr):
        # Envia mensagem inicial com tipo de criptografia
        initial_message = {
            "encryption_type": "DiffieHellman"
        }
        client_socket.send(json.dumps(initial_message).encode())

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                
                # Tenta ler a mensagem (servidor não consegue decifrar)
                data = json.loads(message)
                print(f"\nServidor recebeu mensagem cifrada: {data['content']}")
                print(f"Servidor não pode decifrar pois não tem acesso à chave compartilhada!")
                
                # Encaminha mensagem para outros clientes
                for client in self.clients:
                    if client != client_socket:
                        client.send(message.encode())
            except:
                break

        self.clients.remove(client_socket)
        client_socket.close()
        print(f"Cliente {addr} desconectado")

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            self.clients.append(client_socket)
            print(f"Cliente conectado: {addr}")
            
            thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.start()