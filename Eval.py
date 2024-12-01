import os
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    filters,
)


BOT_TOKEN = "7581811310:AAHBZygnB1fO7WO79n_EJOrVTEcRXnL3Qh0"  
OWNER_ID = [6882559224] 


async def aexec(code, update: Update, context: CallbackContext):
    exec(
        "async def __aexec(update, context): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](update, context)


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in OWNER_ID:
        await update.message.reply_text(
            "Hey Boss! 👑\nI'm up and running!\nUse /eval to execute commands."
        )
    else:
        await update.message.reply_text(
            "Hello! I'm a bot made for specific tasks. You don't have permission to use my advanced features."
        )


async def eval_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in OWNER_ID:
        return await update.message.reply_text("You are not authorized to use this command.")
    
    if len(context.args) == 0:
        return await update.message.reply_text("<b>ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴɴᴀ ᴇxᴇᴄᴜᴛᴇ ʙᴀʙʏ?</b>", parse_mode="HTML")
    
    cmd = " ".join(context.args)
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, update, context)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = "\n"
    if exc:
        evaluation += exc
    elif stderr:
        evaluation += stderr
    elif stdout:
        evaluation += stdout
    else:
        evaluation += "Success"
    final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<pre language='python'>{evaluation}</pre>"
    
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation))
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="⏳", callback_data=f"runtime {t2-t1} Seconds")]]
        )
        await update.message.reply_document(
            document=filename,
            caption=f"<b>⥤ ᴇᴠᴀʟ :</b>\n<code>{cmd[:980]}</code>\n\n<b>⥤ ʀᴇsᴜʟᴛ :</b>\nAttached Document",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        os.remove(filename)
    else:
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {round(t2-t1, 3)} Seconds",
                    ),
                ]
            ]
        )
        await update.message.reply_text(final_output, parse_mode="HTML", reply_markup=keyboard)


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("eval", eval_command, filters=filters.TEXT & ~filters.COMMAND))

    print("Bot is running...")
    app.run_polling()
