# ===============================================================
# Author: Firdauz Fanani
# Email: firdauzfanani@gmail.com
# Twitter: @firdauzfanani
# ===============================================================

from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import apiai,json
from lang_dict import *
import logging
import datetime
import time
import os,subprocess
import telegramcalendar

# You might need to add your tokens to this file...
from credentials import *

from dbhelper import DBHelper

db = DBHelper()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# Global vars:
IJIN = "ABSEN"
SET_IJIN,ATASAN,ALASAN,SELESAI,CALENDAR,ALASAN_IJIN,PILIH_KARYAWAN,BATAL, ALASAN_APP, SELESAI_APP, BATAL_APP, APP_DPP,LAMPIRAN_IJIN = range(13)
STATE = SET_IJIN

data_all_tele= db.get_tele_all()
print(data_all_tele)

Data_Ijin_Semua ={}
App_Manager_Semua ={}

def start(bot, update):
    """
    Start function. Displayed whenever the /start command is called.
    This function sets the language of the bot.
    """
    user = update.message.from_user

    # Create buttons to slect ijin:
    keyboard = [['TELAT', 'ABSEN', 'DINAS KELUAR']]

    # Create initial message:
    message = "Hey, Saya VIO Bot Ijin Absensi! \n\n\
Silahkan pilih ijin apa untuk memulai"

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text(message, reply_markup=reply_markup)

    print(Data_Ijin_Semua)

    #Untuk ceking biar sehari 1 ijin

#     cek_double=db.check_double(user.id)
#
#     if cek_double<1:
#         # Create buttons to slect ijin:
#         keyboard = [['TELAT', 'ABSEN', 'DINAS KELUAR']]
#
#         # Create initial message:
#         message = "Hey, Saya VIO Bot Ijin Absensi! \n\n\
# Silahkan pilih ijin apa untuk memulai"
#
#         reply_markup = ReplyKeyboardMarkup(keyboard,
#                                            one_time_keyboard=True,
#                                            resize_keyboard=True)
#         update.message.reply_text(message, reply_markup=reply_markup)
#
#         print(Data_Ijin_Semua)
#
#     else:
#         kirim_notdouble(bot, update)

    return SET_IJIN


def set_ijin(bot, update):
    """
    First handler with received data to set ijin globally.
    """
    # Set language:
    global IJIN
    IJIN = update.message.text
    user = update.message.from_user

    logger.info("Ijin set by {} to {}.".format(user.first_name, IJIN))
    update.message.reply_text(pilihtanggal[IJIN],
                              reply_markup=ReplyKeyboardRemove())


    Data_Ijin_Semua.setdefault(user.id, []).append(user.id)
    Data_Ijin_Semua.setdefault(user.id, []).append(IJIN)

    print(Data_Ijin_Semua)

    return CALENDAR

def calendar_handler(bot, update):
    user = update.message.from_user
    logger.info("Calender command requested by {}.".format(user.first_name))
    update.message.reply_text("Silahkan Pilih Tanggal: ",
                        reply_markup=telegramcalendar.create_calendar())

    return CALENDAR

def inline_handler(bot,update):
    user = update.callback_query.from_user.id
    selected,date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        bot.send_message(chat_id=update.callback_query.from_user.id,
                        text="Kamu memilih tanggal %s \n\n %s" % (date.strftime("%d/%m/%Y"),ijin_selected[IJIN]),
                        reply_markup=ReplyKeyboardRemove())

        logger.info("Calendar set to {}.".format(date.strftime('%d/%m/%Y')))

    Data_Ijin_Semua.setdefault(user, []).append(date.strftime("%Y-%m-%d"))

    print(Data_Ijin_Semua)

    return ATASAN

def atasan(bot, update):
    """
    atasan function.
    This will display the options from the main menu.
    """
    atasans=db.get_nama_manager()

    # Create buttons to slect language:
    keyboard = [[atasan] for atasan in atasans]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    user = update.message.from_user
    logger.info("Atasan command requested by {}.".format(user.first_name))
    update.message.reply_text(atasan_menu[IJIN], reply_markup=reply_markup)

    return ATASAN

