RUN_STRINGS = (

    "Nereye gittiğini düşünüyorsun?",
    "Ha? Ne? Kaçtılar mı?",
    "ZZzzZZzz... Ha? ne? Oh, sadece onlar, boşver.",
    "Buraya geri gel!",
    "Çok hızlı değil...",
    "Duvara dikkat et!",
    "Beni onlarla yalnız bırakma!!",
    "Koşarsan ölürsün.",
    "Sana şaka, ben her yerdeyim",
    "Pişman olacaksın...",
    "Ayrıca /kickme'yi de deneyebilirsin, bunun eğlenceli olduğunu duydum.",
    "Git başkasını rahatsız et, burada kimsenin umurunda değil.",
    "Kaçabilirsin ama saklanamazsın.",
    "Sahip olduğun tek şey bu mu?",
    "Arkandayım...",
    "Bir şirketin var!",
    "Bunu kolay yoldan da yapabiliriz, zor yoldan da.",
    "Anlamıyorsun değil mi?",
    "Evet, kaçsan iyi olur!",
    "Lütfen, bana ne kadar umursadığımı hatırlat?",
    "Yerinde olsam daha hızlı koşardım.",
    "Kesinlikle aradığımız droid bu.",
    "Şanslar her zaman lehinize olsun.",
    "Ünlü son sözler.",
    "Ve sonsuza dek ortadan kayboldular, bir daha asla görülmediler.",
    "\"Ah, bana bak! Çok havalıyım, bir bottan kaçabilirim!\" - bu kişi",
    "Evet evet, /kickme'ye dokunman yeterli.",
    "Al, bu yüzüğü al ve hazır oradayken Mordor'a git.",
    "Efsaneye göre, hala koşuyorlar...",
    "Harry Potter'ın aksine, ailen seni benden koruyamaz.",
    "Korku öfkeye yol açar. Öfke nefrete yol açar. Nefret acıya yol açar. Korku içinde koşmaya devam edersen, yapabilirsin"
    "bir sonraki Vader ol.",
    "Birden çok hesaplamadan sonra, kurnazlıklarınıza olan ilgimin tam olarak 0 olduğuna karar verdim.",
    "Efsaneye göre, hala koşuyorlar.",
    "Devam et, zaten seni burada istediğimizden emin değilim.",
    "Sen bir büyücüsün- Oh. Bekle. Sen Harry değilsin, devam et.",
    "KORİDORLARDA KOŞMAK YOK!",
    "Görüşürüz bebeğim.",
    "Köpekleri kim dışarı bıraktı?",
    "Komik, çünkü kimsenin umurunda değil.",
    "Ah, ne israf. Bunu sevdim.",
    "Açıkçası canım, umurumda değil.",
    "Benim milkshake'im tüm çocukları bahçeye getiriyor... O halde daha hızlı koş!",
    "Gerçeği İŞLEYEMEZSİN!",
    "Uzun zaman önce, çok uzak bir galakside... Birileri bunu umursardı. Artık değil.",
    "Hey, şuna bir bak! Kaçınılmaz engelden kaçıyorlar... Şirin.",
    "Önce Han vurdu. Ben de vuracağım.",
    "Neyin peşindesin, beyaz bir tavşan mı?",
    "Doktorun dediği gibi... KOŞ!",
)

SLAP_TEMPLATES = (
    "{user1} {hits} {user2} with a {item}.",
    "{user1} {hits} {user2} in the face with a {item}.",
    "{user1} {hits} {user2} around a bit with a {item}.",
    "{user1} {throws} a {item} at {user2}.",
    "{user1} grabs a {item} and {throws} it at {user2}'s face.",
    "{user1} launches a {item} in {user2}'s general direction.",
    "{user1} starts slapping {user2} silly with a {item}.",
    "{user1} pins {user2} down and repeatedly {hits} them with a {item}.",
    "{user1} grabs up a {item} and {hits} {user2} with it.",
    "{user1} ties {user2} to a chair and {throws} a {item} at them.",
    "{user1} gave a friendly push to help {user2} learn to swim in lava."
)

ITEMS = (
    "Demir Döküm tencere",
    "büyük alabalık",
    "beysbol sopası",
    "kriket sopası",
    "tahta baston",
    "çivi",
    "yazıcı",
    "kürek",
    "CRT monitör",
    "fizik ders kitabı",
    "tost makinası",
    "Richard Stallman'ın portresi",
    "televizyon",
    "beş tonluk kamyon",
    "koli bandı rulosu",
    "kitap",
    "dizüstü bilgisayar",
    "eski televizyon",
    "taş çuvalı",
    "gökkuşağı alabalığı",
    "plastik tavuk",
    "çivili yarasa",
    "yangın söndürücü",
    "ağır taş",
    "kir parçası",
    "arı kovanı",
    "çürük et parçası",
    "dayanmak",
    "ton tuğla",
)

THROW = (
    "atar",
    "kaçışlar",
    "şakalar",
    "atlar"
)

HIT = (
    "hit",
    "vurmak",
    "tokatlar",
    "smacks",
    "baslar",
)

MARKDOWN_HELP = """
Markdown, telegram tarafından desteklenen çok güçlü bir biçimlendirme aracıdır. {}, olduğundan emin olmak için bazı geliştirmelere sahiptir.
\Saved mesajlar doğru şekilde ayrıştırılır ve düğmeler oluşturmanıza olanak tanır.

- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.
"""

EnglishStrings = {
    "send-help": """*Main commands available*:
 - /start: start the bot
 - /help or /help <module name>: PM's you info about that module.
 - /lang: Change bot language
 - /settings:
   - in PM: will send you your settings for all supported modules.
   - in a group: will redirect you to pm, with all that chat's settings.
   {}
   """,

    "send-group-settings": """Hi there! There are quite a few settings for *{}* - go ahead and pick what
you're interested in.""",

#Misc
"RUNS-K": RUN_STRINGS,
"SLAP_TEMPLATES-K": SLAP_TEMPLATES,
"ITEMS-K": ITEMS,
"HIT-K": HIT,
"THROW-K": THROW,
"ITEMP-K": ITEMS,
"ITEMR-K": ITEMS,
"MARKDOWN_HELP-K": MARKDOWN_HELP,

#GDPR
"send-gdpr": """Your personal data has been deleted.\n\nNote that this will not unban \
you from any chats, as that is telegram data, not YanaBot data.
Flooding, warns, and gbans are also preserved, as of \
[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-to-erasure/), "
which clearly states that the right to erasure does not apply \
\"for the performance of a task carried out in the public interest\", as is \
the case for the aforementioned pieces of data."""

}
