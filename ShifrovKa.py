# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import socket
import json

class ShifrovKaClient:
    def __init__(self, root):
        self.root = root
        self.root.title("ShifrovKa — Клиент AES")
        self.root.geometry("700x600")
        self.root.configure(bg="#f9f9f9")  # светлый фон

        self.text_font = font.Font(family="Consolas", size=11)
        self.title_font = font.Font(family="Segoe UI", size=13, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=11)

        # Ввод текста
        tk.Label(root, text="Введите текст или HEX:", bg="#f9f9f9", fg="#2e2e2e",
                 font=self.title_font).pack(pady=(10, 5))
        self.input_text = scrolledtext.ScrolledText(root, height=7, width=80, font=self.text_font,
                                                    bg="#ffffff", fg="#2e2e2e", insertbackground="black",
                                                    borderwidth=1, relief="solid")
        self.input_text.pack(padx=10, pady=(0, 10))

        # Кнопки
        self.button_frame = tk.Frame(root, bg="#f9f9f9")
        self.button_frame.pack(pady=5)

        self.encrypt_button = tk.Button(self.button_frame, text="Зашифровать", command=self.send_encrypt,
                                        bg="#dddddd", fg="#2e2e2e", font=self.button_font,
                                        relief="flat", width=20)
        self.encrypt_button.grid(row=0, column=0, padx=10)

        self.decrypt_button = tk.Button(self.button_frame, text="Расшифровать", command=self.send_decrypt,
                                        bg="#dddddd", fg="#2e2e2e", font=self.button_font,
                                        relief="flat", width=20)
        self.decrypt_button.grid(row=0, column=1, padx=10)

        # Вывод результата
        tk.Label(root, text="Результат шифрования/дешифрования:", bg="#f9f9f9", fg="#2e2e2e",
                 font=self.title_font).pack(pady=(20, 5))
        self.result_text = scrolledtext.ScrolledText(root, height=7, width=80, font=self.text_font,
                                                     bg="#ffffff", fg="#2e2e2e", borderwidth=1,
                                                     relief="solid")
        self.result_text.pack(padx=10, pady=(0, 20))

    def send_request(self, command):
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Пусто", "Введите текст или HEX.")
            return

        payload = {
            "command": command,
            "message": message
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 12345))
                s.sendall(json.dumps(payload).encode("utf-8"))
                response = s.recv(4096).decode("utf-8")

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, response)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу:\n{e}")

    def send_encrypt(self):
        self.send_request("ENCRYPT")

    def send_decrypt(self):
        self.send_request("DECRYPT")

# Запуск GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ShifrovKaClient(root)
    root.mainloop()
