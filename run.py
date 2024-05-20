import os
import discord
from discord.ext import commands
import logging
import logging.handlers
from dotenv import load_dotenv
from api import api
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
logging.info(f"TOKEN:{token}")

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$jarvis'):
        print(bot.user,message.content)
        inputs = message.content.split(' ')
        inputs.pop(0)
        inputs = " ".join(inputs)
        response = api.get_answer(inputs)
        answer = ""
        for text in response:
            print(text)
            answer += text.decode('utf-8')
        logging.info(f"User: {message.author} Inputs: {inputs} Answer: {answer}")
        await message.channel.send(answer)

@bot.command
async def ping(ctx, arg):
    print(bot.user,ctx,arg)
    await ctx.channel.send("command received")


bot.run(token, log_handler=None)

# Assume client refers to a discord.Client subclass...
# Suppress the default configuration since we have our own
# client.run(token, log_handler=None)
