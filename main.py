# main.py

import json
from encrypt import encrypt_message
from decrypt import decrypt_message

def main():
    choice = input("Выберите действие: (E)ncrypt, (D)ecrypt, (K)ey encrypt: ").strip().lower()
    if choice == 'e':
        message = input("Введите ваше сообщение: ")
        encrypted_base64, key_details = encrypt_message(message)
        print("Зашифрованное сообщение (Base64):", encrypted_base64)
        print("Ключ для расшифровки:", key_details)
    elif choice == 'k':
        message = input("Введите ваше сообщение: ")
        key_details = input("Введите ключ для шифрования (JSON): ")
        encrypted_base64, _ = encrypt_message(message, key_details=key_details)
        print("Зашифрованное сообщение (Base64):", encrypted_base64)
    elif choice == 'd':
        encrypted_message = input("Введите зашифрованное сообщение (Base64): ")
        key_details = input("Введите ключ для расшифровки (JSON): ")
        decrypted_message = decrypt_message(encrypted_message, key_details)
        print("Расшифрованное сообщение:", decrypted_message)
    else:
        print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
