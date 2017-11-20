import hashlib

from peewee import *
from telebot import TeleBot

from config import *
import strings as s


sid = lambda m: m.chat.id 
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id

bot = TeleBot(token)
db = SqliteDatabase('db.sqlite3')

class BaseModel(Model):
	class Meta:
		database = db

class User(BaseModel):
	user_id 	= IntegerField(primary_key = True)
	username 	= TextField(null = True)
	first_name 	= TextField()
	last_name 	= TextField(null = True)
	balance 	= IntegerField(default = 3)
	
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


class Message(BaseModel):
	msg_id 		= IntegerField(primary_key = True)
	chat_id 	= IntegerField()
	sender		= IntegerField()
	text 		= TextField()
	msg_hash    = IntegerField(index=True) # sha1 хеш в целочисленном представлении
	dt 			= DateTimeField()

	# @staticmethod
	def mine(m):
		pass
	# 	text = m.text.encode("utf-8")
	# 	msg_hash = hashlib.sha1()
	# 	msg_hash.update(text)
	# 	int_hash = int(msg_hash.hexdigest(), 16) # хеш текста сообщения в целочисленном представлении
	# 	msg_id = m.message_id
	# 	msg = Message.

