import re
import json
from datetime import time, datetime
import threading # для отложенных сообщений
from multiprocessing import Process
from time import sleep
import random
import ssl

import sqlite3 as sqlite
from aiohttp import web
from telebot import TeleBot, types


from config import *
import strings as s # все строки хранятся здесь
from models import User, System, Message
from functions import *

bot = TeleBot(API_TOKEN)

sid = lambda m: m.chat.id # лямбды для определения адреса ответа
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id




@bot.message_handler(commands = ['ping'])
def ping(m):
	bot.send_message(uid(m), "I'm alive")


@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)
	Message.create_table(fail_silently = True)
	System.create_table(fail_silently = True)
	System.init()


@bot.message_handler(commands = ['za_schekoi'])
def za_schekoi(m):
	u = User.cog(m)
	try:
		target_username = re.findall(r'(?<=\s@)\w+', m.text)[0]
		target = User.get(User.username == target_username)
		bot.send_message(sid(m), s.target_balance.format(target.username, target.balance), reply_to_message_id = m.message_id)
	except:
		bot.send_message(sid(m), s.balance.format(u.balance), reply_to_message_id = m.message_id)


@bot.message_handler(commands = ['za_scheku'])
def za_scheku(m):
	u = User.cog(m)
	u.transact(m)



@bot.message_handler(content_types = ['text'])
def reply(m):
	# print(uid(m))
	# print(m.from_user.username)
	# print(m.text, end="\n\n")
	Message.add(m)
	u = User.cog(m)
	u.mine(m)
	if u.balance == 0 and random.random() < 0.1:
		bot.send_message(sid(m), "Нищеброд просит за щеку", reply_to_message_id = m.message_id)



class Watcher:
	def __call__(self):
		midnight = time(hour = 0, minute = 0, second = 0, microsecond = 0)
		while True:
			cur_time = datetime.time(datetime.now())
			cur_time = cur_time.replace(second = 0, microsecond = 0)
			if cur_time == midnight:
				backup_db()
			sleep(1)





if __name__ == '__main__':
	watcher = Watcher()
	w = Process(target = watcher)
	w.start()

	# Remove webhook, it fails sometimes the set if there is a previous webhook
	bot.remove_webhook()


	if LAUNCH_MODE == "DEV":
		bot.polling(none_stop=True)
	elif LAUNCH_MODE == "PROD":
		app = web.Application()
		app.router.add_post('/{token}/', handle)

		
		# Set webhook
		bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
		                certificate=open(WEBHOOK_SSL_CERT, 'r'))

		# Build ssl context
		context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
		context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

		# Start aiohttp server
		web.run_app(
		    app,
		    host=WEBHOOK_LISTEN,
		    port=WEBHOOK_PORT,
		    ssl_context=context,
		)
