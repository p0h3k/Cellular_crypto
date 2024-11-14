import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import random
from encrypt import encrypt_message
from decrypt import decrypt_message
import lfsr as lfsr_module

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cellular Automaton Crypto")
        self.geometry("600x850")

        self.mode = tk.StringVar(value="encrypt")
        self.automata_params = []

        self.create_widgets()

    def create_widgets(self):
        # Выбор режима
        tk.Label(self, text="Выберите режим:").pack(anchor=tk.W)
        modes = [("Encrypt (Custom/Generated)", "encrypt"),
                 ("Decrypt", "decrypt"),
                 ("Encrypt with Key", "key_encrypt")]
        for text, mode in modes:
            tk.Radiobutton(self, text=text, variable=self.mode, value=mode, command=self.clear_entries).pack(anchor=tk.W)

        # Выбор файла
        tk.Button(self, text="Выбрать файл", command=self.load_file).pack()
        self.file_label = tk.Label(self, text="", wraplength=500)
        self.file_label.pack()

        # Отображение сообщения
        tk.Label(self, text="Сообщение:").pack(anchor=tk.W)
        self.message_text = tk.Text(self, height=10, wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True)

        # Ввод параметров
        self.param_frame = tk.Frame(self)
        self.param_frame.pack()
        self.create_param_widgets()

        # Кнопка выполнения
        tk.Button(self, text="Выполнить", command=self.execute_action).pack()

        # Отображение результата
        tk.Label(self, text="Результат:").pack(anchor=tk.W)
        self.result_text = tk.Text(self, height=5, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Отображение ключа
        tk.Label(self, text="Ключ шифрования:").pack(anchor=tk.W)
        self.key_text = tk.Text(self, height=5, wrap=tk.WORD)
        self.key_text.pack(fill=tk.BOTH, expand=True)

        # Отображение потоковой последовательности
        tk.Label(self, text="Ключевая последовательность (keystream):").pack(anchor=tk.W)
        self.keystream_text = tk.Text(self, height=5, wrap=tk.WORD)
        self.keystream_text.pack(fill=tk.BOTH, expand=True)

    def create_param_widgets(self):
        tk.Button(self.param_frame, text="Настроить параметры шифрования", command=self.configure_encryption_params).pack()

    def clear_entries(self):
        self.message_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.key_text.delete(1.0, tk.END)
        self.keystream_text.delete(1.0, tk.END)

    def load_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.file_label.config(text=filepath)
            try:
                # Открываем файл, читаем часть и сразу закрываем
                with open(filepath, 'r', encoding='utf-8') as file:
                    max_chars = 1024  # Example limit for characters to display
                    data = file.read(max_chars)
                    self.message_text.delete(1.0, tk.END)
                    self.message_text.insert(tk.END, data + ('\n\n... (Кусок файла)' if len(data) == max_chars else ''))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def configure_encryption_params(self):
        num_automata = simpledialog.askinteger("Количество автоматов", "Введите количество автоматов:")
        if num_automata is None:
            return

        self.automata_params = []

        rule_choices_1d = ['rule_30', 'rule_90', 'rule_150']
        rule_choices_2d = ['complex_rule_1', 'complex_rule_2', 'complex_rule_3']

        for i in range(num_automata):
            automaton_type = simpledialog.askstring("Тип автомата", f"Выберите тип автомата {i+1} (1D, 2D):")
            if automaton_type == '1D':
                rule = simpledialog.askstring("Правило 1D", f"Выберите правило для автомата {i+1} (rule_30, rule_90, rule_150):")
            else:
                rule = simpledialog.askstring("Правило 2D", f"Выберите правило для автомата {i+1} (complex_rule_1, complex_rule_2, complex_rule_3):")

            use_random_seed = messagebox.askyesno("Случайное начальное состояние", f"Использовать случайное начальное состояние для автомата {i+1}?")
            seed = random.getrandbits(32) if use_random_seed else simpledialog.askinteger("Начальное состояние", f"Введите начальное состояние для автомата {i+1}:")
            self.automata_params.append((rule, seed))

        block_size = simpledialog.askinteger("Размер блока", "Введите размер блока для шифрования:")
        use_random_lfsr_seed = messagebox.askyesno("Случайное начальное состояние LFSR", "Использовать случайное начальное состояние для LFSR?")
        lfsr_seed = random.getrandbits(32) if use_random_lfsr_seed else simpledialog.askinteger("Начальное состояние LFSR", "Введите начальное состояние LFSR:")
        taps_input = simpledialog.askstring("Биты сдвига LFSR", "Введите биты сдвига LFSR через запятую или оставьте пустым для случайного:")
        taps = list(map(int, taps_input.split(','))) if taps_input else lfsr_module.generate_random_taps(block_size)

        self.key_details = json.dumps({
            "rules": [x[0] for x in self.automata_params],
            "seeds": [x[1] for x in self.automata_params],
            "lfsr_seed": lfsr_seed,
            "taps": taps,
            "block_size": block_size
        })

        self.key_text.delete(1.0, tk.END)
        self.key_text.insert(tk.END, self.key_details)

    def execute_action(self):
        message = self.message_text.get(1.0, tk.END).strip()
        mode = self.mode.get()

        try:
            if mode == "encrypt":
                key_details = self.key_details if hasattr(self, 'key_details') else None
                encrypted_base64, key_details, keystream = encrypt_message(message, key_details=key_details, return_keystream=True)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, encrypted_base64)
                self.keystream_text.delete(1.0, tk.END)
                self.keystream_text.insert(tk.END, ''.join(map(str, keystream)))
                with open("encrypt.txt", 'w', encoding='utf-8') as f:
                    f.write(encrypted_base64 + "\n")
                with open("encryption_keystream.txt", 'w', encoding='utf-8') as f:
                    f.write(''.join(map(str, keystream)))
                self.key_text.delete(1.0, tk.END)
                self.key_text.insert(tk.END, key_details)
            elif mode == "decrypt":
                key_details = self.key_text.get(1.0, tk.END).strip()
                decrypted_message = decrypt_message(message, key_details)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, decrypted_message)
                with open("decrypt.txt", 'w', encoding='utf-8') as f:
                    f.write(decrypted_message)
            elif mode == "key_encrypt":
                key_details = self.key_text.get(1.0, tk.END).strip()
                encrypted_base64, _, keystream = encrypt_message(message, key_details=key_details, return_keystream=True)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, encrypted_base64)
                self.keystream_text.delete(1.0, tk.END)
                self.keystream_text.insert(tk.END, ''.join(map(str, keystream)))
                with open("encrypt.txt", 'w', encoding='utf-8') as f:
                    f.write(encrypted_base64 + "\n")
                with open("encryption_keystream.txt", 'w', encoding='utf-8') as f:
                    f.write(''.join(map(str, keystream)))
            else:
                messagebox.showerror("Ошибка", "Выберите корректный режим.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения: {e}")

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
