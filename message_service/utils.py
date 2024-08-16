from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_tz, mktime_tz

import pytz


def parse_date(date_str):
    """Преобразование даты из строки в datetime."""
    parsed_date = parsedate_tz(date_str)
    if parsed_date:
        timestamp = mktime_tz(parsed_date)
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "Неверный формат даты"


def decode_subject(subject_header):
    """Декодирует тему сообщения из заголовка."""
    subject, encoding = decode_header(subject_header)[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    return subject


def get_content_message(message):
    """Извлекает контент сообщения."""
    files = []
    content = {"text": "", "files": files}

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                content["text"] = part.get_payload(decode=True).decode(
                    part.get_content_charset(), errors="replace"
                )
            file_name = part.get_filename()
            if file_name:
                files.append(
                    {
                        "file_name": file_name,
                        "content_type": part.get_content_type(),
                        "payload": part.get_payload(decode=True),
                    }
                )

    return content


def clean_text(text):
    """Удаляет пустые строки и лишние пробелы из текста."""
    if text:
        cleaned_text = "\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )
        return cleaned_text.replace("\r\n", "")
    return "Текстовая часть не найдена."


def format_message(message) -> dict:
    """Форматирует сообщение в словарь."""
    subject = decode_subject(message.get("Subject", ""))
    from_ = message.get("From", "Не указано")

    # Дата отправления
    date_send = message.get("Date", "Дата отправления не указана")
    if date_send != "Дата отправления не указана":
        try:
            date_send = parse_date(date_send)
        except Exception as e:
            date_send = f"Ошибка при разборе даты отправления: {e}"

    # Дата получения
    received = message.get_all("Received", [])
    if received:
        date_received_str = received[0].split(";", 1)[-1].strip()
        try:
            date_received = parse_date(date_received_str)
        except Exception as e:
            date_received = f"Ошибка при разборе даты получения: {e}"
    else:
        date_received = "Дата получения не указана."

    # контент сообщения
    content = get_content_message(message)
    files = content["files"]
    text_part = clean_text(content["text"])

    message_data = {
        "from": from_,
        "title": subject,
        "content": text_part,
        "date_send": date_send,
        "date_received": date_received,
        "files": files,
    }
    return message_data
