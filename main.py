# A Starboard bot for Discord

# Import dependencies
import discord # needed for controlling access to discord
import json # needed for parsing config file

class starboatOptions(): # build custom options class
    def __init__(self, configPath): # define init behavior
        config = json.load(open(configPath)) # load config file as json object
        archiveEmote = config["archiveEmote"] # store config emote in variable
        archiveEmote = discord.PartialEmoji.from_str(archiveEmote) # transform emoji into PartialEmoji from discord class
        
        self.token = config["token"] # store token in object
        self.emote = archiveEmote # store emote in object
        self.channel = config["archiveChannel"] # store starboard channel in object
        
        print(f"Initialized starboat options using {configPath}") # print completeion of init to console

class starboatClient(discord.Client): # build custom client class
    async def on_ready(self): # define listener behavior for bot ready notifications
        print(f'Logged on as {self.user}!') # log bot readiness to console

    async def on_message(self, message): # define listener behavior for new messages
        print(f'Message from {message.author}: {message.content}') # log message to console -- TESTING

    async def on_raw_reaction_add(self, payload): # define listener behavior for new reaction event (need raw method to capture all reactions, not just cached messages)
        print(f'Message reacted: {payload.message_id}, emoji: {payload.emoji}.') # print message id and reaction emoji to console -- TESTING
        if (options.emote == payload.emoji): # check for equality between the emoji defined in the config and the message's emoji
            print("Archival Candidate") # print message status as candidate -- INDEV


intents = discord.Intents.default() # load intents class
intents.message_content = True # ensure nessecary intents

options = starboatOptions("./configFile") # define options
client = starboatClient(intents=intents) # define client
client.run(options.token) # run client
