import json
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Твой токен бота
TOKEN = '7722288298:AAGbqQX-3ZT12kLKjtoMT-9-ome4P2ie0Qo'

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Папка для хранения файлов пользователей
DATA_FOLDER = "users_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Клавиатура с командами
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Баланс"), KeyboardButton(text="📜 История")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот для учета финансов.\n\n"
        "Добавить доход: /dohod 1000\n"
        "Добавить расход: /rashod 500\n"
        "Посмотреть баланс: 📊 Баланс\n"
        "История операций: 📜 История",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

def get_user_file(user_id):
    """ Возвращает путь к JSON-файлу пользователя """
    return os.path.join(DATA_FOLDER, f"{user_id}.json")

def load_transactions(user_id):
    """ Загружает список транзакций пользователя """
    file_path = get_user_file(user_id)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_transactions(user_id, transactions):
    """ Сохраняет список транзакций пользователя """
    file_path = get_user_file(user_id)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(transactions, file, indent=4)

@dp.message(Command("dohod"))
async def add_income(message: types.Message):
    await process_transaction(message, is_income=True)

@dp.message(Command("rashod"))
async def add_expense(message: types.Message):
    await process_transaction(message, is_income=False)

async def process_transaction(message: types.Message, is_income: bool):
    """ Универсальная функция для добавления доходов и расходов """
    try:
        amount = float(message.text.split()[1])  # Получаем сумму из команды
        if amount <= 0:
            raise ValueError

        user_id = message.from_user.id
        transactions = load_transactions(user_id)
        transactions.append(amount if is_income else -amount)
        save_transactions(user_id, transactions)

        operation = "Доход" if is_income else "Расход"
        await message.answer(f"✅ {operation} {amount} добавлен!")
    except (IndexError, ValueError):
        await message.answer("❌ Ошибка! Используйте формат: /dohod 1000 или /rashod 500", parse_mode="Markdown")

@dp.message(lambda message: message.text == "📊 Баланс")
async def show_balance(message: types.Message):
    user_id = message.from_user.id
    transactions = load_transactions(user_id)
    balance = sum(transactions)

    await message.answer(f"💰 Ваш баланс: {balance}")

@dp.message(lambda message: message.text == "📜 История")
async def show_history(message: types.Message):
    user_id = message.from_user.id
    transactions = load_transactions(user_id)

    if not transactions:
        await message.answer("📜 История пуста.")
        return

    history_text = "📜 Последние 5 операций:\n" + "\n".join(
        [f"{'➕' if amount > 0 else '➖'} {abs(amount)}" for amount in transactions[-5:]]
    )

    await message.answer(history_text)

async def main():
    print("Бот запущен и ожидает команды...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    dp.run_polling(bot)
