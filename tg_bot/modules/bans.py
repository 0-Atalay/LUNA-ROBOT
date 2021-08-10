import html
from typing import List

from telegram import Bot, Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher, LOGGER, DEV_USERS, SUDO_USERS, TIGER_USERS
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import (bot_admin, user_admin, is_user_ban_protected, can_restrict,
                                                     is_user_admin, is_user_in_chat, connection_status)
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.log_channel import loggable, gloggable


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Kullanıcı bulunamadı":
            message.reply_text("Bu kişiyi bulamıyor gibi görünüyor.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Oh evet, kendimi yasakla, noob!")
        return log_message

    # dev users to bypass whitelist protection incase of abuse
    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        message.reply_text("Bu kullanıcının dokunulmazlığı var - onları yasaklayamam.")
        return log_message

    log = (f"<b>{html.escape(chat.title)}:</b>\n"
           f"#BANNED\n"
           f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
           f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(chat.id, "Banned user {}.".format(mention_html(member.user.id, member.user.first_name)),
                        parse_mode=ParseMode.HTML)
        return log

    except BadRequest as excp:
        if excp.message == "Yanıt mesajı bulunamadı":
            # Do not reply
            message.reply_text('Banned!', quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Uhm...bu işe yaramadı...")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Kullanıcı bulunamadı":
            message.reply_text("Bu kullanıcıyı bulamıyorum.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Kendimi banlamayacağım, deli misin?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("öyle hissetmiyorum.")
        return log_message

    if not reason:
        message.reply_text("Bu kullanıcıyı yasaklamak için bir zaman belirtmediniz!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (f"<b>{html.escape(chat.title)}:</b>\n"
           "#TEMP BANNED\n"
           f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
           f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}\n"
           f"<b>Time:</b> {time_val}")
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(chat.id, f"Banned! User {mention_html(member.user.id, member.user.first_name)} "
                                 f"will be banned for {time_val}.",
                        parse_mode=ParseMode.HTML)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(f"Yasaklandı! Kullanıcı {time_val} süreyle yasaklanacak.", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s",
                             user_id, chat.title, chat.id, excp.message)
            message.reply_text("Lanet olsun, o kullanıcıyı yasaklayamam.")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def punch(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Bu kullanıcıyı bulamıyorum..")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Evet, bunu yapmayacağım.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Keşke bu kullanıcıyı yumruklayabilseydim....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(chat.id, f"One Punched! {mention_html(member.user.id, member.user.first_name)}.",
                        parse_mode=ParseMode.HTML)
        log = (f"<b>{html.escape(chat.title)}:</b>\n"
               f"#KICKED\n"
               f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
               f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log

    else:
        message.reply_text("Lanet olsun, o kullanıcıyı yumruklayamam.")

    return log_message


@run_async
@bot_admin
@can_restrict
def punchme(bot: Bot, update: Update):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Keşke yapabilseydim... ama sen bir adminsin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("sorun yok.")
    else:
        update.effective_message.reply_text("Ha? yapamam :/")


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def unban(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("bunun bir kullanıcı olduğundan şüpheliyim.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Bu kullanıcıyı bulamıyorum.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Burada olmasaydım kendimi nasıl yasaklardım...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Bu kişi zaten burada değil mi??")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Evet, bu kullanıcı katılabilir!")

    log = (f"<b>{html.escape(chat.title)}:</b>\n"
           f"#UNBANNED\n"
           f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
           f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@run_async
@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user

    if user.id not in SUDO_USERS or user.id not in TIGER_USERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Geçerli bir sohbet kimliği verin.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "kullanıcıyı bulamadım":
            message.reply_text("Bu kullanıcıyı bulamıyorum.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Zaten sohbette değil misin??")
        return

    chat.unban_member(user.id)
    message.reply_text("evet seni engelledim.")

    log = (f"<b>{html.escape(chat.title)}:</b>\n"
           f"#UNBANNED\n"
           f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log


__help__ = """
- /punchme: komutu veren kullanıcıyı yumruklar

 *Yalnızca yönetici:*
- /ban <userhandle>: bir kullanıcıyı yasaklar. (tutamaç veya yanıt yoluyla) 
- /tban <userhandle> x(m/h/d): bir kullanıcıyı x kez yasaklar. (tanıtıcı veya yanıt yoluyla). m = dakika, h = saat, d = gün. 
- /unban <userhandle>: bir kullanıcının yasağını kaldırır. (tutamaç veya yanıt yoluyla) 
- /punch <userhandle>: Bir kullanıcıyı gruptan çıkarır, (tutamaç veya yanıt yoluyla)
"""

BAN_HANDLER = CommandHandler("ban", ban, pass_args=True)
TEMPBAN_HANDLER = CommandHandler(["tban", "tempban"], temp_ban, pass_args=True)
PUNCH_HANDLER = CommandHandler("punch", punch, pass_args=True)
UNBAN_HANDLER = CommandHandler("unban", unban, pass_args=True)
ROAR_HANDLER = CommandHandler("roar", selfunban, pass_args=True)
PUNCHME_HANDLER = DisableAbleCommandHandler("punchme", punchme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(PUNCH_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(PUNCHME_HANDLER)

__mod_name__ = "BAN👨‍💻"
__handlers__ = [BAN_HANDLER, TEMPBAN_HANDLER, PUNCH_HANDLER, UNBAN_HANDLER, ROAR_HANDLER, PUNCHME_HANDLER]
