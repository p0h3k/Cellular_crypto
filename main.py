# main.py

import json
from encrypt import encrypt_message
from decrypt import decrypt_message

def main():
    choice = input("Выберите действие: (E)ncrypt, (D)ecrypt, (K)ey encrypt: ").strip().lower()
    if choice == 'e':
        filename = input("Введите имя файла с вашим сообщением: ").strip()
        with open(filename, 'r', encoding='utf-8') as f:
            message = f.read()
        
        encrypted_base64, key_details = encrypt_message(message)
        with open("encrypt.txt", 'w', encoding='utf-8') as f:
            f.write(encrypted_base64 + "\n")
        
        print("Зашифрованное сообщение (Base64): ", encrypted_base64)
        print("Ключ для расшифровки:", key_details)
        print("Результаты шифрования записаны в файл encrypt.txt")
    elif choice == 'k':
        filename = input("Введите имя файла с вашим сообщением: ").strip()
        with open(filename, 'r', encoding='utf-8') as f:
            message = f.read()
        
        key_details = input("Введите ключ для шифрования (JSON): ")
        encrypted_base64, _ = encrypt_message(message, key_details=key_details)
        with open("encrypt.txt", 'w', encoding='utf-8') as f:
            f.write(encrypted_base64 + "\n")
        
        print("Зашифрованное сообщение (Base64):", encrypted_base64)
        print("Результаты шифрования записаны в файл encrypt.txt")
    elif choice == 'd':
        filename = input("Введите имя файла с вашим зашифрованным сообщением (Base64): ").strip()
        with open(filename, 'r', encoding='utf-8') as f:
            encrypted_message = f.read().strip()
        
        key_details = input("Введите ключ для расшифровки (JSON): ")
        decrypted_message = decrypt_message(encrypted_message, key_details)
        with open("decrypt.txt", 'w', encoding='utf-8') as f:
            f.write(decrypted_message)
        
        print("Расшифрованное сообщение:", decrypted_message)
        print("Результаты дешифрования записаны в файл decrypt.txt")
    else:
        print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
