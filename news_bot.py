import requests
from bs4 import BeautifulSoup
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import asyncio

# Set up your list of news sources here
sources = ['https://www.bbc.com/news', 'https://www.nytimes.com', 'https://www.reuters.com']

# Initialize the bot and dispatcher
bot = Bot(token='')
dp = Dispatcher(bot)


# Scrape news headlines from the specified sources
async def get_news():
    news = []
    for source in sources:
        try:
            html = requests.get(source).text
            soup = BeautifulSoup(html, 'html.parser')
            for article in soup.find_all('h3')[:10]:
                news.append(article.text)
        except:
            pass
    return news


# Define the command that the bot will respond to
@dp.message_handler(commands=['news'])
async def send_news(message: types.Message):
    # Get the latest news headlines
    headlines = await get_news()
    if headlines:
        # Combine the headlines into a single message
        news_message = md.text('Here are the latest news headlines:\n\n')
        for i, headline in enumerate(headlines, start=1):
            news_message += md.text(f'{i}. {headline}\n\n')
        # Send the message to the user
        await bot.send_message(chat_id=message.chat.id, text=news_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id=message.chat.id, text='Sorry, there was an error getting the latest news.')


if __name__ == '__main__':
    # Start the bot
    executor.start_polling(dp, skip_updates=True)
