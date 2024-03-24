import telebot

from utils import (
    download_photo_from_message,
    make_text_beautiful,
    remove_empty_values,
    remove_line_breaks_without_dot,
    scrape_text_from_image,
)
from utils.config import settings
from utils.logger import logger

logger.info("start")

bot = telebot.TeleBot(settings.TOKEN)
bot.get_updates()


def reply_with_beautiful_text(message_to_reply: telebot.types.Message, text: str,
                              with_link=False, parse_mode="markdown"):
    beautiful_text = make_text_beautiful(text)

    if with_link:
        beautiful_text += f"\n\n<b><a href=\"{settings.CHANNEL_LINK}\">" \
                          f"{make_text_beautiful(settings.LINK_TEXT)}</a></b>"
        parse_mode = "HTML"

    bot.reply_to(message_to_reply, beautiful_text, parse_mode=parse_mode)


@bot.message_handler(commands=['start'])
def handle_start_command(message: telebot.types.Message):
    reply_with_beautiful_text(message, settings.WELCOME_MESSAGE)


@bot.message_handler(commands=['font'])
def handle_font_command(message: telebot.types.Message):
    logger.info(remove_empty_values(message))
    text = message.text[6:]
    if not text:
        bot.reply_to(
            message,
            "Please provide some text after the _/font_ command.",
            parse_mode="markdown",
        )
        return
    reply_with_beautiful_text(message, text)


@bot.message_handler(commands=['s'])
def handle_s_command(message: telebot.types.Message):
    """Sends a link from the config with beautified text from the config"""
    logger.info(remove_empty_values(message))
    if message.from_user.id == settings.OWNER:
        reply_with_beautiful_text(message, "", with_link=True)


@bot.message_handler(commands=['send_btnpost_to_channel'])
def handle_send_btnpost_to_channel_command(message: telebot.types.Message):
    if message.from_user.id == settings.OWNER:
        parts = message.text.split(' ', 1)
        if len(parts) != 2 or '|#|' not in parts[1]:
            bot.reply_to(
                message,
                "The command format is incorrect. Use: /send_btnpost_to_channel "
                "<channel_username> |#| <post_text> |#| <btn-text> |#| <btn_link>"
            )
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
            bot.reply_to(
                message,
                "You must specify the channel username, text of the message, "
                "the text of the button, and the link."
            )
            return

        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text=btn_text, url=btn_link)
        markup.add(btn)

        try:
            bot.send_message(chat_id=channel_username, text=post_text, reply_markup=markup)
            bot.reply_to(message, "Message sent successfully to the channel.")
        except Exception as e:
            bot.reply_to(message, f"An error occurred while sending the message: {e}")


@bot.message_handler(content_types=['text', 'photo', 'video', 'sticker', 'document', 'audio', 'voice'])
def handle_private_message(message: telebot.types.Message):
    logger.info(remove_empty_values(message))

    if message.from_user.id == settings.OWNER and message.reply_to_message:
        original_chat_id = message.reply_to_message.forward_from.id if message.reply_to_message.forward_from else None
        if original_chat_id:
            bot.copy_message(
                chat_id=original_chat_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )

    elif message.from_user.id != settings.OWNER:
        bot.forward_message(settings.OWNER, message.chat.id, message.message_id)

    elif message.from_user.id == settings.OWNER:
        if message.content_type == 'text':
            reply_with_beautiful_text(message, message.text, with_link=True)
        elif message.content_type == 'photo':
            photo = download_photo_from_message(bot, message)
            scraped_text = remove_line_breaks_without_dot(scrape_text_from_image(photo))
            bot.reply_to(message, scraped_text)


bot.infinity_polling()
