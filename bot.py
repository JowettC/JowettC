# -*- coding: utf-8 -*-
import telebot
import logging
import config
import datetime
import json
import traceback
import calendar
import requests

import time
import telegram

# from requests_futures.sessions import FuturesSession
from telegram import (TelegramObject, ReplyKeyboardMarkup, KeyboardButton)
from telebot import types
from telegram.ext import CallbackQueryHandler
from telegram import ReplyKeyboardRemove
from datetime import date
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, ConversationHandler)
# session = FuturesSession()

date_of_cro = ""
message_id_toDel = -1
bot = telebot.AsyncTeleBot(config.TOKEN, threaded=True)

# start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Main Menu",
                     reply_markup=generate_mainMenu_markup())

# cluster menu
@bot.callback_query_handler(func=lambda call: True if call.data == "cback" else False)
def announcement_menu(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Cluster", reply_markup=generate_cluster_markup())

# main menu
@bot.callback_query_handler(func=lambda call: True if call.data == "HQ" or call.data == "AC" or call.data == "ARC" or call.data == "EC" or call.data == "back" else False)
def announcement_menu(call):
    print(call.message.chat.id)
    if call.data == "HQ" or call.data == "AC" or call.data == "ARC" or call.data == "EC":
        url = "http://13.229.89.122:8080/addToCluster"
        data = {"UID": call.from_user.id, "cluster": call.data}
        repsonse = requests.post(url, data).text
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Main Menu", reply_markup=generate_mainMenu_markup())


# Announcement
@bot.callback_query_handler(func=lambda call: True if call.data == "Announcement" or call.data == "aback" else False)
def announcement_menu(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Announcements:", reply_markup=generate_announcement_markup())


@bot.callback_query_handler(func=lambda call: True if call.data[0:12] == "AnnounceData" else False)
def announcement_details(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Announcement:" + call.data[12:-1],
                          reply_markup=generate_announcement_details())

# Routine Order
@bot.callback_query_handler(func=lambda call: True if call.data == "RO" or call.data == "rback" or call.data == "rtback" else False)
def RO_menu(call):
    global message_id_toDel
    try:
        if(message_id_toDel != -1):
            msg = bot.delete_message(call.message.chat.id,
                                     message_id_toDel)
            # task.wait()
            print(message_id_toDel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Routine Order", reply_markup=generate_RO_markup())
    except:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Routine Order", reply_markup=generate_RO_markup())

# today
@bot.callback_query_handler(func=lambda call: True if call.data == "Today" or call.data == "rback" else False)
def RO_menu(call):
    # get cluster name
    url = "http://13.229.89.122:8080/getUserCluster"
    data = {"UID": call.from_user.id}
    repsonse = requests.post(url, data).text
    clusterName = json.loads(repsonse)
    name = clusterName['clusterName']
    # get RO
    try:
        url1 = "http://13.229.89.122:8080/getRO"
        data1 = {"cluster": name}
        repsonse1 = requests.post(url1, data1).text
        roData = json.loads(repsonse1)
        date = roData['date']
        ro = roData['ro']
        string = "Today's Routine RO for " + name + "\n" + "Date: " + date + "\n" + ro
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=string, reply_markup=generate_today_RO_markup())
    except ValueError:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Either RO was not uploaded for this date or Connection problem. Please try again', reply_markup=generate_today_RO_markup())
# Yesterday
@bot.callback_query_handler(func=lambda call: True if call.data == "Yesterday" or call.data == "rback" else False)
def RO_menu(call):
    # get cluster name
    url = "http://13.229.89.122:8080/getUserCluster"
    data = {"UID": call.from_user.id}
    repsonse = requests.post(url, data).text
    clusterName = json.loads(repsonse)
    name = clusterName['clusterName']
    # get RO
    try:
        url1 = "http://13.229.89.122:8080/getRO/yesterday"
        data1 = {"cluster": name}
        repsonse1 = requests.post(url1, data1).text
        roData = json.loads(repsonse1)
        date = roData['date']
        ro = roData['ro']

        string = "Yesterday's Routine RO for " + \
            name + "\n" + "Date: " + date + "\n" + ro
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=string, reply_markup=generate_today_RO_markup())
    except ValueError:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Wrong Date or RO has not been uploaded', reply_markup=generate_today_RO_markup())
# Other days
@bot.callback_query_handler(func=lambda call: True if call.data == "Other days" else False)
def otherdays_menu(call):
    msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text="Please enter date:(ddmmyy)", reply_markup=generate_RO_Otherdays())
    bot.register_next_step_handler(call.message, custom_day)

