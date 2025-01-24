# bot.py

import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.utils import executor
from config import TOKEN, APIKEY

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Функция для получения погоды из API
def get_weather(location: str):
    """
    Получение погоды по названию города или координатам (latitude,longitude).
    """
    url = f"http://api.weatherapi.com/v1/current.json?key={APIKEY}&q={location}&aqi=no"
    try:
        response = requests.get(url)
        data = response.json()

        # Проверяем успешность ответа
        if "current" in data:
            temperature = data["current"]["temp_c"]
            location_name = data["location"]["name"]
            return f"Температура в {location_name}: {temperature}°C"
        else:
            return "Не удалось найти данные о погоде."
    except Exception as e:
        logging.error(f"Ошибка при запросе к API: {e}")
        return "Ошибка при получении данных о погоде."

# Создаём клавиатуру с кнопкой "Погода за окном"
weather_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
weather_button = KeyboardButton("Погода за окном", request_location=True)
weather_keyboard.add(weather_button)

@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    await message.reply(
        "Привет! Введите название города на английском языке, чтобы узнать температуру. "
        "Или нажмите кнопку ниже, чтобы узнать погоду по вашему местоположению.",
        reply_markup=weather_keyboard,
    )

@dp.message_handler(commands=["help"])
async def help_command(message: Message):
    await message.reply(
        "Введите название города на английском языке, и я покажу температуру воздуха. "
        "Или нажмите кнопку 'Погода за окном', чтобы отправить своё местоположение."
    )

# Обработчик текстовых сообщений (поиск погоды по названию города)
@dp.message_handler()
async def send_weather(message: Message):
    city = message.text.strip()  # Получаем текст сообщения (название города)
    weather_info = get_weather(city)  # Получаем данные о погоде
    await message.reply(weather_info)  # Отправляем ответ пользователю

# Обработчик местоположения (поиск погоды по координатам)
@dp.message_handler(content_types=ContentType.LOCATION)
async def send_weather_by_location(message: Message):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        location = f"{latitude},{longitude}"  # Формируем строку с координатами
        weather_info = get_weather(location)  # Получаем данные о погоде по координатам
        await message.reply(weather_info)  # Отправляем ответ пользователю
    else:
        await message.reply("Не удалось определить местоположение.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)