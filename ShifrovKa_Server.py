# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, font
import socket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import binascii
import json

AES_KEY = b"ShifrovKaSecret!"  # 16 байт
AES_BLOCK_SIZE = 16

class ShifrovKaServer:
    def __init__(self, root):
        self.root = root
        self.root.title("ShifrovKa Server — AES CBC")
        self.root.geometry("700x600")
        self.root.configure(bg="#f9f9f9")

        self.text_font = font.Font(family="Consolas", size=11)
        self.title_font = font.Font(family="Segoe UI", size=13, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=11)

        tk.Label(root, text="Журнал обмена:", bg="#f9f9f9", fg="#2e2e2e", font=self.title_font).pack(pady=10)

        self.output = scrolledtext.ScrolledText(root, height=25, width=80, font=self.text_font,
                                                bg="#ffffff", fg="#2e2e2e", borderwidth=1, relief="solid")
        self.output.pack(padx=10)

        # Кнопки
        self.button_frame = tk.Frame(root, bg="#f9f9f9")
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Запустить сервер", command=self.start_server,
                                      bg="#dddddd", fg="#2e2e2e", font=self.button_font, relief="flat", width=20)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(self.button_frame, text="Остановить сервер", command=self.stop_server,
                                     bg="#dddddd", fg="#2e2e2e", font=self.button_font, relief="flat", width=20, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10)

        self.running = False
        self.server_socket = None

    def start_server(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.run_server, daemon=True).start()
        self.output.insert(tk.END, "[SERVER] Сервер запущен на 127.0.0.1:12345\n")

    def stop_server(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.output.insert(tk.END, "[SERVER] Сервер остановлен.\n")

    def run_server(self):
        host = "127.0.0.1"
        port = 12345
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, addr = self.server_socket.accept()
                    self.output.insert(tk.END, f"[CONNECT] {addr} подключился\n")
                    threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
                except socket.timeout:
                    continue
        except Exception as e:
            self.output.insert(tk.END, f"[ERROR] {e}\n")
            self.stop_server()

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(4096)
            if not data:
                return

            decoded = data.decode("utf-8")
            payload = json.loads(decoded)
            command = payload.get("command")
            message = payload.get("message")

            if command == "ENCRYPT":
                iv = get_random_bytes(AES_BLOCK_SIZE)
                cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
                encrypted = cipher.encrypt(pad(message.encode('utf-8'), AES_BLOCK_SIZE))
                hex_data = binascii.hexlify(iv + encrypted).decode()

                client_socket.sendall(hex_data.encode("utf-8"))
                self.output.insert(tk.END, f"[ENCRYPT] Исходный текст: {message}\n")
                self.output.insert(tk.END, f"[ENCRYPT] HEX: {hex_data}\n\n")

            elif command == "DECRYPT":
                raw = binascii.unhexlify(message)
                iv = raw[:AES_BLOCK_SIZE]
                ciphertext = raw[AES_BLOCK_SIZE:]
                cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
                decrypted = unpad(cipher.decrypt(ciphertext), AES_BLOCK_SIZE).decode('utf-8')

                client_socket.sendall(decrypted.encode("utf-8"))
                self.output.insert(tk.END, f"[DECRYPT] HEX: {message}\n")
                self.output.insert(tk.END, f"[DECRYPT] Расшифровка: {decrypted}\n\n")

            else:
                client_socket.sendall("Неизвестная команда.".encode("utf-8"))
                self.output.insert(tk.END, "[ERROR] Неизвестная команда\n")

        except Exception as e:
            self.output.insert(tk.END, f"[ERROR] {str(e)}\n")
        finally:
            client_socket.close()

# Запуск GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ShifrovKaServer(root)
    root.mainloop()
