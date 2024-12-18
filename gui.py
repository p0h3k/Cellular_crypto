import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
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
        # Очищаем ключ только при смене режима
        if self.mode.get() != 'decrypt':
            self.key_text.delete(1.0, tk.END)
        self.keystream_text.delete(1.0, tk.END)

    def load_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.file_label.config(text=filepath)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    max_chars = 1024  # Пример ограничения на количество символов для отображения
                    data = file.read(max_chars)
                    self.message_text.delete(1.0, tk.END)
                    self.message_text.insert(tk.END, data)
            except UnicodeDecodeError:
                # Если не удалось прочитать файл в кодировке utf-8, пробуем cp1251
                try:
                    with open(filepath, 'r', encoding='cp1251') as file:
                        data = file.read(max_chars)
                        self.message_text.delete(1.0, tk.END)
                        self.message_text.insert(tk.END, data)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def configure_encryption_params(self):
        # Создаем новое окно для ввода параметров
        self.param_window = tk.Toplevel(self)
        self.param_window.title("Параметры шифрования")

        row = 0

        # Количество автоматов
        tk.Label(self.param_window, text="Количество автоматов:").grid(row=row, column=0, sticky=tk.W)
        self.num_automata_var = tk.StringVar()
        tk.Entry(self.param_window, textvariable=self.num_automata_var).grid(row=row, column=1)
        row += 1

        # Кнопка для генерации полей автоматов
        tk.Button(self.param_window, text="Задать параметры автоматов", command=self.generate_automata_entries).grid(row=row, column=0, columnspan=2)
        row += 1

        # Фрейм для параметров автоматов
        self.automata_frame = tk.Frame(self.param_window)
        self.automata_frame.grid(row=row, column=0, columnspan=2)
        row += 1

        # Размер блока
        tk.Label(self.param_window, text="Размер блока:").grid(row=row, column=0, sticky=tk.W)
        self.block_size_var = tk.StringVar()
        tk.Entry(self.param_window, textvariable=self.block_size_var).grid(row=row, column=1)
        row += 1

        # Начальное состояние LFSR
        tk.Label(self.param_window, text="Начальное состояние LFSR:").grid(row=row, column=0, sticky=tk.W)
        self.lfsr_seed_var = tk.StringVar()
        tk.Entry(self.param_window, textvariable=self.lfsr_seed_var).grid(row=row, column=1)
        row += 1

        # Биты сдвига LFSR
        tk.Label(self.param_window, text="Биты сдвига LFSR:").grid(row=row, column=0, sticky=tk.W)
        self.lfsr_taps_var = tk.StringVar()
        tk.Entry(self.param_window, textvariable=self.lfsr_taps_var).grid(row=row, column=1)
        row += 1

        # Кнопки OK и Cancel
        tk.Button(self.param_window, text="OK", command=self.save_encryption_params).grid(row=row, column=0)
        tk.Button(self.param_window, text="Cancel", command=self.param_window.destroy).grid(row=row, column=1)

    def generate_automata_entries(self):
        # Очищаем предыдущие записи
        for widget in self.automata_frame.winfo_children():
            widget.destroy()

        try:
            num_automata = int(self.num_automata_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество автоматов.")
            return

        self.automata_entries = []

        for i in range(num_automata):
            row = i * 4
            tk.Label(self.automata_frame, text=f"Автомат {i+1} тип:").grid(row=row, column=0, sticky=tk.W)
            automaton_type_var = tk.StringVar()
            automaton_type_combobox = ttk.Combobox(self.automata_frame, textvariable=automaton_type_var)
            automaton_type_combobox['values'] = ('1D', '2D')
            automaton_type_combobox.grid(row=row, column=1)

            row += 1
            tk.Label(self.automata_frame, text=f"Автомат {i+1} правило:").grid(row=row, column=0, sticky=tk.W)
            rule_var = tk.StringVar()
            rule_combobox = ttk.Combobox(self.automata_frame, textvariable=rule_var)
            rule_combobox.grid(row=row, column=1)

            # Обновляем список правил при выборе типа автомата
            def update_rule_options(event, rule_combobox=rule_combobox, automaton_type_var=automaton_type_var):
                automaton_type = automaton_type_var.get()
                if automaton_type == '1D':
                    rule_combobox['values'] = ['rule_30', 'rule_90', 'rule_150']
                elif automaton_type == '2D':
                    rule_combobox['values'] = ['complex_rule_1', 'complex_rule_2', 'complex_rule_3']
                else:
                    rule_combobox.set('')
                    rule_combobox['values'] = []

            automaton_type_combobox.bind('<<ComboboxSelected>>', update_rule_options)

            row += 1
            tk.Label(self.automata_frame, text=f"Автомат {i+1} начальное состояние:").grid(row=row, column=0, sticky=tk.W)
            seed_var = tk.StringVar()
            tk.Entry(self.automata_frame, textvariable=seed_var).grid(row=row, column=1)

            self.automata_entries.append((automaton_type_var, rule_var, seed_var))

    def save_encryption_params(self):
        # Собираем параметры
        try:
            num_automata = int(self.num_automata_var.get())
            if num_automata <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество автоматов.")
            return

        self.automata_params = []

        for automaton_type_var, rule_var, seed_var in self.automata_entries:
            automaton_type = automaton_type_var.get().strip()
            rule = rule_var.get().strip()
            seed = seed_var.get().strip()

            # Если тип автомата или правило не указаны, генерируем случайные
            if not automaton_type:
                automaton_type = random.choice(['1D', '2D'])

            if not rule or rule == '':
                if automaton_type == '1D':
                    rule = random.choice(['rule_30', 'rule_90', 'rule_150'])
                else:
                    rule = random.choice(['complex_rule_1', 'complex_rule_2', 'complex_rule_3'])
            else:
                # Проверяем, что выбранное правило соответствует типу автомата
                if automaton_type == '1D' and rule not in ['rule_30', 'rule_90', 'rule_150']:
                    messagebox.showerror("Ошибка", f"Недопустимое правило {rule} для автомата 1D.")
                    return
                elif automaton_type == '2D' and rule not in ['complex_rule_1', 'complex_rule_2', 'complex_rule_3']:
                    messagebox.showerror("Ошибка", f"Недопустимое правило {rule} для автомата 2D.")
                    return

            if not seed:
                seed = random.getrandbits(32)
            else:
                try:
                    seed = int(seed)
                except ValueError:
                    messagebox.showerror("Ошибка", "Начальное состояние автомата должно быть целым числом.")
                    return

            self.automata_params.append((rule, seed))

        # Размер блока
        block_size_str = self.block_size_var.get().strip()
        if block_size_str:
            try:
                block_size = int(block_size_str)
                if block_size <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Размер блока должен быть положительным целым числом.")
                return
        else:
            block_size = 32  # Значение по умолчанию

        # Начальное состояние LFSR
        lfsr_seed_str = self.lfsr_seed_var.get().strip()
        if lfsr_seed_str:
            try:
                lfsr_seed = int(lfsr_seed_str)
                if lfsr_seed < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Начальное состояние LFSR должно быть неотрицательным целым числом.")
                return
        else:
            lfsr_seed = random.getrandbits(block_size)

        # Биты сдвига LFSR
        lfsr_taps_str = self.lfsr_taps_var.get().strip()
        if lfsr_taps_str:
            try:
                taps = list(map(int, lfsr_taps_str.split(',')))
                if not taps:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Биты сдвига LFSR должны быть числами, разделенными запятыми.")
                return
        else:
            taps = lfsr_module.generate_random_taps(block_size)

        self.key_details = json.dumps({
            "rules": [x[0] for x in self.automata_params],
            "seeds": [x[1] for x in self.automata_params],
            "lfsr_seed": lfsr_seed,
            "taps": taps,
            "block_size": block_size
        })

        self.key_text.delete(1.0, tk.END)
        self.key_text.insert(tk.END, self.key_details)

        self.param_window.destroy()

    def execute_action(self):
        message = self.message_text.get(1.0, tk.END).strip()
        mode = self.mode.get()

        try:
            if mode == "encrypt":
                key_details = self.key_text.get(1.0, tk.END).strip()
                if not key_details:
                    key_details = getattr(self, 'key_details', None)
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
                if not key_details:
                    messagebox.showerror("Ошибка", "Ключ для расшифровки пустой.")
                    return
                decrypted_message = decrypt_message(message, key_details)
                # Проверяем и декодируем сообщение при необходимости
                if isinstance(decrypted_message, bytes):
                    # Сохраняем расшифрованные байты для диагностики
                    with open("decrypted_bytes.bin", "wb") as f:
                        f.write(decrypted_message)
                    # Пытаемся декодировать с разными кодировками
                    for encoding in ('utf-8', 'cp1251', 'latin1'):
                        try:
                            decrypted_message = decrypted_message.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # Если не удалось декодировать, сообщаем об ошибке
                        messagebox.showerror("Ошибка", f"Не удалось декодировать расшифрованное сообщение. Расшифрованные байты сохранены в 'decrypted_bytes.bin'.")
                        return
                elif not isinstance(decrypted_message, str):
                    messagebox.showerror("Ошибка", "Неверный формат расшифрованного сообщения.")
                    return
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, decrypted_message)
                with open("decrypt.txt", 'w', encoding='utf-8') as f:
                    f.write(decrypted_message)
            elif mode == "key_encrypt":
                key_details = self.key_text.get(1.0, tk.END).strip()
                if not key_details:
                    messagebox.showerror("Ошибка", "Ключ для шифрования пустой.")
                    return
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
