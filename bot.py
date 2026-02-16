import logging
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import Message
from aiogram.utils import executor
import openai

# Настройки из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
RESPONSE_CHANCE = float(os.getenv("RESPONSE_CHANCE", "0.1"))

# Настройка DeepSeek
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Обработчик команды start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.chat.type != 'private':
        await message.reply(
            f"👋 Привет! Я AI-бот на базе DeepSeek.\n"
            f"У меня {RESPONSE_CHANCE*100}% шанс ответить на любое сообщение"
        )

# Обработчик всех сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return
    
    # Проверяем упоминание бота
    bot_mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention_text = message.text[entity.offset:entity.offset+entity.length]
                if mention_text == f"@{bot.username}":
                    bot_mentioned = True
                    break
    
    # Случайный шанс или упоминание
    if not (bot_mentioned or random.random() < RESPONSE_CHANCE):
        return
    
    try:
        # Отправляем статус "печатает"
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Получаем ответ от DeepSeek
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты дружелюбный AI-ассистент в Telegram группе. Отвечай кратко и по делу."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Отправляем ответ
        if bot_mentioned:
            await message.reply(ai_response)
        else:
            await message.answer(ai_response)
            
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("😵 Извините, ошибка...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
