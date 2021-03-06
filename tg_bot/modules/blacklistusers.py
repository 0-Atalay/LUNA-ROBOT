# Module to blacklist users and prevent them from using commands by @TheRealPhoenix
from typing import List

from telegram import Bot, Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async
from telegram.utils.helpers import mention_html

import tg_bot.modules.sql.blacklistusers_sql as sql
from tg_bot import dispatcher, OWNER_ID, DEV_USERS, SUDO_USERS, WHITELIST_USERS, SUPPORT_USERS
from tg_bot.modules.helper_funcs.chat_status import dev_plus
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text, extract_user
from tg_bot.modules.log_channel import gloggable

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS + SUDO_USERS + WHITELIST_USERS + SUPPORT_USERS
BLABLEUSERS = [OWNER_ID] + DEV_USERS


@run_async
@dev_plus
@gloggable
def bl_user(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("bunun bir kullanıcı olduğundan şüpheliyim.")
        return ""

    if user_id == bot.id:
        message.reply_text("Kendimi görmezden geliyorsam işimi nasıl yapacağım?")
        return ""

    if user_id in BLACKLISTWHITELIST:
        message.reply_text("Hayır!\nAfetleri fark etmek benim işim.")
        return ""

    try:
        target_user = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Bu kullanıcıyı bulamıyorum.")
            return ""
        else:
            raise

    sql.blacklist_user(user_id, reason)
    message.reply_text("Bu kullanıcının varlığını görmezden geleceğim!")
    log_message = (f"#BLACKLIST\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(target_user.id, target_user.first_name)}")
    if reason:
        log_message += f"\n<b>Reason:</b> {reason}"

    return log_message


@run_async
@dev_plus
@gloggable
def unbl_user(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("Bunun bir kullanıcı olduğundan şüpheliyim.")
        return ""

    if user_id == bot.id:
        message.reply_text("Her zaman kendimi fark ederim.")
        return ""

    try:
        target_user = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Bu kullanıcıyı bulamıyorum.")
            return ""
        else:
            raise

    if sql.is_user_blacklisted(user_id):

        sql.unblacklist_user(user_id)
        message.reply_text("*kullanıcıyı uyarır*")
        log_message = (f"#UNBLACKLIST\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(target_user.id, target_user.first_name)}")

        return log_message

    else:
        message.reply_text("Yine de onları görmezden gelmiyorum!")
        return ""


@run_async
@dev_plus
def bl_users(bot: Bot, update: Update):
    users = []

    for each_user in sql.BLACKLIST_USERS:

        user = bot.get_chat(each_user)
        reason = sql.get_reason(each_user)

        if reason:
            users.append(f"• {mention_html(user.id, user.first_name)} :- {reason}")
        else:
            users.append(f"• {mention_html(user.id, user.first_name)}")

    message = "<b>Kara Listeye Alınan Kullanıcılar</b>\n"
    if not users:
        message += "Henüz kimse görmezden gelinmiyor."
    else:
        message += '\n'.join(users)

    update.effective_message.reply_text(message, parse_mode=ParseMode.HTML)


def __user_info__(user_id):
    is_blacklisted = sql.is_user_blacklisted(user_id)

    text = "Genel Olarak Yok Sayılan: <b>{}</b>"

    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nNedeni: <code>{reason}</code>"
    else:
        text = text.format("No")

    return text


BL_HANDLER = CommandHandler("ignore", bl_user, pass_args=True)
UNBL_HANDLER = CommandHandler("notice", unbl_user, pass_args=True)
BLUSERS_HANDLER = CommandHandler("ignoredlist", bl_users)

dispatcher.add_handler(BL_HANDLER)
dispatcher.add_handler(UNBL_HANDLER)
dispatcher.add_handler(BLUSERS_HANDLER)

__mod_name__ = "BLACKLISTING USERS⚫"
__handlers__ = [BL_HANDLER, UNBL_HANDLER, BLUSERS_HANDLER]
