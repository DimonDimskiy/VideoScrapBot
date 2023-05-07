import os
import subprocess


from yt_dlp import YoutubeDL, utils
from telegram import Update, error
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.constants import MessageEntityType


TEMP_NAME = 'tmp.mp4'
EXPECTED_FORMAT = '.mp4'
MAX_FILE_SIZE = 52428800


async def bot_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'{update.effective_user.first_name}, please enter video URL')


async def bot_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    urls = update.message.parse_entities([MessageEntityType.URL])
    if len(urls) > 1:
        await update.message.reply_text(f"{update.effective_user.first_name}, you entered to much URLs")
    else:
        url = urls.popitem()[1]

        await update.message.reply_text("Downloading...")
        try:
            download(url)
            await update.message.reply_text("File downloaded and converted")
        except utils.DownloadError:
            await update.message.reply_text(f"{update.effective_user.first_name}, you entered an unsupported URL")
            return

        filesize = os.path.getsize(TEMP_NAME)
        if filesize > MAX_FILE_SIZE:
            await update.message.reply_text("To large file to upload")
            return

        await update.message.reply_text("Uploading...")
        try:
            await update.message.reply_document(TEMP_NAME, write_timeout=240)
        except error.NetworkError:
            await update.message.reply_text("Uploading failed, network error")


def ensure_mp4(filename: str) -> None:
    _, ext = os.path.splitext(filename)
    if ext != EXPECTED_FORMAT:
        subprocess.run(['ffmpeg', '-i', filename, TEMP_NAME, '-y'])
        os.remove(filename)
    else:
        os.rename(filename, TEMP_NAME)


params = {
    'format': 'b[filesize<50M]/ w',
    'vext': '(mp4 > webm > flv > other > unknown)',
    'post_hooks': [ensure_mp4],
    'keep_video': False
}


def download(url: str) -> None:
    with YoutubeDL(params) as ydl:
        ydl.download(url)


app = ApplicationBuilder().token("6055251020:AAHwkEyhuhsh9-5afrm0tx52cP7KzK9IyBk").build()

app.add_handler(MessageHandler(filters.Entity(MessageEntityType.URL), bot_answer))
app.add_handler(MessageHandler(filters.ALL, bot_text))


app.run_polling()
