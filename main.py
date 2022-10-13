# This example requires the 'message_content' intent.

import discord
import json

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

    async def on_raw_reaction_add(self, payload):
        print(f'Message reacted: {payload.message_id}, emoji: {payload.emoji}.')
        print(f'\'{archiveEmote}\'vs\'{payload.emoji}\'')
        print(archiveEmote == payload.emoji)
        if (payload.emoji == archiveEmote):
            print("Archival Candidate")


intents = discord.Intents.default()
intents.message_content = True

config = json.load(open("configFile"))
archiveEmote = config["archiveEmote"]
archiveEmote = discord.PartialEmoji.from_str(archiveEmote)

client = MyClient(intents=intents)
client.run(config["token"])
