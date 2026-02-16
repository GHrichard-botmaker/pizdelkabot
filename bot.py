import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import openai  # Для DeepSeek используем OpenAI-совместимый клиент

# Настройки
BOT_TOKEN = "8450095162:AAELM9tK0GYYsJUHgV8r3LmdAw9WMucPMWQ"
DEEPSEEK_API_KEY = "sk-323062d009a24624b49d0edbd58be612"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"  # Или другой endpoint
RESPONSE_CHANCE = 0.1  # 10% шанс ответа на любое сообщение

# Настройка DeepSeek клиента
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_URL
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Приветственное сообщение при добавлении в группу
@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.chat.type != "private":
        await message.reply(
            "👋 Привет! Я AI-бот на базе DeepSeek.\n"
            f"У меня {RESPONSE_CHANCE*100}% шанс ответить на любое сообщение, "
            "или просто отметь меня @username_bot"
        )

# Обработка упоминаний и случайных сообщений
@dp.message()
async def handle_message(message: Message):
    # Проверяем, не от бота ли сообщение
    if message.from_user.is_bot:
        return
    
    # Проверяем, упомянули ли бота
    bot_mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention_text = message.text[entity.offset:entity.offset+entity.length]
                if mention_text == f"@{bot.id}":
                    bot_mentioned = True
                    break
    
    # Случайный шанс или упоминание
    should_respond = bot_mentioned or random.random() < RESPONSE_CHANCE
    
    if not should_respond:
        return
    
    try:
        # Отправляем "печатает..." для реализма
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Формируем контекст
        prompt = f"Ответь на сообщение от лица AI-ассистента: {message.text}"
        
        # Запрос к DeepSeek
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты дружелюбный AI-ассистент в Telegram группе. Отвечай кратко и по делу."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Отправляем ответ, упоминая пользователя если нужно
        if bot_mentioned:
            await message.reply(ai_response)
        else:
            await message.answer(ai_response)
            
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("😵 Извините, я временно недоступен...")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
