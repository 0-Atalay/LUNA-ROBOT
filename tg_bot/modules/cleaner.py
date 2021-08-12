import html

from typing import List

from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async

from tg_bot import ALLOW_EXCL, dispatcher, CustomCommandHandler
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import user_admin, bot_can_delete, dev_plus, connection_status
from tg_bot.modules.sql import cleaner_sql as sql

if ALLOW_EXCL:
    CMD_STARTERS = ('/', '!')
else:
    CMD_STARTERS = ('/')

BLUE_TEXT_CLEAN_GROUP = 15
CommandHandlerList = (CommandHandler, CustomCommandHandler, DisableAbleCommandHandler)
command_list = ["cleanblue", "ignoreblue", "unignoreblue", "listblue", "ungignoreblue", "gignoreblue"
                "start", "help", "settings", "donate", "stalk", "aka", "leaderboard"]

for handler_list in dispatcher.handlers:
    for handler in dispatcher.handlers[handler_list]:
        if any(isinstance(handler, cmd_handler) for cmd_handler in CommandHandlerList):
            command_list += handler.command


@run_async
def clean_blue_text_must_click(bot: Bot, update: Update):

    chat = update.effective_chat
    message = update.effective_message

    if chat.get_member(bot.id).can_delete_messages:
        if sql.is_enabled(chat.id):
            fst_word = message.text.strip().split(None, 1)[0]

            if len(fst_word) > 1 and any(fst_word.startswith(start) for start in CMD_STARTERS):

                command = fst_word[1:].split('@')
                chat = update.effective_chat

                ignored = sql.is_command_ignored(chat.id, command[0])
                if ignored:
                    return

                if command[0] not in command_list:
                    message.delete()


@run_async
@connection_status
@bot_can_delete
@user_admin
def set_blue_text_must_click(bot: Bot, update: Update, args: List[str]):

    chat = update.effective_chat
    message = update.effective_message

    if len(args) >= 1:
        val = args[0].lower()
        if val == "off" or val == "no":
            sql.set_cleanbt(chat.id, False)
            reply = "Bluetext cleaning has been disabled for <b>{}</b>".format(html.escape(chat.title))
            message.reply_text(reply, parse_mode=ParseMode.HTML)

        elif val == "yes" or val == "on":
            sql.set_cleanbt(chat.id, True)
            reply = "Bluetext cleaning has been enabled for <b>{}</b>".format(html.escape(chat.title))
            message.reply_text(reply, parse_mode=ParseMode.HTML)

        else:
            reply = "Geçersiz argüman.Kabul edilen değerler 'yes', 'on', 'no', 'off'"
            message.reply_text(reply)
    else:
        clean_status = sql.is_enabled(chat.id)
        if clean_status:
            clean_status = "Enabled"
        else:
            clean_status = "Disabled"
        reply = "Bluetext temizleme <b>{}</b> : <b>{}</b>".format(chat.title, clean_status)
        message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@user_admin
def add_bluetext_ignore(bot: Bot, update: Update, args: List[str]):

    message = update.effective_message
    chat = update.effective_chat

    if len(args) >= 1:
        val = args[0].lower()
        added = sql.chat_ignore_command(chat.id, val)
        if added:
            reply = "<b>{}</b> bluetext temizleyici yoksayma listesine eklendi .".format(args[0])
        else:
            reply = "Komut zaten yoksayıldı."
        message.reply_text(reply, parse_mode=ParseMode.HTML)
        
    else:
        reply = "Yok sayılacak komut verilmedi."
        message.reply_text(reply)


@run_async
@user_admin
def remove_bluetext_ignore(bot: Bot, update: Update, args: List[str]):

    message = update.effective_message
    chat = update.effective_chat

    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.chat_unignore_command(chat.id, val)
        if removed:
            reply = "<b>{}</b> has been removed from bluetext cleaner ignore list.".format(args[0])
        else:
            reply = "Komut şu anda yok sayılmıyor."
        message.reply_text(reply, parse_mode=ParseMode.HTML)
        
    else:
        reply = "No command supplied to be unignored."
        message.reply_text(reply)


