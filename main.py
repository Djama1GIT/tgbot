from telebot import types

from logger import logger
from config import settings
import telebot

logger.info("start")

bot = telebot.TeleBot(settings.TOKEN)
updates = bot.get_updates()


def remove_empty_values(item: dict | object) -> dict:
    if type(item) is not dict and "__dict__" not in item.__dir__():
        return item
    if "__dict__" in item.__dir__():
        item = item.__dict__
    return {k: remove_empty_values(v) for k, v in item.items() if v is not None}


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


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    beautiful_text = make_text_beautiful(settings.WELCOME_MESSAGE)
    bot.reply_to(message, beautiful_text)


@bot.message_handler(commands=['font'])
def send_beautiful_text(message: telebot.types.Message):
    logger.info(remove_empty_values(message))
    text = message.text[6:]
    if not text:
        bot.reply_to(
            message,
            "Please provide some text after the _/font_ command.",
            parse_mode="markdown",
        )
        return
    beautiful_text = make_text_beautiful(text)
    bot.reply_to(message, beautiful_text)


@bot.message_handler(commands=['s'])
def s(message: telebot.types.Message):
    logger.info(remove_empty_values(message))
    if message.from_user.id == settings.OWNER:
        beautiful_text = f"<b><a href=\"{settings.CHANNEL_LINK}\">" \
                         f"{make_text_beautiful(settings.LINK_TEXT)}</a></b>"
        bot.send_message(
            message.chat.id,
            beautiful_text,
            parse_mode="HTML",
        )


@bot.message_handler(commands=['send_btnpost_to_channel'])
def command_send_btnpost_to_channel(message: telebot.types.Message):
    if message.from_user.id == settings.OWNER:
        parts = message.text.split(' ', 1)
        if len(parts) != 2 or '|#|' not in parts[1]:
            bot.reply_to(message,
                         "The command format is incorrect. Use: /send_btnpost_to_channel "
                         "<channel_username> |#| <post_text> |#| <btn-text> |#| <btn_link>")
            return

        logger.info(parts[1].split("|#|"))
        channel_username, post_text, btn_text, btn_link = parts[1].split('|#|', 3)
        channel_username = channel_username.strip()
        post_text = post_text.strip()
        btn_text = btn_text.strip()
        btn_link = btn_link.strip()

        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username

        if not post_text or not btn_text or not btn_link:
            bot.reply_to(message,
                         "You must specify the channel username, text of the message, "
                         "the text of the button, and the link.")
            return

        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text=btn_text, url=btn_link)
        markup.add(btn)

        try:
            bot.send_message(chat_id=channel_username, text=post_text, reply_markup=markup)
            bot.reply_to(message, "Message sent successfully to the channel.")
        except Exception as e:
            bot.reply_to(message, f"An error occurred while sending the message: {e}")


@bot.message_handler(content_types=['text', 'photo', 'video', 'sticker', 'document', 'audio', 'voice'])
def handle_private_message(message):
    logger.info(remove_empty_values(message))

    if message.from_user.id == settings.OWNER and message.reply_to_message:
        original_chat_id = message.reply_to_message.forward_from.id if message.reply_to_message.forward_from else None
        if original_chat_id:
            if message.content_type == 'text':
                bot.send_message(original_chat_id, make_text_beautiful(message.text))
            else:
                bot.forward_message(original_chat_id, settings.OWNER, message.message_id)

    elif message.from_user.id != settings.OWNER:
        bot.forward_message(settings.OWNER, message.chat.id, message.message_id)

    elif message.from_user.id == settings.OWNER:
        beautiful_text = make_text_beautiful(message.text + "\n\n") if message.content_type == 'text' else ''
        bot.reply_to(
            message,
            beautiful_text + f"<b><a href=\"{settings.CHANNEL_LINK}\">"
                             f"{make_text_beautiful(settings.LINK_TEXT)}</a></b>",
            parse_mode="HTML",
        )


bot.infinity_polling()
