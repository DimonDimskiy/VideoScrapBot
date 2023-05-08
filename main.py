"""
Telegram bot that downloads videos from received URLs and sends
them back to user as a mediafile.
"""
import os


from yt_dlp import YoutubeDL, utils
from telegram import Update, error
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.constants import MessageEntityType
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN")
EXPECTED_FORMAT = "mp4"
TEMP_NAME = "tmp." + EXPECTED_FORMAT
MAX_FILE_SIZE = 52428800


async def universal_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles any user input excluded sending URL
    """
    await update.message.reply_text(
        f"{update.effective_user.first_name}, please enter video URL"
    )


async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles URL sent by user
    """
    urls = update.message.parse_entities([MessageEntityType.URL])
    if len(urls) > 1:
        await update.message.reply_text(
            f"{update.effective_user.first_name}, you entered to much URLs"
        )
    else:
        url = urls.popitem()[1]

        await update.message.reply_text("Downloading...")
        try:
            download(url)
            await update.message.reply_text("File downloaded and converted")
        except utils.DownloadError:
            await update.message.reply_text(
                f"{update.effective_user.first_name}, you entered an unsupported URL"
            )
            return
        except TypeError:
            await update.message.reply_text("Unable to convert file into mp4")
            return

        if os.path.getsize(TEMP_NAME) > MAX_FILE_SIZE:
            await update.message.reply_text("File is to large to upload")
            return

        await update.message.reply_text("Uploading...")
        try:
            await update.message.reply_document(
                TEMP_NAME, write_timeout=240, read_timeout=240
            )
            # without defining read timeout app running in docker throws an exception
            # ReadTimeout while running in laptop does not cause this exception
        except error.NetworkError:
            await update.message.reply_text("Uploading failed, network error")


def rename(filename: str) -> None:
    """
    Function receives name of the file after postprocessing,
    change it to temporary name to avoid storing few different
    files, before renaming it ensures that file has expected
    extension, otherwise it raises TypeError, that will be
    caught in link_handler function
    :param filename: str
    :return: None
    """
    _, ext = os.path.splitext(filename)
    if ext == "." + EXPECTED_FORMAT:
        os.rename(filename, TEMP_NAME)
    else:
        os.remove(filename)
        raise TypeError("Unexpected file extension")


def download(url: str) -> None:
    """
    Creates YoutubeDL obj with specified options, runs download.
    Format "w" allows to avoid errors "Requested format is not available"
    in services like https://pikabu.ru/ , when video is hosted not by YouTube.
    [ext!=png] used to fix some unexpected behaviour from yt-dlp, usually it
    doesn't accept URL without video, but I've found URL that contains .png
    image that yt-dlp downloads and PP converts into mp4 - bug?.
    https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png
    :param url: a video URL (str)
    :return: None
    """
    params = {
        "format": f"b[filesize<{MAX_FILE_SIZE}]/w[ext!=png]",
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": EXPECTED_FORMAT}
        ],
        "keep_video": False,
        "post_hooks": [rename],
    }
    with YoutubeDL(params) as ydl:
        ydl.download(url)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.Entity(MessageEntityType.URL), link_handler))
app.add_handler(MessageHandler(filters.ALL, universal_answer))


app.run_polling()
