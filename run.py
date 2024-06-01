import os
import discord
import logging
import logging.handlers
from dotenv import load_dotenv
from api import api
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
logging.info(f"TOKEN:{token}")

bot = discord.Bot()

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.command(name='ask',description="ask question to Filecoin TLDR AI Assitant")
async def ask(ctx,inputs: discord.Option(str)):
    await ctx.defer()  # 延迟响应，告诉 Discord 正在处理
    print(f"QJR ctx: {ctx} inputs: {inputs}")
    response = api.get_answer(inputs)
    answer = f"*TLDR Bot is experimental and still learning. Please bear with us as we improve its accuracy*\n**Q:** {inputs}\n**A:** "
    for text in response:
        answer += text.decode('utf-8')
    # answer += "\n\n *Please note the TLDR bot is still learning so we advise doing your own research,  we are constantly fine-tuning it to make sure most relevant results are shown.  Thanks everyone and looking for everyone to use it more. :love_letter:*"
    await ctx.followup.send(answer)  # 使用 followup 发送最终消息

# @bot.command(description="say hi")
# async def hello(ctx):
#     await ctx.respond("Hello, world!")
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

bot.run(token)