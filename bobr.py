import time
import telebot
import datetime
from telebot import types
import sqlite3
import bobr_time

def update_users():
	global users
	dbn = 'bobr_data.db'
	conn = sqlite3.connect(dbn)
	#else: print("error: don't connected to data base")
	cursor = conn.cursor()

	sqlite_users = """SELECT * FROM InPh"""
	cursor.execute(sqlite_users)
	users = cursor.fetchall()
	conn.commit()
	conn.close()
	print(users)

def update_events():
	global events, time_events
	dbn = 'bobr_data.db'
	conn = sqlite3.connect(dbn)
	#else: print("error: don't connected to data base")
	cursor = conn.cursor()
	sqlite_events = """SELECT * FROM InPh_events"""
	cursor.execute(sqlite_events)
	events = cursor.fetchall()
	sqlite_events = """SELECT time FROM InPh_events"""
	cursor.execute(sqlite_events)
	time_events = cursor.fetchall()
	conn.commit()
	conn.close()
	print(events)
	print(time_events)

def send_time_message(message, timer):
	for a in events:
		if a[3] == timer:
			bot,send_message(message.chat.id, f'Напоминаю, что у вас стоит задача {a[1]}: {a[2]} на {a[3]}.')

date = datetime.datetime.today()

print("запуск БОБР-а...")

print("Проверка данных о пользователях:")
users =[]
update_users()
print("Проверка данных об эвентах:")
events = []
time_events = []
update_events()

print('Таблицы синхронизированы успешно!')
print(date.strftime('%Y-%m-%d %H:%M'))

user_reg = False;

bot = telebot.TeleBot('API')

@bot.message_handler(content_types=['text'])
@bot.message_handler(content_types=['text', 'document', 'audio'])

def command_hendler(message):
	global users, user_reg

	if message.text == '/start':
		bot.reply_to(message, 'Приветики! Я - БОБР (Бот Оперативной Борьбы Русланчик)!\n\nЧтобы узнать мои команды - используй: "/info"')

	if message.text == "/register":
		new_user_name = message.from_user.first_name
		new_user_username = "@" + str(message.from_user.username)
		for a in users:
			if new_user_name in a and new_user_username in a or new_user_name in users and new_user_username in users:
				print(a)
				bot.reply_to(message, 'Эй, ' + new_user_name + ', обмануть Русланчика вздумал!?!?!?!?\n\nЯ такого не допущу! Никто не смеет обманывать бобра! Ты уже есть в команде\n\n>:(')
				print(users)
				return()
		if user_reg == False:
			dbn = 'bobr_data.db'
			conn = sqlite3.connect(dbn)
			cursor = conn.cursor()
			sqlite_users = f"""INSERT INTO InPh(users,  usernames) VALUES ('{new_user_name}', '{new_user_username}')"""
			cursor.execute(sqlite_users)
			conn.commit()
			conn.close()
			users.append(new_user_name)
			users.append("@" + str(new_user_username))
			bot.reply_to(message, 'Новый пользователь зарегистрирован!')
			bot.send_message(message.chat.id, 'Добро пожаловать в команду, ' + new_user_name + ')))')
			update_users()
			print(users)
			user_reg = True;
			return()

	if message.text == '/event':
		name = ''
		text = ''
		time =  ''
		bot.reply_to(message, 'Вижу, пришло время работы над эвентами? Ну, поему бы и нет! Как назовём его?')
		@bot.message_handler(content_types=['text'])

		def name_event(message):
			global name
			name = message.text
			bot.reply_to(message, 'Класс, теперь нужна задача, которую нужно выполнить (советую пингануть участников эвента).')
			@bot.message_handler(content_types=['text'])
			def text_event(message):
				global text
				text = message.text
				bot.reply_to(message, 'Отлично! Осталось лишь добавить время эвента! Сделай это в следующем виде: "номер_месяца-число часы:минуты"(10-26 22:22).')
				@bot.message_handler(content_types=['text'])
				def time_event(message):
					global time, name, text, events
					time = message.text
					bot.reply_to(message, f'Итак, эвент {name} запланирован на {time}, текст сообщения: {text}.')
					dbn = 'bobr_data.db'
					conn = sqlite3.connect(dbn)
					cursor = conn.cursor()
					sqlite_events = f"""INSERT INTO InPh_events(name, text, time) VALUES ('{name}', '{text}', '{time}')"""
					cursor.execute(sqlite_events)
					conn.commit()
					conn.close()
					update_events()
				bot.register_next_step_handler(message, time_event)
				x = bobr_time.time_update()
				y = bobr_time.timer()
			bot.register_next_step_handler(message, text_event)

		bot.register_next_step_handler(message, name_event)

	if message.text == '/delete_event':
		name_delete_event = ''
		bot.reply_to(message, 'Надеюсь, что ты решил удалить его потому что выполнил, а не забил, ведь так?🤔🤔🤔\n\nОкей, в любом случае мне нужно название эвента, который ты хочешь удалить. Если не посмотрел его заранее, напиши /cancel.')
		@bot.message_handler(content_types=['text'])
		def delete_event(message):
			if message.text == "/cancel":
				pass
			else:
				name_delete_event = message.text
				for a in events:
					if a[1] == name_delete_event:
						dbn = 'bobr_data.db'
						conn = sqlite3.connect(dbn)
						cursor = conn.cursor()
						sqlite_events = f"""DELETE FROM InPh_events WHERE name='{name_delete_event}'"""
						cursor.execute(sqlite_events)
						conn.commit()
						conn.close()
						update_events()
						bot.reply_to(message, f'Оки-доки, эвент {name_delete_event} удалён! (Жалко этого добряка).')
		bot.register_next_step_handler(message, delete_event)

	if message.text == '/events':
		all_events = ''
		for a in events:
			all_events += f'"{a[1]}", дата: {a[3]}, задача: {a[2]};\n'
		bot.reply_to(message, f'''Хм, дайте-ка глянуть, в моей библиотеке должно что-то пылиться🤓🤓🤓
			Итак, по планам у нас:

			{all_events}
			Как-то так)''')

	if message.text == '/info':
		bot.reply_to(message,'''Вот возможности пиратского разогнанного процессора БОБР-а Русланчика😉

			/register - регистрация тебя (участника) в команде!
			/event - добавляет общий эвент)))
			/delete_event - удаляет эвент(((
			/events - выводит список всех эвентов!
			/command - выводит список всех участников команды.(не работает пока что)''')
bot.polling(none_stop=True, interval=1)