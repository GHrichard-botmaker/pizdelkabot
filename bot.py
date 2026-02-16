import logging
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import Message
from aiogram.utils import executor
import openai

# Настройки
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

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply(f"👋 Я AI-бот! Отвечаю с шансом {RESPONSE_CHANCE*100}%")

@dp.message_handler()
async def handle_message(message: types.Message):
    if message.from_user.is_bot:
        return
    
    # Проверяем упоминание или случайный шанс
    bot_mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention_text = message.text[entity.offset:entity.offset+entity.length]
                if mention_text == f"@{bot.username}":
                    bot_mentioned = True
                    break
    
    if not (bot_mentioned or random.random() < RESPONSE_CHANCE):
        return
    
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": message.text}],
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        await message.reply(ai_response)
            
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("😵 Ошибка...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
