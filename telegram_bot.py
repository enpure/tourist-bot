from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
import requests

TOKEN = '6430226616:AAFlF0a15LfDulVki2a9k99s-VAb95x81Ng'
WEATHER_API_KEY = '417b46af81a0b8cc0b0f4880284ca7ee'
CURRENCY_API_KEY = '8dae2136fa422f927edcbcaba42af464'
NEWS_API_KEY = '7ce6a58e729344c3b381cc2463b9516e'

# Определение состояний для ConversationHandler
WEATHER, CURRENCY, NEWS = range(3)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Добро пожаловать в TouristCityGuide! Вы можете использовать команды /weather, /currency и /news.')

def ask_for_city(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Пожалуйста, укажите город.')
    return WEATHER

def get_weather(update: Update, context: CallbackContext):
    город = update.message.text
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={город}&appid={WEATHER_API_KEY}&lang=ru')
    data = response.json()

    if data['cod'] == 200:
        температура = data['main']['temp'] - 273.15  # Перевод из Кельвина в Цельсий
        описание = data['weather'][0]['description']
        update.message.reply_text(f'Погода в {город}: {описание}, {температура:.2f}°C')
    else:
        update.message.reply_text('Не удалось получить погоду для этого города.')
    return ConversationHandler.END

def ask_for_currency(update: Update, context: CallbackContext):
    update.message.reply_text('Пожалуйста, введите интересующую валюту.')
    return CURRENCY

def get_currency(update: Update, context: CallbackContext):
    страна = update.message.text.upper()
    response = requests.get(f'https://open.er-api.com/v6/latest/{страна}')
    data = response.json()

    if 'rates' in data:
        курс = data['rates']['THB']  # Пример для тайского бата
        update.message.reply_text(f'Текущий курс валюты в {страна} относительно THB: {курс}')
    else:
        update.message.reply_text('Не удалось получить курс валюты для этой страны.')
    return ConversationHandler.END

def ask_for_news(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Пожалуйста, введите двухзначный код страны английскими буквами.')
    return NEWS

def get_news(update: Update, context: CallbackContext):
    страна = update.message.text.lower()
    response = requests.get(f'https://newsapi.org/v2/top-headlines?country={страна}&apiKey={NEWS_API_KEY}')
    data = response.json()

    if data['status'] == 'ok' and data['articles']:
        заголовки = [статья['title'] for статья in data['articles'][:5]]
        сообщение_с_новостями = '\n'.join(заголовки)
        update.message.reply_text(сообщение_с_новостями)
    else:
        update.message.reply_text('Не удалось получить новости для этой страны.')
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    # Добавляем обработчики для каждой команды
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('weather', ask_for_city)],
        states={
            WEATHER: [MessageHandler(Filters.text & ~Filters.command, get_weather)]
        },
        fallbacks=[]
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('currency', ask_for_currency)],
        states={
            CURRENCY: [MessageHandler(Filters.text & ~Filters.command, get_currency)]
        },
        fallbacks=[]
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('news', ask_for_news)],
        states={
            NEWS: [MessageHandler(Filters.text & ~Filters.command, get_news)]
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
