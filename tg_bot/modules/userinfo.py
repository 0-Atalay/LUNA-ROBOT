import html
from typing import List

from telegram import Bot, Update, ParseMode, MAX_MESSAGE_LENGTH
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import tg_bot.modules.sql.userinfo_sql as sql
from tg_bot import dispatcher, SUDO_USERS, DEV_USERS
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.extraction import extract_user


@run_async
def about_me(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    user_id = extract_user(message, args)

    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text(f"*{user.first_name}*:\n{escape_markdown(info)}",
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(f"{username} henüz kendileri hakkında bir bilgi mesajı oluşturmadı!")
    else:
        güncelleme . etkili_mesaj . answer_text ( "Kendiniz hakkında henüz bir bilgi mesajı oluşturmadınız!" )


@run_async
def set_about_me(bot: Bot, update: Update):
    message = update.effective_message
    user_id = message.from_user.id
    if message.reply_to_message:
        repl_message = message.reply_to_message
        repl_user_id = repl_message.from_user.id
        if repl_user_id == bot.id and (user_id in SUDO_USERS or user_id in DEV_USERS):
            user_id = repl_user_id

    text = message.text
    info = text.split(None, 1)

    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            if user_id == bot.id:
                message.reply_text("Bilgilerim güncellendi!")
            else:
                message.reply_text("Bilgileriniz güncellendi!")
        else:
            message.reply_text(
                "Bilginin {} karakterin altında olması gerekiyor! Var {}.".format(MAX_MESSAGE_LENGTH // 4, len(info[1])))


@run_async
def about_bio(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    user_id = extract_user(message, args)
    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text("*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(f"{username} henüz kendileri hakkında bir mesaj oluşturmadı!")
    else:
        update.effective_message.reply_text("Henüz kendin hakkında bir biyografi setin yok!")


@run_async
def set_about_bio(bot: Bot, update: Update):
    message = update.effective_message
    sender_id = update.effective_user.id

    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id

        if user_id == message.from_user.id:
            message.reply_text("Ha, kendi biyografini belirleyemezsin! Burada başkalarının insafına kalmışsın...")
            return

        if user_id == bot.id and sender_id not in SUDO_USERS and sender_id not in DEV_USERS:
            message.reply_text("evet, biyografimi ayarlamak için yalnızca sudo kullanıcılarına veya geliştiricilerine güveniyorum.")
            return

        text = message.text
        bio = text.split(None, 1)  # sadece cmd'yi kaldırmak için python'un maxsplit'ini kullanın, dolayısıyla yeni satırları koruyun

        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text("{}'nin biyografisi güncellendi!".format(repl_message.from_user.first_name))
            else:
                message.reply_text(
                    "Bir biyografinin {} karakterin altında olması gerekir! {} ayarlamayı denediniz".format(
                       MAX_MESSAGE_LENGTH // 4, len(bio[1])))

    else:
        message.reply_text("Biyografisini ayarlamak için birinin mesajına cevap verin!")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    if bio and me:
        return f"\n<b>About user:</b>\n{me}\n<b>What others say:</b>\n{bio}\n"
    elif bio:
        return f"\n<b>What others say:</b>\n{bio}\n"
    elif me:
        return f"\n<b>About user:</b>\n{me}\n"
    else:
        return "\n"


__help__ = """
 - /setbio <text>: yanıtlarken, başka bir kullanıcının biyografisini kaydedecek
 - /bio: sizin veya başka bir kullanıcının biyografisini alacak. Bu kendi başınıza ayarlanamaz.
 - /setme <text>: bilgilerini ayarlayacak
 - /me: sizin veya başka bir kullanıcının bilgilerini alacak
"""

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio, pass_args=True)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me, pass_args=True)

dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)

__mod_name__ = "BIOS & ABOUTS"
__command_list__ = ["setbio", "bio", "setme", "me"]
__handlers__ = [SET_BIO_HANDLER, GET_BIO_HANDLER, SET_ABOUT_HANDLER, GET_ABOUT_HANDLER]
