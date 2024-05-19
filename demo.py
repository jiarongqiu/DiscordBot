
import discord
from dotenv import load_dotenv
load_dotenv()
TOEKN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message.content,type(message.content),len(message.content),message.content == 'hello')

    await message.channel.send('Hello!')    
print("Running...")
client.run(TOKEN)