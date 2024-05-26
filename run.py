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
logger.setLevel(logging.INFO)
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

intents = discord.Intents.default()
# intents.message_content = True
# bot = commands.Bot(command_prefix='/', intents=intents)
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.slash_command(description="Jarvis AI Assitant")
async def your_command(ctx, *, inputs):
    print(f"QJR ctx: {ctx} ctx.message.author: {ctx.message.author} Inputs: {inputs}") 
    print(f"User: {ctx.message.author} Inputs: {inputs}")
    response = api.get_answer(inputs)
    answer = ""
    for text in response:
        print(text)
        answer += text.decode('utf-8')
    logging.info(f"User: {ctx.message.author} Inputs: {inputs} Answer: {answer}")
    await ctx.send(answer)

@bot.slash_command(description="打招呼")
async def hello(ctx):
    await ctx.respond("Hello, world!")
# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     if message.content.startswith('!jarvis'):
#         print(bot.user,message.content)
#         inputs = message.content.split(' ')
#         inputs.pop(0)
#         inputs = " ".join(inputs)
#         response = api.get_answer(inputs)
#         answer = ""
#         for text in response:
#             print(text)
#             answer += text.decode('utf-8')
#         logging.info(f"User: {message.author} Inputs: {inputs} Answer: {answer}")
#         await message.channel.send(answer)

# @bot.command()
# async def jarvis(ctx, *, inputs):
#     print(f"User: {ctx.message.author} Inputs: {inputs}")
#     response = api.get_answer(inputs)
#     answer = ""
#     for text in response:
#         print(text)
#         answer += text.decode('utf-8')
#     logging.info(f"User: {ctx.message.author} Inputs: {inputs} Answer: {answer}")
#     await ctx.send(answer)

bot.run(token, log_handler=None)