import re
import json
import datetime
import threading # для отложенных сообщений
from multiprocessing import Process
from time import sleep

import sqlite3 as sqlite
from telebot import TeleBot, types


from config import *
import strings as s # все строки хранятся здесь
from models import User, System, Message

bot = TeleBot(token)

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
	if u.balance == 0:
		bot.send_message(sid(m), "Нищеброд просит за щеку", reply_to_message_id = m.message_id)



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
	# bot.polling(none_stop=True)
	w.start()
	while True:
		try:
			bot.polling(none_stop=True)
		except:
			sleep(3)
