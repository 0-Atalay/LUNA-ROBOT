import html
import os
from typing import Optional, List

import requests
from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown, mention_html

from tg_bot import dispatcher, TOKEN
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import bot_admin, can_promote, user_admin, can_pin, connection_status
from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.log_channel import loggable
from tg_bot.modules.connection import connected
from tg_bot.modules.translations.strings import tld

@run_async
@bot_admin
@user_admin
@loggable
def promote(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    conn = connected(bot, update, chat, user.id)
    if not conn == False:
        chatD = dispatcher.bot.getChat(conn)
    else:
        chatD = update.effective_chat
        if chat.type == "private":
            exit(1)

    if not chatD.get_member(bot.id).can_promote_members:
        update.effective_message.reply_text("İnsanları burada terfi ettiremem/indirgeyemem! "
                                            "Yönetici olduğumdan ve yeni yöneticiler atayabildiğimden emin olun.")
        exit(1)

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(tld(chat.id, "Bir kullanıcıdan bahsediyor gibi görünmüyorsun."))
        return ""

    user_member = chatD.get_member(user_id)
    if user_member.status == 'administrator' or user_member.status == 'creator':
        message.reply_text(tld(chat.id, "Zaten yönetici olan birini nasıl terfi ettirebilirim?"))
        return ""

    if user_id == bot.id:
        message.reply_text(tld(chat.id, "Kendimi terfi ettiremiyorum! Bunu benim için yapacak bir yönetici bulun."))
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chatD.get_member(bot.id)

    bot.promoteChatMember(chatD.id, user_id,
                          can_change_info=bot_member.can_change_info,
                          can_post_messages=bot_member.can_post_messages,
                          can_edit_messages=bot_member.can_edit_messages,
                          can_delete_messages=bot_member.can_delete_messages,
                          #can_invite_users=bot_member.can_invite_users,
                          can_restrict_members=bot_member.can_restrict_members,
                          can_pin_messages=bot_member.can_pin_messages,
                          can_promote_members=bot_member.can_promote_members)

    message.reply_text(tld(chat.id, f"Successfully promoted {mention_html(user_member.user.id, user_member.user.first_name)} in {html.escape(chatD.title)}!"), parse_mode=ParseMode.HTML)
    return f"<b>{html.escape(chatD.title)}:</b>" \
            "\n#PROMOTED" \
           f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}" \
           f"\n<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"


@run_async
@bot_admin
@user_admin
@loggable
def demote(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    conn = connected(bot, update, chat, user.id)
    if not conn == False:
        chatD = dispatcher.bot.getChat(conn)
    else:
        chatD = update.effective_chat
        if chat.type == "private":
            exit(1)

    if not chatD.get_member(bot.id).can_promote_members:
        update.effective_message.reply_text("İnsanları burada terfi ettiremem/indirgeyemem! "
                                            "Yönetici olduğumdan ve yeni yöneticiler atayabildiğimden emin olun.🤡")
        exit(1)

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(tld(chat.id, "Bir kullanıcıdan bahsediyor gibi görünmüyorsun."))
        return ""

    user_member = chatD.get_member(user_id)
    if user_member.status == 'creator':
        message.reply_text(tld(chat.id, "Bu kişi sohbeti OLUŞTURDU, onların sıralamasını nasıl düşürürüm?"))
        return ""

    if not user_member.status == 'administrator':
        message.reply_text(tld(chat.id, "Terfi edilmeyen şeyin derecesi düşürülemez!"))
        return ""

    if user_id == bot.id:
        message.reply_text(tld(chat.id, "kendimi küçültemiyorum!"))
        return ""

    try:
        bot.promoteChatMember(int(chatD.id), int(user_id),
                              can_change_info=False,
                              can_post_messages=False,
                              can_edit_messages=False,
                              can_delete_messages=False,
                              can_invite_users=False,
                              can_restrict_members=False,
                              can_pin_messages=False,
                              can_promote_members=False)
        message.reply_text(tld(chat.id, f"Successfully demoted in *{chatD.title}*!"), parse_mode=ParseMode.MARKDOWN)
        return f"<b>{html.escape(chatD.title)}:</b>" \
                "\n#DEMOTED" \
               f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}" \
               f"\n<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"

    except BadRequest:
        message.reply_text(
            tld(chat.id, "İndirilemedi. Yönetici olmayabilirim veya yönetici statüsü başka bir kullanıcı tarafından atanmış olabilir, bu yüzden onlara göre işlem yapamam!")
            )
        return ""

        


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(bot: Bot, update: Update, args: List[str]) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    is_group = chat.type != "private" and chat.type != "channel"

    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (args[0].lower() == 'notify' or args[0].lower() == 'loud' or args[0].lower() == 'violent')

    if prev_message and is_group:
        try:
            bot.pinChatMessage(chat.id, prev_message.message_id, disable_notification=is_silent)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        return "<b>{}:</b>" \
               "\n#PINNED" \
               "\n<b>Admin:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name))

    return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(bot: Bot, update: Update) -> str:
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    return "<b>{}:</b>" \
           "\n#UNPINNED" \
           "\n<b>Admin:</b> {}".format(html.escape(chat.title),
                                       mention_html(user.id, user.first_name))