@run_async
@user_admin
def add_bluetext_ignore_global(bot: Bot, update: Update, args: List[str]):

    message = update.effective_message

    if len(args) >= 1:
        val = args[0].lower()
        added = sql.global_ignore_command(val)
        if added:
            reply = "<b>{}</b> global bluetext temizleyici yoksayma listesine eklendi.".format(args[0])
        else:
            reply = "Komut zaten yoksayıldı."
        message.reply_text(reply, parse_mode=ParseMode.HTML)
        
    else:
        reply = "Yok sayılacak komut verilmedi."
        message.reply_text(reply)


@run_async
@dev_plus
def remove_bluetext_ignore_global(bot: Bot, update: Update, args: List[str]):

    message = update.effective_message

    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.global_unignore_command(val)
        if removed:
            reply = "<b>{}</b> global bluetext temizleyici yoksayma listesinden kaldırıldı.".format(args[0])
        else:
            reply = "Komut şu anda yok sayılmıyor."
        message.reply_text(reply, parse_mode=ParseMode.HTML)
        
    else:
        reply = "Yoksayılacak komut verilmedi."
        message.reply_text(reply)


@run_async
@dev_plus
def bluetext_ignore_list(bot: Bot, update: Update):

    message = update.effective_message
    chat = update.effective_chat

    global_ignored_list, local_ignore_list = sql.get_all_ignored(chat.id)
    text = ""

    if global_ignored_list:
        text = "Aşağıdaki komutlar şu anda bluetext temizlemeden genel olarak yok sayılıyor :\n"

        for x in global_ignored_list:
            text += f" - <code>{x}</code>\n"

    if local_ignore_list:
        text += "\nAşağıdaki komutlar şu anda bluetext temizlemeden yerel olarak yok sayılıyor :\n"

        for x in local_ignore_list:
            text += f" - <code>{x}</code>\n"

    if text == "":
        text = "Şu anda mavi metin temizlemede hiçbir komut yok sayılmıyor."
        message.reply_text(text)
        return

    message.reply_text(text, parse_mode=ParseMode.HTML)
    return


__help__ = """
- /cleanblue <on/off/yes/no> - komutları gönderdikten sonra temizle 
- /ignoreblue <word> - komutun otomatik olarak temizlenmesini engelle 
- /unignoreblue <word> - komutun otomatik olarak temizlenmesini engelle 
- /listblue - şu anda beyaz listeye alınmış komutları listeler Aşağıdakiler yalnızca Afet komutlarıdır, yöneticiler bunları kullanamaz: 
- /gignoreblue <word> - genel olarak mavi metin temizlemeyi yok sayar. 
- /ungignoreblue <word> - söz konusu komutu genel temizleme listesinden kaldır
"""

SET_CLEAN_BLUE_TEXT_HANDLER = CommandHandler("cleanblue", set_blue_text_must_click, pass_args=True)
ADD_CLEAN_BLUE_TEXT_HANDLER = CommandHandler("ignoreblue", add_bluetext_ignore, pass_args=True)
REMOVE_CLEAN_BLUE_TEXT_HANDLER = CommandHandler("unignoreblue", remove_bluetext_ignore, pass_args=True)
ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler("gignoreblue", add_bluetext_ignore_global, pass_args=True)
REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler("ungignoreblue", remove_bluetext_ignore_global, pass_args=True)
LIST_CLEAN_BLUE_TEXT_HANDLER = CommandHandler("listblue", bluetext_ignore_list)
CLEAN_BLUE_TEXT_HANDLER = MessageHandler(Filters.command & Filters.group, clean_blue_text_must_click)

dispatcher.add_handler(SET_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(ADD_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(REMOVE_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
dispatcher.add_handler(REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
dispatcher.add_handler(LIST_CLEAN_BLUE_TEXT_HANDLER)
dispatcher.add_handler(CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP)

__mod_name__ = "BlUETEXT CLEANING🚮"
__handlers__ = [SET_CLEAN_BLUE_TEXT_HANDLER, ADD_CLEAN_BLUE_TEXT_HANDLER, REMOVE_CLEAN_BLUE_TEXT_HANDLER,
                ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER, REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER,
                LIST_CLEAN_BLUE_TEXT_HANDLER, (CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP)]
