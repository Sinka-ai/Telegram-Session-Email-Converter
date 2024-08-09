import json
import os
import time
import random
import asyncio
from convert import *
from datetime import datetime

def generate_unique_name(base_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_name}_{timestamp}"

async def process_tdatas(method, tdatas_paths, password_to_remove, password_to_add, email, gmail_path):
    for i in range(len(tdatas_paths)):
        relative_path = os.path.join("", tdatas_paths[i]).replace("\\", "/")
        if method == 'remove':
            await remove_password(path=relative_path, password=password_to_remove)
        elif method == 'add':
            await add_password(path=relative_path, password=password_to_add)
        elif method == '2fa':
            await add_2fa(path=relative_path, email=email, password=password_to_add, gmail_path=gmail_path)
        time.sleep(random.randint(3, 4))

def main():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            password_to_remove = config["password_to_remove"]
            password_to_add = config["password_to_add"]
            email = config["email"]
            smtp_server = config["smtp_server"]
            smtp_port = config["smtp_port"]
            smtp_login = config["smtp_login"]
            smtp_password = config["smtp_password"]
            interval_min = config["interval_min"]
            interval_max = config["interval_max"]
            delay_after_count = config["delay_after_count"]
            delay_duration = config["delay_duration"]
    except Exception as ex:
        print(f'Не удалось открыть файл config.json\nКод ошибки: {str(ex)}')
        return

    method = ''
    while True:
        ask = input(
            '\nВыберите режим: \n1. Снятие паролей\n2. Добавление паролей\n3. Добавление паролей с двухфакторкой\n4. Разбан аккаунтов\n- ')
        if ask == '1':
            method = 'remove'
            break
        if ask == '2':
            method = 'add'
            break
        if ask == '3':
            method = '2fa'
            break
        if ask == '4':
            method = 'unban'
            break

    try:
        if method == 'unban':
            numbers_path = 'Numbers/numbers.txt'
            message_path = 'Numbers/message.txt'
            subject_path = 'Numbers/subject.txt'
            mail_path = 'Numbers/mail.txt'

            with open(numbers_path, 'r') as f:
                numbers = f.read().splitlines()

            with open(message_path, 'r') as f:
                message_template = f.read()

            with open(subject_path, 'r') as f:
                subject = f.read().strip()

            with open(mail_path, 'r') as f:
                mail_to = f.read().strip()

            for idx, number in enumerate(numbers):
                message = message_template.replace('**', number)
                send_unban_email(mail_to, subject, message, smtp_server, smtp_port, smtp_login, smtp_password)

                # Удаление номера из списка и обновление файла
                numbers.remove(number)
                with open(numbers_path, 'w') as f:
                    f.write('\n'.join(numbers))

                time.sleep(random.randint(interval_min, interval_max))

                if (idx + 1) % delay_after_count == 0:
                    print(f'Отлёжка на {delay_duration} секунд.')
                    time.sleep(delay_duration)
        else:
            tdatas_paths = []
            for root, dirs, files in os.walk('tdatas'):
                for dir in dirs:
                    if "tdata" in dir.lower():
                        tdatas_paths.append(os.path.join(root, dir))

            gmail_path = get_tdata_gmail()
            if '.DS_Store' in tdatas_paths:
                tdatas_paths.remove('.DS_Store')

            asyncio.run(process_tdatas(method, tdatas_paths, password_to_remove, password_to_add, email, gmail_path))

    except Exception as ex:
        print(str(ex))
        return

if __name__ == "__main__":
    while True:
        main()