@run_async
@bot_admin
@user_admin
def invite(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    if chat.username:
        update.effective_message.reply_text(chat.username)
    elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text("Davet bağlantısına erişimim yok, izinlerimi değiştirmeyi deneyin!")
    else:
        update.effective_message.reply_text("Sana sadece süper gruplar ve kanallar için davet linkleri verebilirim, üzgünüm!")

@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text("Bir kullanıcıdan bahsediyor gibi görünmüyorsun.")
        return

    if user_member.status == 'creator':
        message.reply_text("Bu kişi sohbeti OLUŞTURDU, ona nasıl özel başlık ayarlayabilirim?")
        return

    if not user_member.status == 'administrator':
        message.reply_text("Yönetici olmayanlar için başlık ayarlanamıyor!\nÖzel başlık ayarlamak için önce onları tanıtın!")
        return

    if user_id == bot.id:
        message.reply_text("Kendi başlığımı kendim belirleyemem! Beni yönetici yapanın benim için yapmasını sağlayın.")
        return

    if not title:
        message.reply_text("Boş başlık ayarlamak hiçbir şey yapmaz")
        return

    if len(title) > 16:
        message.reply_text("Başlık uzunluğu 16 karakterden uzun.\n16 karaktere kısaltılıyor.")

    result = requests.post(f"https://api.telegram.org/bot{TOKEN}/setChatAdministratorCustomTitle"
                           f"?chat_id={chat.id}"
                           f"&user_id={user_id}"
                           f"&custom_title={title}")
    status = result.json()["ok"]

    if status is True:
        bot.sendMessage(chat.id, f"Sucessfully set title for <code>{user_member.user.first_name or user_id}</code> "
                                 f"to <code>{title[:16]}</code>!", parse_mode=ParseMode.HTML)
    else:
        description = result.json()["description"]
        if description == "Kötü İstek: kullanıcının özel başlığını değiştirmek için yeterli hak yok":
            message.reply_text("Terfi ettirmediğim yöneticiler için özel başlık belirleyemiyorum!")


@run_async
@bot_admin
@user_admin
def setchatpic(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    user_member = chat.get_member(user.id)
    if user_member.can_change_info == False:
       msg.reply_text("Grup bilgilerini değiştirme hakkınız yok!")
       return

    if msg.reply_to_message:
       if msg.reply_to_message.photo:
          pic_id = msg.reply_to_message.photo[-1].file_id
       elif msg.reply_to_message.document:
          pic_id = msg.reply_to_message.document.file_id
       else:
          msg.reply_text("Bazı fotoğrafları yalnızca sohbet resmi olarak ayarlayabilirsiniz!")
          return
       dlmsg = msg.reply_text("Hold on...")
       tpic = bot.get_file(pic_id)
       tpic.download('gpic.png')
       try:
          with open('gpic.png', 'rb') as chatp:
               bot.set_chat_photo(int(chat.id), photo=chatp)
               msg.reply_text("Yeni sohbeti başarıyla ayarla Resim!")
       except BadRequest as excp:
          msg.reply_text(f"Error! {excp.message}")
       finally:
          dlmsg.delete()
          if os.path.isfile('gpic.png'):
             os.remove("gpic.png")
    else:
          msg.reply_text("Yeni sohbet resmi ayarlamak için bir fotoğrafa veya dosyaya yanıt verin!")


@run_async
@bot_admin
@user_admin
def rmchatpic(bot: Bot, update: Update):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    user_member = chat.get_member(user.id)
    if user_member.can_change_info == False:
       msg.reply_text("Grup fotoğrafını silmek için yeterli hakkınız yok")
       return
    try:
        bot.delete_chat_photo(int(chat.id))
        msg.reply_text("Sohbetin profil fotoğrafı başarıyla silindi!")
    except BadRequest as excp:
       msg.reply_text(f"Error! {excp.message}.")
       return


@run_async
def adminlist(bot: Bot, update: Update):
    administrators = update.effective_chat.get_administrators()
    msg = update.effective_message
    text = "yöneticiler *{}*:".format(update.effective_chat.title or "bu sohbet")
    for admin in administrators:
        user = admin.user
        status = admin.status
        name = "[{}](tg://user?id={})".format(user.first_name + " " + (user.last_name or ""), user.id)
        if user.username:
            name = name = escape_markdown("@" + user.username)
        if status == "sahibi ":
            text += "\n 🔱 sahibi:"
            text += "\n` • `{} \n\n • *Administrators*:".format(name)




    for admin in administrators:
        user = admin.user
        status = admin.status
        chat = update.effective_chat
        count = chat.get_members_count()
        name = "[{}](tg://user?id={})".format(user.first_name + " " + (user.last_name or ""), user.id)
        if user.username:
            name = escape_markdown("@" + user.username)
            
        if status == "yöneticiler":
            text += "\n`👮🏻 `{}".format(name)
            members = "\n\n*members:*\n`🙍‍♂️ ` {} users".format(count)
            
    msg.reply_text(text + members, parse_mode=ParseMode.MARKDOWN)



def __chat_settings__(chat_id, user_id):
    return "You are *admin*: `{}`".format(
        dispatcher.bot.get_chat_member(chat_id, user_id).status in ("administrator", "creator"))


__help__ = """
 - /adminlist: sohbetteki yöneticilerin listesi

*Admin only:*
 - /pin: yanıtlanan mesajı sessizce sabitler - kullanıcılara bildirim vermek için 'yüksek sesle' veya 'bildir' ekleyin.
 - /unpin: şu anda sabitlenmiş mesajın sabitlemesini kaldırır
 - /invitelink: davet bağlantısı alır
 - /promote: yanıtladığı kullanıcıyı tanıtır
 - /demote: yanıtladığı kullanıcının değerini düşürür
 - /settitle: botun terfi ettirdiği bir yönetici için özel bir başlık ayarlar.
 - /settitle: Bot tarafından terfi ettirilen bir yönetici için özel bir
 - /setgpic: Grup profili resmini ayarlamak için dosyaya veya fotoğrafa yanıt olarak!
 - /delgpic: Yukarıdakiyle aynı, ancak grup profil resmini kaldırmak için!

"""


PIN_HANDLER = CommandHandler("pin", pin, pass_args=True, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = CommandHandler("invitelink", invite, filters=Filters.group)

PROMOTE_HANDLER = CommandHandler("promote", promote, pass_args=True, filters=Filters.group)
DEMOTE_HANDLER = CommandHandler("demote", demote, pass_args=True, filters=Filters.group)


SET_TITLE_HANDLER = CommandHandler("settitle", set_title, pass_args=True)
CHAT_PIC_HANDLER = CommandHandler("setgpic", setchatpic, filters=Filters.group)
DEL_CHAT_PIC_HANDLER = CommandHandler("delgpic", rmchatpic, filters=Filters.group)




ADMINLIST_HANDLER = DisableAbleCommandHandler("adminlist", adminlist, filters=Filters.group)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(CHAT_PIC_HANDLER)
dispatcher.add_handler(DEL_CHAT_PIC_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)

__mod_name__ = "ADMIN"

__command_list__ = ["adminlist", "admins", "invitelink"]

__handlers__ = [ADMINLIST_HANDLER, PIN_HANDLER, UNPIN_HANDLER,
                INVITE_HANDLER, PROMOTE_HANDLER, DEMOTE_HANDLER, SET_TITLE_HANDLER, CHAT_PIC_HANDLER, DEL_CHAT_PIC_HANDLER]
