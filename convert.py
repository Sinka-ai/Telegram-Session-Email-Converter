from opentele.api import API
from pyrogram import Client, idle, filters
from pyrogram.raw import *
from pyrogram.raw.base.email_verify_purpose import EmailVerifyPurpose
from pyrogram.raw.types.email_verify_purpose_login_change import EmailVerifyPurposeLoginChange
from pyrogram.errors import EmailUnconfirmed, CodeInvalid
from TGConvertor.manager import SessionManager
from pathlib import Path
import asyncio
import os
import json
import shutil
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

def get_tdata_gmail(directory='tdata_gmail'):
    ready_directories = []
    ready_directory = ''
    for foldername, subfolders, filenames in os.walk(directory):
        for subfolder in subfolders:
            if "tdata" in subfolder.lower():
                directory_path = os.path.join(foldername, subfolder)
                if directory_path not in ready_directories:
                    ready_directories.append(directory_path[9:])
                    ready_directory += directory_path
    return ready_directory

def generate_unique_name(base_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_name}_{timestamp}"

async def check_account_is_ok(client, path):
    try:
        async with client:
            user = await client.get_me()
            phone_number = user.phone_number
            return True
    except Exception as ex:
        print(f'{path} | Account is invalid or deactivated')
        return False

async def validate_account(client, path):
    try:
        task = asyncio.create_task(check_account_is_ok(client, path))
        await asyncio.wait_for(task, timeout=15)
        return task.result()
    except asyncio.TimeoutError:
        print(f'{path} | Account validation timeout')
        return False

def main_convert(path: str):
    with open('config.json', 'r') as file:
        config = json.load(file)
    try:
        session = SessionManager.from_tdata_folder(Path(path))
        app = session.pyrogram.client(session.api)
        app.APP_VERSION = config["app_version"]
        app.DEVICE_MODEL = config["device_model"]
        app.SYSTEM_VERSION = config["system_version"]
        app.app_version = config["app_version"]
        app.device_model = config["device_model"]
        app.system_version = config["system_version"]
        app.api_hash = config["api_hash"]
        app.api_id = config["api_id"]

        return app
    except Exception as ex:
        print(str(ex))
        return None

async def check_and_convert(path):
    client = main_convert(path)
    if client is not None:
        is_valid = await validate_account(client, path)
        if not is_valid:
            unique_name = generate_unique_name(os.path.basename(path))
            shutil.move(path, f'invalid_tdatas/{unique_name}')
            return None
        return client
    else:
        unique_name = generate_unique_name(os.path.basename(path))
        shutil.move(path, f'invalid_tdatas/{unique_name}')
        return None

async def remove_password(path, password):
    try:
        client = await check_and_convert(path)
        if client is not None:
            try:
                async with client:
                    result = await client.remove_cloud_password(password)
                    if result:
                        print(f'{path} | Пароль успешно снят')
                    else:
                        print(f'{path} | Пароль не установлен')
            except Exception as ex:
                unique_name = generate_unique_name(os.path.basename(path))
                if 'invalidated' in str(ex) or 'deactivated' in str(ex):
                    shutil.move(f'tdatas/{os.path.basename(path)}', f'invalid_tdatas/{unique_name}')
                elif 'invalid' in str(ex):
                    print("Пароль неверный!")
                    shutil.move(f'tdatas/{os.path.basename(path)}', f'invalid_password/{unique_name}')
                elif 'no cloud' in str(ex):
                    print("Пароля нет!")
                    return
                else:
                    print(f'{path} | Не смог сменить пароль\nКод ошибки: {str(ex)}')
                return -1
        else:
            unique_name = generate_unique_name(os.path.basename(path))
            shutil.move(f'tdatas/{os.path.basename(path)}', f'invalid_tdatas/{unique_name}')
    except Exception as ex:
        print(f'{path} | Error removing password\nError code: {str(ex)}')

async def add_password(path, password):
    try:
        client = await check_and_convert(path)
        if client is not None:
            try:
                async with client:
                    result = await client.enable_cloud_password(password)
                    if result:
                        print(f'{path} | Пароль успешно добавлен')
            except Exception as ex:
                unique_name = generate_unique_name(os.path.basename(path))
                if 'invalidated' in str(ex) or 'deactivated' in str(ex):
                    shutil.move(f'tdatas/{os.path.basename(path)}', f'invalid_tdatas/{unique_name}')
                else:
                    shutil.move(f'tdatas/{os.path.basename(path)}', f'invalid_password/{unique_name}')
                print(f'{path} | Не смог добавить пароль\nКод ошибки: {str(ex)}')
                return -1
        else:
            unique_name = generate_unique_name(os.path.basename(path))
            shutil.move(f'tdatas/{os.path.basename(path)}', f'invalid_tdatas/{unique_name}')
    except Exception as ex:
        print(f'{path} | Error adding password\nError code: {str(ex)}')

async def parse_gmail(client, timee):
    try:
        code = 0
        async with client:
            ok = False
            while not ok:
                print(f'Парсим почту...')
                history = client.get_chat_history(chat_id='@GmailBot', limit=2)
                async for message in history:
                    if ('Your code is: ' in message.text) and (timee < message.date):
                        code = str(message.text.split('Your code is: ')[1][:6])
                        ok = True
                await asyncio.sleep(10)
        return code
    except Exception as ex:
        print(str(ex))

async def add_2fa(path, email, password, gmail_path):
    client = await check_and_convert(path)
    await asyncio.sleep(1)
    gmail_client = await check_and_convert(gmail_path)
    if client is not None and gmail_client is not None:
        current_time = datetime.datetime.now()

        async with client:
            print(f'{path} | Проверка на наличие пароля...')
            try:
                result = await client.check_password(password=password)
                if result.is_self:
                    print(f'{path} | Пароль есть!')
                    await client.remove_cloud_password(password=password)
            except:
                print(f'{path} | Пароля нет!')
            try:
                print(f'{path} | Ставим 2фа...')
                await asyncio.sleep(5)
                await client.enable_cloud_password(password=password, email=email)
            except EmailUnconfirmed:
                pass
        code = await parse_gmail(gmail_client, current_time)
        print(f'{gmail_path} | Код получен - {code}')
        print(f'{path} | Пробуем подтвердить 2фа...')
        async with client:
            try:
                await client.invoke(
                    functions.account.ConfirmPasswordEmail(code=code)
                )
                print(f'{path} | 2фа успешно поставлена!')
            except CodeInvalid:
                print(f'{path} | Код неверный')
        print(f'{path} | Завершает работу...')
        return

def send_unban_email(to_email, subject, message, smtp_server, smtp_port, smtp_login, smtp_password):
    try:
        if not to_email or not subject:
            print(f"Invalid email or subject: {to_email}, {subject}")
            return

        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = formataddr((str(Header(smtp_login, 'utf-8')), smtp_login))
        msg['To'] = formataddr((str(Header(to_email, 'utf-8')), to_email))
        msg['Subject'] = Header(subject, 'utf-8')

        # Добавляем текст сообщения с кодировкой UTF-8
        part = MIMEText(message, 'plain', 'utf-8')
        msg.attach(part)

        # Отправляем письмо
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_login, smtp_password)
        server.sendmail(smtp_login, to_email, msg.as_string())
        server.quit()
        print(f'Email sent to {to_email}')
    except Exception as ex:
        print(f'Не удалось отправить email\nКод ошибки: {str(ex)}')
