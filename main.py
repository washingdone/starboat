# A Starboard bot for Discord

# Import dependencies
import disnake # needed for controlling access to discord
from disnake.ext import commands # needed for controlling slash commands
import json # needed for parsing config file

class starboatOptions(): # build custom options class
    def __init__(self, configPath): # define init behavior
        config = json.load(open(configPath)) # load config file as json object
        archiveEmote = config["archiveEmote"] # store archive emote in variable
        archiveEmote = disnake.PartialEmoji.from_str(archiveEmote) # transform emoji into PartialEmoji from discord class
        
        confirmEmote = config["confirmEmote"] # store confirmation emote in variable
        confirmEmote = disnake.PartialEmoji.from_str(confirmEmote) # transform emoji into PartialEmoji from discord class
        
        self.token = config["token"] # store token in object
        self.arcEmote = archiveEmote # store archive emote in object
        self.confEmote = confirmEmote # store confirmation emote in object
        self.channel = config["archiveChannel"] # store archive channel id in object to be transformed later
        self.minReacts = config["minReacts"]
        
        print(f"Initialized starboat options using {configPath}") # print completeion of init to console

class starboatClient(disnake.Client): # build custom client class
    async def on_ready(self): # define listener behavior for bot ready notifications
        options.channel = await client.fetch_channel(options.channel) # fetch Channel object from client and store in options object
        print(f'Logged on as {self.user}!') # log bot readiness to console

    async def on_message(self, message): # define listener behavior for new messages
        print(f'Message from {message.author}: {message.content}') # log message to console -- TESTING

    async def on_raw_reaction_add(self, payload): # define listener behavior for new reaction event (need raw method to capture all reactions, not just cached messages)
        if (options.arcEmote == payload.emoji): # check for equality between the emoji defined in the config and the message's emoji
            canChannel = await self.fetch_channel(payload.channel_id) # get channel of message
            canMessage = await canChannel.fetch_message(payload.message_id) # get message object
            
            reacts = canMessage.reactions # store array of reactions for loping
            ignoreMessage = False
            for react in reacts: # search raction array
                if (str(react.emoji) == str(options.confEmote)) : ignoreMessage = True # exit if message already pinned
                if (str(react.emoji) == str(options.arcEmote) and react.count != options.minReacts): ignoreMessage = True # exit if have not met reaction count

            if (ignoreMessage): return # exit if criteria not met

            arcContent = f"{canMessage.channel.mention} - {canMessage.created_at.date()} - {canMessage.author.mention}\n" # build archive message (split for clarity)
            arcContent += f"{canMessage.content}\n"
            arcContent += f"{canMessage.jump_url}"
            await options.channel.send(arcContent) # send message to archive channel
            await canMessage.add_reaction(options.confEmote) # react to message confirming addition to archive


intents = disnake.Intents.default() # load intents class
intents.message_content = True # ensure nessecary intents

client = starboatClient(intents=intents) # define client
options = starboatOptions("./configFile") # define options
bot = commands.InteractionBot() # register commands

@bot.slash_command(name="upload_screenshot", description="Add file to message")
async def uploadScreenshot(interaction, message_id):
    message = await options.channel.fetch_message(message_id)
    print(message)
    await interaction.response.send_message("Done!")

bot.run(options.token) # run client

