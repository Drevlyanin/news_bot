import requests
from bs4 import BeautifulSoup
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor


# Set up your list of news sources here
sources = [
    {'name': 'BBC News', 'url': 'https://www.bbc.com/news'},
    {'name': 'The New York Times', 'url': 'https://www.nytimes.com'},
    {'name': 'The Guardian', 'url': 'https://www.theguardian.com/international'}
]

# Initialize the bot and dispatcher
bot = Bot(token='')
dp = Dispatcher(bot)

# Store news headlines for each chat
chat_data = {}

# Scrape news headlines from the specified source
async def get_news(source_url):
    news = []
    try:
        html = requests.get(source_url).text
        soup = BeautifulSoup(html, 'html.parser')
        for article in soup.find_all('h3')[:10]:
            news.append(article.text.strip())
    except:
        pass
    return news


# Define the command that the bot will respond to
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Send welcome message
    await bot.send_message(chat_id=message.chat.id, text="Welcome to the News Bot! Type /news to get started.")


@dp.message_handler(commands=['news'])
async def send_news(message: types.Message):
    # Create buttons for each news source
    buttons = []
    for source in sources:
        buttons.append(types.InlineKeyboardButton(source['name'], callback_data=source['url']))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*buttons)

    # Send message with buttons to user
    await bot.send_message(chat_id=message.chat.id, text='Select a news source:', reply_markup=keyboard)


# Handle button presses
@dp.callback_query_handler(lambda c: True)
async def handle_callback(callback_query: types.CallbackQuery):
    source_url = callback_query.data
    source_name = next((source['name'] for source in sources if source['url'] == source_url), 'Unknown')
    news = await get_news(source_url)
    chat_id = callback_query.message.chat.id

    if news:
        # Combine the headlines into a single message
        news_message = md.text(f'Here are the latest news headlines from {source_name}:\n\n')
        for i, headline in enumerate(news, start=1):
            news_message += md.text(f'{i}. {headline}\n\n')

        # Erase previous headlines if they exist for this chat
        if chat_id in chat_data:
            previous_message_id = chat_data[chat_id]
            await bot.delete_message(chat_id=chat_id, message_id=previous_message_id)

        # Send the new message to the user and save the message ID for later
        message = await bot.send_message(chat_id=callback_query.message.chat.id, text=news_message, parse_mode=ParseMode.MARKDOWN)
        chat_data[chat_id] = message.message_id
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=f'Sorry, there was an error getting the latest news from {source_name}.')


if __name__ == '__main__':
    # Start the bot
    executor.start_polling(dp, skip_updates=True)