def set_atasan(bot,update):
    atasan = update.message.text
    user = update.message.from_user
    logger.info("Atasan set by {} to {}.".format(user.first_name, atasan))
    update.message.reply_text(alasan_ijinapa[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(atasan)

    print(Data_Ijin_Semua)


    return ALASAN_IJIN

def alasan_ijin(bot, update):
    alasan = update.message.text
    user = update.message.from_user
    logger.info("Alasan_ijin set by {} to {}.".format(user.first_name, alasan))

    update.message.reply_text(ijin_lampiran[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(alasan)

    print(Data_Ijin_Semua)

    return ALASAN_IJIN

def dengan_lampiran_ijin(bot, update):
    user = update.message.from_user

    keyboard = [['Document', 'Photo']]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    logger.info("dengan_lampiran_ijin command requested by {}.".format(user.first_name))
    update.message.reply_text(pilihijinlampiran_attach[IJIN], reply_markup=reply_markup)

    print(Data_Ijin_Semua)

    return LAMPIRAN_IJIN

def define_dengan_lampiran_ijin_photo(bot, update):
    user = update.message.from_user
    logger.info("define_dengan_lampiran_ijin_photo command requested by {}.".format(user.first_name))
    update.message.reply_text(ijinlampiran_attach[IJIN], reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(update.message.text)

    print(Data_Ijin_Semua)

    return LAMPIRAN_IJIN

def set_dengan_lampiran_ijin_photo(bot, update):
    user = update.message.from_user

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    lampiran_id= update.message.photo[-1].file_id
    namafilesave= '%s_%s_%s' %(user.id,timestamp,lampiran_id)
    lampiran_file= bot.get_file(file_id=lampiran_id)
    lampiran_file.download('Lampiran/%s' %namafilesave)

    logger.info("set_dengan_lampiran_ijin_document set by {} to {}.".format(user.first_name, namafilesave))
    update.message.reply_text(selesaiin[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(namafilesave)

    print(Data_Ijin_Semua)

    return SELESAI

def define_dengan_lampiran_ijin_document(bot, update):
    user = update.message.from_user
    logger.info("define_dengan_lampiran_ijin_document command requested by {}.".format(user.first_name))
    update.message.reply_text(ijinlampiran_attach[IJIN], reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(update.message.text)

    print(Data_Ijin_Semua)

    return LAMPIRAN_IJIN

def set_dengan_lampiran_ijin_document(bot, update):
    user = update.message.from_user

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    lampiran = update.message.document.file_name
    lampiran_id= update.message.document.file_id
    namafilesave= '%s_%s_%s' %(user.id,timestamp,lampiran)
    lampiran_file= bot.get_file(file_id=lampiran_id)
    lampiran_file.download('Lampiran/%s' %namafilesave)

    logger.info("set_dengan_lampiran_ijin_document set by {} to {}.".format(user.first_name, namafilesave))
    update.message.reply_text(selesaiin[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(namafilesave)

    print(Data_Ijin_Semua)

    return SELESAI

def tanpa_lampiran_ijin(bot, update):
    lampiran = 'NULL'
    lampiran_tipe = 'NULL'
    user = update.message.from_user
    logger.info("dengan_lampiran_ijin set by {} to {}.".format(user.first_name, lampiran))

    update.message.reply_text(selesaiin[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    Data_Ijin_Semua.setdefault(user.id, []).append(lampiran)
    Data_Ijin_Semua.setdefault(user.id, []).append(lampiran_tipe)

    print(Data_Ijin_Semua)

    return LAMPIRAN_IJIN

def selesai(bot, update):
    user = update.message.from_user
    data= Data_Ijin_Semua[user.id]
    datainsert=db.insert_data_ijin(data)

    logger.info("ijin_selesai set by {}".format(user.first_name))
    update.message.reply_text(kalimatselesai[IJIN],
                              reply_markup=ReplyKeyboardRemove())


    data_tele=db.get_tele_manager(data)

    if data[5]=='NULL':
        process = subprocess.Popen("python3 notif_manager.py", shell=True)
    elif data[5]=='Document':
        lampfile = open('Lampiran/%s' %data[6] , 'rb')
        bot.send_document(chat_id=data_tele, document=lampfile)
        process = subprocess.Popen("python3 notif_manager.py", shell=True)
    elif data[5]=='Photo':
        lampfile = open('Lampiran/%s' %data[6] , 'rb')
        bot.send_photo(chat_id=data_tele, photo=lampfile)
        process = subprocess.Popen("python3 notif_manager.py", shell=True)

    del Data_Ijin_Semua[user.id]

    return SELESAI

def kirim_notdouble(bot, update):
    user = update.message.from_user
    bot.send_message(chat_id=user.id, text='Anda sudah melakukan ijin satu kali pada hari ini. Kembali lagi besok dengan /start')

def batal(bot, update):
    user = update.message.from_user
    data= Data_Ijin_Semua[user.id]
    del Data_Ijin_Semua[user.id]

    update.message.reply_text(batalkalimat[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    return BATAL

def batal_ijin(bot, update):
    user = update.message.from_user
    data= Data_Ijin_Semua[user.id]

    if data[5]=='NULL':
        del Data_Ijin_Semua[user.id]
    elif data[5]=='Document':
        os.remove("Lampiran/%s" %data[6])
        del Data_Ijin_Semua[user.id]

    update.message.reply_text(batalkalimat[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    return BATAL

def pilih_karyawan(bot, update):
    user = update.message.from_user

    logger.info("Pilih Karyawan command by {}".format(user.first_name))
    datakarijin= db.get_data_ijin_kar(user.id)

    keyboard = [[karyawan] for karyawan in datakarijin]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    update.message.reply_text(karyawan_menu[IJIN], reply_markup=reply_markup)

    return PILIH_KARYAWAN


def set_karyawan(bot,update):
    pilih_karyawan = update.message.text
    user = update.message.from_user
    logger.info("Pilih Karyawan set by {} to {}.".format(user.first_name, pilih_karyawan))
    update.message.reply_text(menuju_appdpp[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    App_Manager_Semua.setdefault(user.id, []).append(user.id)
    App_Manager_Semua.setdefault(user.id, []).append(pilih_karyawan)

    print(App_Manager_Semua)

    return APP_DPP

def pilih_appdpp(bot, update):
    user = update.message.from_user

    logger.info("Pilih appdpp command by {}".format(user.first_name))

    keyboard = [['APPROVE', 'DISAPPROVE']]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    update.message.reply_text(appdpp_menu[IJIN], reply_markup=reply_markup)

    return APP_DPP


def set_appdpp(bot,update):
    pilih_appdpp = update.message.text
    user = update.message.from_user
    logger.info("Pilih appdpp set by {} to {}.".format(user.first_name, pilih_appdpp))
    update.message.reply_text(alasan_Appapa[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    App_Manager_Semua.setdefault(user.id, []).append(pilih_appdpp)

    print(App_Manager_Semua)

    return ALASAN_APP

def alasan_app(bot,update):
    alasan_app = update.message.text
    user = update.message.from_user
    logger.info("Alasan_app set by {} to {}.".format(user.first_name, alasan_app))

    update.message.reply_text(selesaiin_app[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    App_Manager_Semua.setdefault(user.id, []).append(alasan_app)

    print(App_Manager_Semua)

    return ALASAN_APP

def selesai_app(bot, update):
    user = update.message.from_user
    data= App_Manager_Semua[user.id]

    datainsert=db.insert_insert_app(data)

    logger.info("ijin_selesai set by {}".format(user.first_name))
    update.message.reply_text(kalimatselesai_app[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    process = subprocess.Popen("python3 notif_karyawan.py", shell=True)

    del App_Manager_Semua[user.id]

    return SELESAI_APP

def batal_app(bot, update):
    user = update.message.from_user
    del App_Manager_Semua[user.id]

    update.message.reply_text(batalkalimat_app[IJIN],
                              reply_markup=ReplyKeyboardRemove())

    return BATAL_APP

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """
    global IJIN
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    karyawans=db.get_nama_karyawan()

    karyawann=','.join(karyawans)
    listkaryawan = karyawann.replace(',', '|')
    print(listkaryawan)

    # Add conversation handler with predefined states:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),CommandHandler('pilih_karyawan', pilih_karyawan)],

        states={
            SET_IJIN: [RegexHandler('^(TELAT|ABSEN|DINAS KELUAR)$', set_ijin)],

            ATASAN: [CommandHandler('atasan', atasan),RegexHandler('^(%s)$' %listkaryawan, set_atasan),CommandHandler('batal', batal)],

            ALASAN_IJIN: [CommandHandler('alasan_ijin', alasan_ijin),CommandHandler('dengan_lampiran_ijin', dengan_lampiran_ijin),CommandHandler('tanpa_lampiran_ijin', tanpa_lampiran_ijin),CommandHandler('batal', batal),MessageHandler(Filters.text, alasan_ijin)],

            LAMPIRAN_IJIN: [CommandHandler('dengan_lampiran_ijin', dengan_lampiran_ijin),RegexHandler('^(Document)$', define_dengan_lampiran_ijin_document),RegexHandler('^(Photo)$', define_dengan_lampiran_ijin_photo),CommandHandler('tanpa_lampiran_ijin', tanpa_lampiran_ijin),CommandHandler('selesai', selesai),CommandHandler('batal', batal),MessageHandler(Filters.document, set_dengan_lampiran_ijin_document),MessageHandler(Filters.photo, set_dengan_lampiran_ijin_photo)],

            SELESAI: [CommandHandler('selesai', selesai),CommandHandler('batal_ijin', batal_ijin),CommandHandler('start', start)],

            BATAL: [CommandHandler('batal', batal),CommandHandler('start', start)],

            CALENDAR: [CommandHandler('calendar', calendar_handler),CallbackQueryHandler(inline_handler)],

            PILIH_KARYAWAN: [CommandHandler('pilih_karyawan', pilih_karyawan),RegexHandler('^(%s)$' %listkaryawan, set_karyawan),CommandHandler('batal_app', batal_app)],

            APP_DPP: [CommandHandler('pilih_appdpp', pilih_appdpp),RegexHandler('^(APPROVE|DISAPPROVE)$', set_appdpp),CommandHandler('batal_app', batal_app)],

            ALASAN_APP: [CommandHandler('alasan_app', alasan_app),CommandHandler('selesai_app', selesai_app),MessageHandler(Filters.text, alasan_app),CommandHandler('batal_app', batal_app)],

            SELESAI_APP: [CommandHandler('selesai_app', selesai),CommandHandler('batal_app', batal_app),CommandHandler('pilih_karyawan', pilih_karyawan)],

            BATAL_APP: [CommandHandler('batal_app', batal_app),CommandHandler('pilih_karyawan', pilih_karyawan)]

        },

        fallbacks=[CommandHandler('help', help),CommandHandler('pilih_karyawan', pilih_karyawan),CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    # Log all errors:
    dp.add_error_handler(error)

    # Start DisAtBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == '__main__':
    main()
