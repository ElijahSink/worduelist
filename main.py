import base64
import json
import logging
import os
import subprocess
from datetime import date, timedelta

import requests
from telegram import ForceReply, ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from solve_waffle import WaffleSolver, list_solution

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


"""
WORDUEL STUFF
"""

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


"""
WORDLE STUFF
"""

with open("./word_list.json") as f:
    word_list = json.load(f)


WORDLE_DAY_0 = date(2021, 6, 19)


def wordle_command(update: Update, context: CallbackContext) -> None:
    if not update.message:
        return

    text = update.message.text
    if text:
        text = text.replace("/wordle", "").strip()

    offset = date.today() - WORDLE_DAY_0
    if text:
        offset += timedelta(days=int(text))

    update.message.reply_text(word_list[offset.days])


"""
QUORDLE STUFF
"""


def get_quordle_answer(date_offset: int) -> str:
    words = json.loads(
        subprocess.check_output(["node", "get_quordle_words.js", str(date_offset)])
    )
    return " ".join(words)


def quordle_command(update: Update, context: CallbackContext) -> None:
    if not update.message:
        return

    text = update.message.text
    if text:
        text = text.replace("/quordle", "").strip()

    try:
        offset = int(text)
    except ValueError:
        offset = 0

    update.message.reply_text(get_quordle_answer(offset))


"""
WAFFLE STUFF
"""


def format_waffle(s: str) -> str:
    return f"```\n{' '.join(s[0:5])}\n{s[5]}   {s[6]}   {s[7]}\n{' '.join(s[8:13])}\n{s[13]}   {s[14]}   {s[15]}\n{' '.join(s[16:21])}\n```"


def get_waffle_answer(date_offset: int) -> str:
    num = 1 + date_offset
    encoded_bytes = requests.get(f"https://wafflegame.net/daily{num}.txt").text
    decoded_bytes = base64.b64decode(encoded_bytes)
    decoded_str = decoded_bytes.decode("UTF-16")
    parsed_obj = json.loads(decoded_str)
    puzzle = parsed_obj["puzzle"]
    solution = parsed_obj["solution"]
    print(puzzle, solution)

    solver = WaffleSolver(puzzle, solution, 10, 2)
    solution_path = solver.solve()
    if not solution_path:
        return format_waffle(solution)

    return f"{list_solution(solution_path)}\n{format_waffle(solution)}"


def waffle_command(update: Update, context: CallbackContext) -> None:
    if not update.message:
        return

    text = update.message.text
    if text:
        text = text.replace("/waffle", "").strip()

    try:
        offset = int(text)
    except ValueError:
        offset = 0

    update.message.reply_text(get_waffle_answer(offset), parse_mode=ParseMode.MARKDOWN)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    TOKEN = os.environ["BOT_TOKEN"]

    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("wordle", wordle_command))
    dispatcher.add_handler(CommandHandler("quordle", quordle_command))
    dispatcher.add_handler(CommandHandler("waffle", waffle_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    if os.getenv("USE_POLLING"):
        updater.start_polling()
    else:
        PORT = int(os.environ["PORT"])
        WEBHOOK_URL = os.environ["WEBHOOK_URL"]
        logger.info("Starting webhook on port %s", PORT)
        updater.start_webhook(
            listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=WEBHOOK_URL + TOKEN
        )

    updater.idle()


if __name__ == "__main__":
    main()