# Hazard
@bot.callback_query_handler(func=lambda call: True if call.data == "Hazard Reporting" or call.data == "hback" else False)
def hazard_menu(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Hazard Reporting", reply_markup=generate_hazard_markup())


# Safety
@bot.callback_query_handler(func=lambda call: True if call.data == "Safety Dissemination" or call.data == "rback" else False)
def safetydissemination_menu(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Safety Dissemination", reply_markup=generate_safetyD_markup())


# back button
@bot.callback_query_handler(func=lambda call: True if call.data == "back" else False)
def back_menu(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Announcement", reply_markup=generate_mainMenu_markup())

# delete all other msg except start
@bot.message_handler(func=lambda m: True)
def delete_all(message):
    bot.delete_message(message.chat.id, message.message_id)


def generate_cluster_markup():
    item_list = []
    reponse = requests.get('http://13.229.89.122:8080/getClusterList')
    for item in reponse.json().get('clusterName'):
        item_list.append(item['clusterName'])
    markup = types.InlineKeyboardMarkup()
    for item_name in item_list:
        markup.add(types.InlineKeyboardButton(
            item_name, callback_data=item_name))
    return markup


def generate_mainMenu_markup():
    markup = types.InlineKeyboardMarkup()
    item_list = ['Singapore Count', 'Other Countries']
    for item_name in item_list:
        markup.add(types.InlineKeyboardButton(
            item_name, callback_data=item_name))
    markup.add(types.InlineKeyboardButton("BACK", callback_data="cback"))
    return markup



def generate_safetyD_markup():
    markup = types.InlineKeyboardMarkup()
    i = 0
    item_a = types.InlineKeyboardButton(
        'Report Hazard And Near Misses...', url="https://mforcexvi.github.io/random_info_display/mock_login.html")
    markup.add(item_a)
    item_list = ['Don’t leave key in vehicle...', 'Don’t drive PMD in camp...',
                 'Don’t leave belongings unattended...', 'Beware of moving vehicles...', 'Beware of Bee Hives...']
    for item_name in item_list:
        i = i + 1
        data = "A" + str(i)
        markup.add(types.InlineKeyboardButton(item_name, callback_data=data))
    markup.add(types.InlineKeyboardButton("BACK", callback_data="back"))
    return markup


def generate_TemperatureD_markup():
    markup = types.InlineKeyboardMarkup()
    item_list = ['Declare Temperature']
    for item_name in item_list:
        markup.add(types.InlineKeyboardButton(
            item_name, url='go.gov.sg/sbn-submit-temp'))
    markup.add(types.InlineKeyboardButton("BACK", callback_data="back"))
    return markup


def custom_day(message):
    global message_id_toDel
    chat_id = message.chat.id
    date = message.text
    if not date.isdigit() or len(date) != 6:
        task = bot.send_message(
            message.chat.id, 'Date format incorrect, please press back and try again')
        msg = task.wait()
        message_id_toDel = msg.message_id
        bot.delete_message(message.chat.id, message_id_toDel-1)

    else:
        try:
            global date_of_cro
            date_of_cro = date
            url = "http://13.229.89.122:8080/getUserCluster"
            data = {"UID": message.from_user.id}
            repsonse = requests.post(url, data).text
            clusterName = json.loads(repsonse)
            name = clusterName['clusterName']
            url1 = "http://13.229.89.122:8080/getRO/customDate"
            data1 = {"cluster": name, "date": date_of_cro}
            repsonse1 = requests.post(url1, data1).text
            dataRo = json.loads(repsonse1)
            task = bot.send_message(message.chat.id, 'Here is your RO' +
                                    '\n ' + 'Date: ' + dataRo['date'] + '\n' + dataRo['ro'])
            msg = task.wait()
            message_id_toDel = msg.message_id
            task = bot.delete_message(
                message.chat.id, message_id_toDel-1)
        except ValueError:
            task = bot.send_message(
                message.chat.id, "Either RO was not uploaded for this date or Connection problem. Please try again")
            msg = task.wait()
            message_id_toDel = msg.message_id
            bot.delete_message(message.chat.id, message_id_toDel-1)



bot.polling(none_stop=True)
