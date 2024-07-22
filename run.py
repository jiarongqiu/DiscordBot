import os
import discord
import logging
import logging.handlers
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
from api import api

bot = discord.Bot()
print("Bot is running")
logging.info("Bot is running")
@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.command(name='ask',description="ask question to Filecoin TLDR AI Assistant")
async def ask(ctx,inputs: discord.Option(str)):
    await ctx.defer()  # 延迟响应，告诉 Discord 正在处理
    print(f"QJR ctx: {ctx} inputs: {inputs}")
    logging.info(f"QJR ctx: {ctx} inputs: {inputs}")
    response = api.get_answer(inputs)
    answer = f"**Q:** {inputs}\n**A:** "
    for text in response:
        answer += text.decode('utf-8')
    answer += "\n\n **TLDR Bot is experimental and still learning. Please bear with us as we improve its accuracy*\n"
    await ctx.followup.send(answer)  # 使用 followup 发送最终消息

@bot.command(name='add',description="add urls to Filecoin TLDR AI Assistant")
async def add(ctx,url: discord.Option(str)):
    await ctx.defer()  # 延迟响应，告诉用户正在处理
    print(f"QJR command add ctx: {ctx} inputs: {url}")
    logging.info(f"QJR command add ctx: {ctx} inputs: {url}")
    await ctx.followup.send(f"Start crawling {url} in background. Please wait for a while.")
    api.add_docs(url)


bot.run(token)