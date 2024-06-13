import telebot
from telebot import custom_filters
import psutil
import os
import ping3
import ipaddress
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot('')

class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key='is_admin'
    @staticmethod
    def check(message: telebot.types.Message):
        return bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator']
bot.add_custom_filter(IsAdmin())

@bot.message_handler(commands=["start"])
def wakeup(welcome_message):
    bot.send_message(welcome_message.chat.id, """Escolha uma funcionalidade escrevendo:
/ping_to (ip que você deseja acessar.)
/reboot
/sistema
""")

@bot.message_handler(chat_id=[],commands=['ping_to'])
def ping(user_answer):

    input = telebot.util.extract_arguments(user_answer.text)

    try:
        ipaddress.ip_address(input)

        delay = ping3.ping(input)

        if delay is not None or delay == False:
            bot.reply_to(user_answer, f"O ip {input} está acessível, com o delay: {(delay):.3f}ms!!!")
        else:
            bot.reply_to(user_answer, f"O ip {input} não está acessível!!!")
    except:
            bot.reply_to(user_answer, f"O ip enviado não é valido para testes!!!")

@bot.message_handler(is_admin=True,chat_id=[],commands=['reboot'])
def buttons(buttons_reboot):
    keyboard_reboot = telebot.types.InlineKeyboardMarkup()
    key1 = telebot.types.InlineKeyboardButton(text='Sim', callback_data='reboot_sim')
    key2 = telebot.types.InlineKeyboardButton(text='Não', callback_data='reboot_não')
    keyboard_reboot.add(key1, key2)
    bot.send_message(buttons_reboot.chat.id,'Você quer mesmo reiniciar seu servidor?',reply_markup=keyboard_reboot)

@bot.message_handler(chat_id=[],commands=['sistema'])
def buttons(buttons_system):
    keyboard_system = telebot.types.InlineKeyboardMarkup()
    key3 = telebot.types.InlineKeyboardButton(text='Cpu', callback_data='sistema_cpu')
    key4 = telebot.types.InlineKeyboardButton(text='Disco', callback_data='sistema_memoria')
    key5 = telebot.types.InlineKeyboardButton(text='Memoria RAM', callback_data='sistema_memoria_ram')
    keyboard_system.add(key3, key4, key5)
    bot.send_message(buttons_system.chat.id, 'Escolha uma opção!', reply_markup=keyboard_system)

@bot.callback_query_handler(func=lambda callback_query:callback_query.data.startswith('reboot'))
def call_reboot(reboot):
    bot.delete_message(reboot.message.chat.id, reboot.message.id)
    if reboot.data == 'reboot_sim':
        reboot = os.system('reboot now')
    elif reboot.data == 'reboot_não':
        bot.send_message(reboot.message.chat.id, 'Seu servidor não será reiniciado!!!')

@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith('sistema'))
def call_system(system):
    if system.data == 'sistema_cpu':
        cpu1 = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent()
        bot.send_message(system.message.chat.id, f"Uso da CPU: {cpu_percent}%\nFrequência total: {cpu1.current}Mhz\nFrequência minima : {cpu1.min}Mhz\nFrequência máxima : {cpu1.max}Mhz")
    elif system.data == 'sistema_memoria':
        disk_usage = psutil.disk_usage('/')
        bot.send_message(system.message.chat.id, f"Uso de disco: {disk_usage.percent}%\nQuantidade de usada: {bytes(disk_usage.used)}\nQuantidade livre do disco: {bytes(disk_usage.free)}\nCapacidade total do disco: {bytes(disk_usage.total)}")
    elif system.data == 'sistema_memoria_ram':
        memory = psutil.virtual_memory()
        bot.send_message(system.message.chat.id, f"Uso de memória RAM: {memory.percent}%\nQuantidade de memoria RAM livre: {bytes(memory.free)}\nTotal de memoria RAM: {bytes(memory.total)}")
def bytes(n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % n

scheduler = BackgroundScheduler()
def warning():
    chat_id = '' 
    memoria = psutil.virtual_memory().percent
    if memoria >= 80:
        bot.send_message(chat_id, f'Sua memória ram está sendo usada em {memoria}%!')
scheduler.add_job(warning, 'interval', seconds=60) 
scheduler.start()

@bot.message_handler(commands=['ping_to','reboot','sistema'])
def not_admin(message):
    bot.send_message(message.chat.id, "Você não pode usar este comando.")

bot.add_custom_filter(custom_filters.ChatFilter())

bot.polling()
