import re
import json
import datetime
import threading # для отложенных сообщений
from multiprocessing import Process
from time import sleep

# import sqlite3 as sqlite
from telebot import TeleBot, types
from peewee import *

from config import *
import strings as s # все строки хранятся здесь
from models import User, Message

bot = TeleBot(token)

sid = lambda m: m.chat.id 
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id


@bot.message_handler(commands = ['ping'])
def ping(m):
	bot.send_message(uid(m), "I'm alive")


@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)
	Message.create_table(fail_silently = True)

@bot.message_handler(commands = ['za_schekoi'])
def za_schekoi(m):
	u = User.cog(m)
	bot.send_message(sid(m), s.balance.format(u.balance), reply_to_message_id = m.message_id)


@bot.message_handler(content_types = ['text'])
def reply(m):
	# print(m)
	u = User.cog(m)
	if Message.mine(m):
		pass



class Watcher:
	def __call__(self):
		while True:
			now = datetime.datetime.now()
			now = now.replace(microsecond = 0)
			# print(now)
			# try:
			# 	for user in User.select():
			# 		pass
			# except:
				# pass
			sleep(1)





if __name__ == '__main__':
	watcher = Watcher()
	w = Process(target = watcher)
	bot.polling(none_stop=True)
	# w.start()
	# while True:
	# 	try:
	# 		bot.polling(none_stop=True)
	# 	except:
	# 		sleep(3)
