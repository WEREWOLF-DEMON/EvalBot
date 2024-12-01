import os
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7581811310:AAHBZygnB1fO7WO79n_EJOrVTEcRXnL3Qh0"
OWNER_ID = [6882559224]


async def aexec(code, update: Update, context: CallbackContext):
    exec(
        "async def __aexec(update, context): "
        + "".join(f"\n {line}" for line in code.split("\n"))
    )
    return await locals()["__aexec"](update, context)


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} triggered /start.")
    if user_id in OWNER_ID:
        await update.message.reply_text(
            "👋 Hey Boss! 👑\n\n"
            "I'm ready and running to execute your commands.\n"
            "Use /eval to evaluate Python code dynamically.\n\n"
            "🚀 *Let’s create something awesome!*",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "Hello! 👋\n\n"
            "This bot is for specific tasks, and you currently don't have permission to access its advanced features. 🔒",
            parse_mode="Markdown",
        )


async def eval_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id not in OWNER_ID:
        logger.warning(f"Unauthorized user {user_id} attempted to use /eval.")
        return await update.message.reply_text(
            "🚫 Sorry, you are not authorized to use this command."
        )

    if not context.args:
        return await update.message.reply_text(
            "🤔 *What would you like me to execute, boss?*\n\n"
            "_Please provide some code to evaluate._",
            parse_mode="Markdown",
        )

    code = " ".join(context.args)
    logger.info(f"Evaluating code from user {user_id}:\n{code}")
    t1 = time()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirected_output, redirected_error = StringIO(), StringIO()
    sys.stdout, sys.stderr = redirected_output, redirected_error
    stdout, stderr, exc = None, None, None

    try:
        await aexec(code, update, context)
    except Exception:
        exc = traceback.format_exc()

    sys.stdout, sys.stderr = old_stdout, old_stderr
    stdout, stderr = redirected_output.getvalue(), redirected_error.getvalue()

    evaluation = "💡 *Result:*\n"
    if exc:
        evaluation += f"🚨 *Error:*\n```\n{exc}\n```"
    elif stderr:
        evaluation += f"⚠️ *Stderr:*\n```\n{stderr}\n```"
    elif stdout:
        evaluation += f"✅ *Stdout:*\n```\n{stdout}\n```"
    else:
        evaluation += "✅ *Execution completed successfully!*"

    if len(evaluation) > 4096:
        filename = "output.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(evaluation)
        t2 = time()
        await update.message.reply_document(
            document=filename,
            caption=f"📂 *Result too long, attached as a file.*\n\n⏱️ *Execution Time:* {round(t2-t1, 3)} seconds.",
            parse_mode="Markdown",
        )
        os.remove(filename)
    else:
        t2 = time()
        await update.message.reply_text(
            evaluation + f"\n\n⏱️ *Execution Time:* {round(t2-t1, 3)} seconds.",
            parse_mode="Markdown",
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("eval", eval_command))

    logger.info("Bot is running...")
    app.run_polling()
