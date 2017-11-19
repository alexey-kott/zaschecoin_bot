import re
import json
import datetime
import threading # для отложенных сообщений
from multiprocessing import Process
from time import sleep

import sqlite3 as sqlite
from telebot import TeleBot, types
from peewee import *

from config import *
import strings as s # все строки хранятся здесь

bot = TeleBot(token)

sid = lambda m: m.chat.id # лямбды для определения адреса ответа
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id

db = SqliteDatabase('db.sqlite3')

class BaseModel(Model):
	class Meta:
		database = db

class User(BaseModel):
	user_id = IntegerField(primary_key = True)
	username = TextField(null = True)
	first_name = TextField()
	last_name = TextField(null = True)
	balance = IntegerField(default = 3)
	
	def cog(m):
		username = m.from_user.username
		first_name = m.from_user.first_name
		last_name = m.from_user.last_name
		try:
			with db.atomic():
				u = User.create(user_id = uid(m), username = username, first_name = first_name, last_name = last_name)
				bot.send_message(sid(m), s.greeting, reply_to_message_id = m.message_id)
				return u
		except Exception as e:
			return User.select().where(User.user_id == uid(m)).get()


@bot.message_handler(commands = ['ping'])
def ping(m):
	bot.send_message(uid(m), "I'm alive")


@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)

@bot.message_handler(commands = ['za_schekoi'])
def za_schekoi(m):
	u = User.cog(m)
	# if u.username == "squizduos":
	# 	bot.send_message(sid(m), "У тебя ОГРОМНЫЙ ХУИЩЕ за щекой", reply_to_message_id = m.message_id)	
	# else:
	bot.send_message(sid(m), s.balance.format(u.balance), reply_to_message_id = m.message_id)


@bot.message_handler(content_types = ['text'])
def reply(m):
	print(uid(m))
	print(m.from_user.username)
	print(m.text, end="\n\n")
	u = User.cog(m)



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
