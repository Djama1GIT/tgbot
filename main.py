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
            "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎",
        )
    )

    alphabet = english_abc | russian_abc | digits_abc
    return "".join(
        alphabet.get(text[i], text[i])
        for i in range(len(text))
    )


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
def send_beautiful_text(message: telebot.types.Message):
    logger.info(remove_empty_values(message))
    if message.from_user.id == settings.OWNER:
        beautiful_text = f"<b><a href=\"{settings.CHANNEL_LINK}\">" \
                         f"{make_text_beautiful(settings.LINK_TEXT)}</a></b>"
        bot.send_message(
            message.chat.id,
            beautiful_text,
            parse_mode="HTML",
        )
    else:
        bot.reply_to(message, "Sorry, I didn't understand that command.\nUse: /help")


@bot.message_handler(commands=['help', 'start'])
def send_help(message: telebot.types.Message):
    logger.info(remove_empty_values(message))
    help_text = "Welcome!\n\n" \
                "Commands:\n" \
                "To beautify your text, send a message with the:\n" \
                "_/font_ command followed by your text.\n" \
                "```for-example\n/font Hello, world!```\n"
    bot.reply_to(
        message,
        help_text,
        parse_mode="markdown",
    )


@bot.message_handler(content_types=['text'])
def unknown_command(message: telebot.types.Message):
    logger.info(remove_empty_values(message))
    if message.from_user.id == settings.OWNER:
        beautiful_text = make_text_beautiful(message.text + "\n\n")
        bot.reply_to(
            message,
            beautiful_text + f"<b><a href=\"{settings.CHANNEL_LINK}\">"
                             f"{make_text_beautiful(settings.LINK_TEXT)}</a></b>",
            parse_mode="HTML",
        )
    else:
        bot.reply_to(message, "Sorry, I didn't understand that command.\nUse: /help")


bot.infinity_polling()
