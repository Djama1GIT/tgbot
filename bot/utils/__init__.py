import os
import re
import uuid

import telebot

from .parser import TextParserFromImage


def make_text_beautiful(text: str) -> str:
    english_abc = dict(
        zip(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛",
        )
    )
    russian_abc = dict(
        zip(
            "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя",
            "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯᴀбʙᴦдᴇёжɜийᴋᴧʍнᴏᴨᴩᴄᴛуɸхцчɯщъыь϶юя",
        )
    )
    digits_abc = dict(
        zip(
            "1234567890",
            "𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶",
        )
    )

    alphabet = english_abc | russian_abc | digits_abc
    return "".join(
        alphabet.get(text[i], text[i])
        for i in range(len(text))
    )


def remove_empty_values(item: dict | object) -> dict:
    if type(item) is not dict and "__dict__" not in item.__dir__():
        return item
    if "__dict__" in item.__dir__():
        item = item.__dict__
    return {k: remove_empty_values(v) for k, v in item.items() if v is not None}


def remove_line_breaks_without_dot(text):
    pattern = r'(?<!\.)\n'
    result = re.sub(pattern, ' ', text)
    return result


def scrape_text_from_image(photo: bytes) -> str:
    image_filename = f"{uuid.uuid4()}.png"
    with open(image_filename, 'wb') as file:
        file.write(photo)

    image_filepath = os.path.join(os.getcwd(), image_filename)

    text_parser = TextParserFromImage()
    text = text_parser.parse_text_from_image(image_filepath)

    os.remove(image_filepath)

    return text


def download_photo_from_message(bot: telebot.TeleBot, message: telebot.types.Message):
    photo_id = message.photo[-1].file_id
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    return downloaded_file
