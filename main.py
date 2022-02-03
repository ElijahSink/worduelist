#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if update.message and (user := update.effective_user):
        update.message.reply_markdown_v2(
            rf"Hi {user.mention_markdown_v2()}\!",
            reply_markup=ForceReply(selective=True),
        )


HELP_TEXT = (
    "Send me a five letter word to be encoded, or a 10 digit number to be decoded."
)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    if update.message:
        update.message.reply_text(HELP_TEXT)


key = [
    ["A", "36"],
    ["B", "61"],
    ["C", "82"],
    ["D", "41"],
    ["E", "97"],
    ["F", "18"],
    ["G", "42"],
    ["H", "35"],
    ["I", "40"],
    ["J", "38"],
    ["K", "21"],
    ["L", "87"],
    ["M", "83"],
    ["N", "34"],
    ["O", "37"],
    ["P", "51"],
    ["Q", "53"],
    ["R", "72"],
    ["S", "52"],
    ["T", "29"],
    ["U", "60"],
    ["V", "55"],
    ["W", "28"],
    ["X", "10"],
    ["Y", "56"],
    ["Z", "70"],
]

encode_map = {letter: code for letter, code in key}
decode_map = {code: letter for letter, code in key}


def decode(ten_digit_number: str) -> str:
    decoded = ""
    for i in range(0, len(ten_digit_number), 2):
        logger.info("i=%d, i+2=%d", i, i + 2)
        decoded += decode_map[ten_digit_number[i : i + 2]]
    return decoded


def encode(five_letter_word: str) -> str:
    return "".join(encode_map[letter] for letter in five_letter_word.upper())


def handle_text(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if not update.message:
        return

    user = "unknown"
    if update.effective_user:
        user = update.effective_user.username or user

    if update.message.text:
        text = update.message.text
    else:
        update.message.reply_text("You need to send a normal message with text.")
        return

    if text.isnumeric and len(text) == 10:
        decoded = decode(text)
        logger.info("User %s decoded '%s' -> '%s'", user, text, decoded)
        update.message.reply_text(decoded)
    elif text.isalpha() and len(text) == 5:
        encoded = encode(text)
        logger.info("User %s encoded '%s' -> '%s'", user, text, encoded)
        update.message.reply_text(encoded)
    else:
        logger.info("User has unknown intentions: %s", text)
        update.message.reply_text("I'm not sure what to do with that.\n" + HELP_TEXT)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    TOKEN = os.environ["BOT_TOKEN"]
    PORT = int(os.environ["PORT"])
    WEBHOOK_URL = os.environ["WEBHOOK_URL"]

    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    logger.info("Starting webhook on port %s", PORT)
    updater.start_webhook(
        listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=WEBHOOK_URL + TOKEN
    )

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
