import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import requests
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
OWM_API_KEY = os.getenv('OWM_API_KEY')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command('start'))
async def send_welcome(message: Message):
    await message.reply("Добро пожаловать! Я бот для прогноза погоды.\nВведите /help для просмотра доступных команд.")


# Обработчик команды /help
@dp.message(Command('help'))
async def send_help(message: Message):
    await message.reply("Вы можете управлять мной, отправляя следующие команды:\n"
                        "/start - Запуск бота.\n"
                        "/help - Показать это сообщение помощи.\n"
                        "/weather [город] - Получить прогноз погоды для указанного города.")


# Обработчик команды /weather
@dp.message(Command('weather'))
async def get_weather(message: Message):
    args = message.text.split()[1:]  # Получаем аргументы команды
    if not args:
        await message.reply("Пожалуйста, укажите название города.\nПример: /weather London")
        return

    city = ' '.join(args)
    weather_data = fetch_weather(city)
    if weather_data:
        weather_message = format_weather(weather_data)
        await message.reply(weather_message, parse_mode='HTML')
    else:
        await message.reply("Не удалось получить данные о погоде. Проверьте название города и попробуйте снова.")


# Функция для получения данных о погоде с OpenWeatherMap
def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Функция для преобразования направления ветра из градусов в текстовое значение
def get_wind_direction(degree):
    directions = [
        "северный.", "северо-восточный.", "восточный.", "юго-восточный.",
        "южный.", "юго-западный.", "западный.", "северо-западный."
    ]
    idx = round(degree / 45) % 8
    return directions[idx]


# Функция для форматирования данных о погоде в красивый вид
def format_weather(data):
    city = data['name']
    country = data['sys']['country']
    temp = data['main']['temp']
    weather_description = data['weather'][0]['description']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    wind_deg = data['wind']['deg']
    wind_direction = get_wind_direction(wind_deg)

    return (f"<b>Погода в {city}, {country}:</b>\n"
            f"Температура: {temp}°C\n"
            f"Описание: {weather_description.capitalize()}\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind_speed} м/с\n"
            f"Направление ветра: {wind_direction}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
