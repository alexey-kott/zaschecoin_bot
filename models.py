import re
import hashlib
from random import randint

from peewee import *
from telebot import TeleBot

from config import *
import strings as s # все строки хранятся здесь
from functions import *

bot = TeleBot(token)

sid = lambda m: m.chat.id 
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
			u = User.select().where(User.user_id == uid(m)).get()
			u.username = m.from_user.username
			u.save()
			return u

	def mine(self, m):
		reward = System.calc_reward(m.text)
		if reward:
			bot.send_message(sid(m), "Тебе за щеку прилетело {} защекоинов".format(reward), reply_to_message_id = m.message_id)
			self.balance += reward
			self.save()
		return 0

	def transact(self, m):
		recipient_name = re.findall(r'(?<=\s@)\w+', m.text)
		if not recipient_name:
			bot.send_message(sid(m), "@{} просит за щеку".format(self.username), reply_to_message_id = m.message_id)
			return False

		try:
			recipient = User.get(User.username == recipient_name)
		except:
			bot.send_message(sid(m), s.user_not_found, reply_to_message_id = m.message_id)
			return False

		if recipient.user_id == self.user_id:
			bot.send_message(sid(m), "Аутофелляцией можешь заняться в другом чате", reply_to_message_id = m.message_id)
			return False

		try:
			amount = int(re.findall(r'\s-?\d+', m.text)[0])
			if amount <= 0:
				return False
		except:
			amount = 0
		if self.is_nischebrod(amount): # усли перевести хочет больше, чем у него есть
			bot.send_message(sid(m), "Недостаточно защекоинов. Флуд может тебе накинуть!", reply_to_message_id = m.message_id)
		elif self.is_nischebrod():
			bot.send_message(sid(m), "Отсыпьте за щеку этому нищеброду, у него ничего нет", reply_to_message_id = m.message_id)
		else:
			if amount:
				recipient.balance += amount
				recipient.save()
				self.balance -= amount
				self.save()
				bot.send_message(sid(m), "@{} напихал за щеку @{} {} ZSH".format(self.username, recipient.username, amount), reply_to_message_id = m.message_id)
			else:
				recipient.balance += self.balance
				recipient.save()
				self.balance = 0
				self.save()
				bot.send_message(sid(m), "@{} напихал за щеку @{} все свои защекоины и остался нищебродом. Флуд, напихай ему за щеку!".format(self.username, recipient.username, amount), reply_to_message_id = m.message_id)


	def is_nischebrod(self, amount = None):
		if amount:
			if self.balance >= amount:
				return False
		else:
			if self.balance > 0:
				return False
		return True





class System(BaseModel):
	id 			 = IntegerField(primary_key = True, constraints=[Check('id = 1')])
	border 		 = TextField() # значения слишком большие для IntegerField, храним как строки
	rng			 = TextField()
	reward 		 = FloatField(default = 100)
	reward_count = IntegerField(default = 0)
	active_users = IntegerField(default = 0)

	def init():
		System.create(
			id = 1,
			border = str(randint(0, 10**48)),
			rng = str(10**47)
			)


	@staticmethod
	def calc_reward(m):
		msg_hash = System.calc_hash(m)
		msgs = Message.select().where(Message.msg_hash == msg_hash).count()
		if msgs > 1:
			return 0

		system = System.get(id = 1)
		l_border = int(system.border) 
		r_border = l_border + int(system.rng)
		if msg_hash > l_border and msg_hash < r_border:
			system.reward_count += 1
			system.save()
			return system.reward
		return 0

	@staticmethod
	def calc_hash(m):
		text = m.encode("utf-8")
		msg_hash = hashlib.sha1()
		msg_hash.update(text)
		int_hash = int(msg_hash.hexdigest(), 16) # хеш текста сообщения в целочисленном представлении
		return int_hash




class Message(BaseModel):
	msg_id 		= IntegerField(primary_key = True)
	chat_id 	= IntegerField()
	sender		= IntegerField()
	text 		= TextField()
	msg_hash    = TextField(index=True) # sha1 хеш в целочисленном представлении
	dt 			= BigIntegerField() # по Гринвичу

	def add(m):
		Message.create(
			msg_id = m.message_id,
			chat_id = sid(m),
			sender = uid(m),
			text = m.text,
			msg_hash = System.calc_hash(m.text),
			dt = m.date
			)


