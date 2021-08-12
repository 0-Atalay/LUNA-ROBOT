import random
from telegram.ext import run_async, Filters
from telegram import Message, Chat, Update, Bot, MessageEntity
from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler

SFW_STRINGS = (
    "KENDİMİ KORONAVİRÜS'TEN NASIL KORUYABİLİRİM?",
    "ELLERİNİZİ SIK YIKANIN",
    "🚴‍♂️EGZERSİZ VE DOĞRU UYKU🛌 BAĞIŞIKLIK SİSTEMİNİ GÜÇLENDİRİR",
    "HİJYEN ALIŞKANLIKLARINI HER ZAMAN SAKLAYIN",
    "DİĞERLERİ İLE İLETİŞİME GEÇMEKTEN KAÇININ",
    "😷ENFEKTE HASTALARLA MUHAFAZA EDERKEN YÜZ MASKESİ TAKIN",
    "ÖKSÜRÜRKEN VE BURUN SÜFLERKEN DOKU KULLANIN"
    "GIDALARI DİKKATLİCE YIKALAYIN VE HAZIRLAYIN",
    "EVDE KAL GÜVENDE KAL🇹🇷".,
  )

@run_async
def corona(bot: Bot, update: Update):
    bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    message = update.effective_message
    if message.reply_to_message:
      message.reply_to_message.reply_text(random.choice(SFW_STRINGS))
    else:
      message.reply_text(random.choice(SFW_STRINGS))

__help__ = """
- /corona  😷.
"""

__mod_name__ = "önlem😷"

CRNA_HANDLER = DisableAbleCommandHandler("corona", corona)

dispatcher.add_handler(CRNA_HANDLER)
