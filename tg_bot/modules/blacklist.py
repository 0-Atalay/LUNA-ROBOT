import html
import re
from typing import List

from telegram import Bot, Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async

import tg_bot.modules.sql.blacklist_sql as sql
from tg_bot import dispatcher, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import user_admin, user_not_admin, connection_status
from tg_bot.modules.helper_funcs.extraction import extract_text
from tg_bot.modules.helper_funcs.misc import split_message

BLACKLIST_GROUP = 11


@run_async
@connection_status
def blacklist(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message
    chat = update.effective_chat

    update_chat_title = chat.title
    message_chat_title = update.effective_message.chat.title

    if update_chat_title == message_chat_title:
        base_blacklist_string = "Mevcut <b>kara listeye alınmış</b> kelimeler:\n"
    else:
        base_blacklist_string = f"<b>{update_chat_title}</b> içindeki mevcut <b>kara listeye alınmış</b> kelimeler:\n"

    all_blacklisted = sql.get_chat_blacklist(chat.id)

    filter_list = base_blacklist_string

    if len(args) > 0 and args[0].lower() == 'copy':
        for trigger in all_blacklisted:
            filter_list += f"<code>{html.escape(trigger)}</code>\n"
    else:
        for trigger in all_blacklisted:
            filter_list += f" - <code>{html.escape(trigger)}</code>\n"

    split_text = split_message(filter_list)
    for text in split_text:
        if text == base_blacklist_string:
            if update_chat_title == message_chat_title:
                msg.reply_text("Burada kara listeye alınmış mesaj yok!")
            else:
                msg.reply_text(f"<b>{update_chat_title}</b> içinde kara listeye alınmış mesaj yok!",
                               parse_mode=ParseMode.HTML)
            return
        msg.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
@connection_status
@user_admin
def add_blacklist(bot: Bot, update: Update):
    msg = update.effective_message
    chat = update.effective_chat
    words = msg.text.split(None, 1)

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(set(trigger.strip() for trigger in text.split("\n") if trigger.strip()))

        for trigger in to_blacklist:
            sql.add_to_blacklist(chat.id, trigger.lower())

        if len(to_blacklist) == 1:
            msg.reply_text(f"Kara listeye <code>{html.escape(to_blacklist[0])}</code> eklendi!",
                           parse_mode=ParseMode.HTML)

        else:
            msg.reply_text(f"Kara listeye <code>{len(to_blacklist)}</code> tetikleyicileri eklendi.",
                           parse_mode=ParseMode.HTML)

    else:
        msg.reply_text("Kara listeden hangi kelimeleri çıkarmak istediğini söyle.")


@run_async
@connection_status
@user_admin
def unblacklist(bot: Bot, update: Update):
    msg = update.effective_message
    chat = update.effective_chat
    words = msg.text.split(None, 1)

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(set(trigger.strip() for trigger in text.split("\n") if trigger.strip()))
        successful = 0

        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat.id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                msg.reply_text(f"Kara listeden <code>{html.escape(to_unblacklist[0])}</code> kaldırıldı!",
                               parse_mode=ParseMode.HTML)
            else:
                msg.reply_text("Bu kara listeye alınmış bir tetikleyici değil...!")

        elif successful == len(to_unblacklist):
            msg.reply_text(f"Kara listeden <code>{successful}</code> tetikleyicileri kaldırıldı.", parse_mode=ParseMode.HTML)

        elif not successful:
            msg.reply_text("Bu tetikleyicilerin hiçbiri mevcut olmadığından kaldırılmadı.", parse_mode=ParseMode.HTML)

        else:
            msg.reply_text(f"Kara listeden <code>{successful}</code> tetikleyicileri kaldırıldı."
                           f" {len(to_unblacklist) - successful} mevcut değildi, dolayısıyla kaldırılmadı.",
                           parse_mode=ParseMode.HTML)
    else:
        msg.reply_text("Kara listeden hangi kelimeleri çıkarmak istediğini söyle.")


@run_async
@connection_status
@user_not_admin
def del_blacklist(bot: Bot, update: Update):
    chat = update.effective_chat
    message = update.effective_message
    to_match = extract_text(message)

    if not to_match:
        return

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Silinecek mesaj bulunamadı":
                    pass
                else:
                    LOGGER.exception("Kara liste mesajı silinirken hata oluştu.")
            break


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "{} kara listeye alınmış kelime var.".format(blacklisted)


def __stats__():
    return "{} sohbetlerde {} kara liste tetiklenir.".format(sql.num_blacklist_filters(),
                                                            sql.num_blacklist_filter_chats())


__help__ = """
Kara listeler, belirli tetikleyicilerin bir grupta söylenmesini engellemek için kullanılır. Tetikleyiciden bahsedildiğinde, \ mesaj hemen silinecektir. Bazen bunu uyarı filtreleriyle eşleştirmek iyi bir kombinasyondur! 


*NOT:* kara listeler grup yöneticilerini etkilemez. 

- /kara liste: Mevcut kara listeye alınmış kelimeleri görüntüleyin. 

*Yalnızca yönetici:*

 - /addblacklist <tetikleyiciler>: Kara listeye bir tetikleyici ekleyin. Her satır bir tetikleyici olarak kabul edilir, bu nedenle farklı \ satırları, birden çok tetikleyici eklemenize izin verir. 
- /unblacklist <tetikleyiciler>: Tetikleyicileri kara listeden kaldırın. Aynı satırsonu mantığı burada da geçerlidir, böylece \'yi kaldırabilirsiniz. aynı anda birden fazla tetikleyici. 
- /rmblacklist <tetikleyiciler>: Yukarıdakiyle aynı. 
"""

BLACKLIST_HANDLER = DisableAbleCommandHandler("blacklist", blacklist, pass_args=True, admin_ok=True)
ADD_BLACKLIST_HANDLER = CommandHandler("addblacklist", add_blacklist)
UNBLACKLIST_HANDLER = CommandHandler(["unblacklist", "rmblacklist"], unblacklist)
BLACKLIST_DEL_HANDLER = MessageHandler((Filters.text | Filters.command | Filters.sticker | Filters.photo) & Filters.group, del_blacklist, edited_updates=True)
dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__mod_name__ = "WORD BLACKLIST🖤"
__handlers__ = [BLACKLIST_HANDLER, ADD_BLACKLIST_HANDLER, UNBLACKLIST_HANDLER, (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP)]
