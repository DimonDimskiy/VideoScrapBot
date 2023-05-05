from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.constants import MessageEntityType


async def bot_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'{update.effective_user.first_name}, please enter video URL')


async def bot_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    urls = update.message.parse_entities([MessageEntityType.URL])
    if len(urls) > 1:
        await update.message.reply_text(f"{update.effective_user.first_name}, you entered to much URLs")
    else:
        url = urls.popitem()[1]
        await update.message.reply_text(f"{url}")


app = ApplicationBuilder().token("6055251020:AAHwkEyhuhsh9-5afrm0tx52cP7KzK9IyBk").build()

app.add_handler(MessageHandler(filters.Entity(MessageEntityType.URL), bot_answer))
app.add_handler(MessageHandler(filters.ALL, bot_text))

app.run_polling()

# from telegram import Update
# from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
#
#
# def hello(update: Update, context: CallbackContext) -> None:
#     update.message.reply_text(f'Hello {update.effective_user.first_name}')
#
#
# def botMessage(update: Update, context: CallbackContext):
#     text = update.message.text
#     reply = bot(text)
#     update.message.reply_text(reply)
#
#
# updater = Updater('5249226675:AAETSF6NN51dgtMsQuzC4kg79Yjfl_bfny8')
#
# updater.dispatcher.add_handler(CommandHandler('hello', hello))
# updater.dispatcher.add_handler(MessageHandler(Filters.text, botMessage))
#
# updater.start_polling()
# updater.idle()
