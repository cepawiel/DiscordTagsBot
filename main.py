import discord
import sys
import traceback
from collections import defaultdict
from io import StringIO

CHANNEL_NAME = "tags"

# https://discord.com/api/oauth2/authorize?client_id=765238859407294475&permissions=268512336&scope=bot

class TagBot(discord.Client):

    def __init__(self):
        super().__init__()


    async def on_connect(self):
        print("Connected!")

    async def on_ready(self):
        print('Logged on as', self.user)
        for chan in self.get_all_channels():
            if chan.name == CHANNEL_NAME:
                print("found tags in " + chan.guild.name)
                await self.createTagsIfNecessary(chan)
                await chan.edit(topic="!help -- tags you react to add you to it, removing react removes you")

        print("Ready!")

    async def createTagsIfNecessary(self, channel):
        print("Creating Tags")
        roles = channel.guild.roles
        member = channel.guild.get_member(self.user.id)
        bot_role = discord.utils.get(roles, name=member.name)
        
        pos = roles.index(bot_role)
        roles = roles[1:pos]

        tag_channel = await self.getTagChannel(channel.guild)
        messages = tag_channel.history(limit=100)
        if len(roles) > 0:
            role_missing = True
            for role in roles:
                async for msg in messages:
                    if msg.role_mentions[0] == role:
                        role_missing = False
                        break
                if role_missing:
                    await self.createTagMessage(role)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # if message is for this bot
        if self.isTagsChannel(message.channel):
            l = message.content.split(' ')
            command = l[0]
            args = l[1:]
            await message.delete()
            await self.onCommand(message, command, args)

    async def on_raw_reaction_add(self, payload):
        channel = self.get_channel(payload.channel_id)
        if not self.isTagsChannel(channel): return
        print("on_raw_reaction_add")
        guild = self.get_guild(payload.guild_id)
        user = await guild.fetch_member(payload.user_id)
        msg = await channel.fetch_message(payload.message_id)
        role = msg.role_mentions[0]
        if user != self.user:
            await user.add_roles(role)

    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)
        if not self.isTagsChannel(channel): return
        print("on_raw_reaction_remove")
        guild = self.get_guild(payload.guild_id)
        user = await guild.fetch_member(payload.user_id)
        msg = await channel.fetch_message(payload.message_id)
        role = msg.role_mentions[0]
        if user != self.user:
            await user.remove_roles(role)

    async def on_guild_role_create(self, role):
        if await self.getTagChannel(role.guild) == None: return
        print("on_guild_role_create")
        await self.createTagMessage(role)

    async def on_guild_role_delete(self, role):
        if await self.getTagChannel(role.guild) == None: return
        print("on_guild_role_delete")
        for channel in role.guild.text_channels:
            if channel.name == CHANNEL_NAME:
                async for msg in channel.history(limit=100):
                    if role.mention in msg.content:
                        await msg.delete()
                        return

    async def createTagMessage(self, role):
        channel = await self.getTagChannel(role.guild)
        msg = await channel.send(content=role.mention)
        await msg.add_reaction('👍')

    async def getTagChannel(self, guild):
        return discord.utils.get(guild.text_channels, name=CHANNEL_NAME)

    def isTagsChannel(self, channel):
        if channel.name == CHANNEL_NAME:
            return True
        return False

    # Input Command Switch Function
    async def onCommand(self, message, command, args):
        if command[0] != '!': return

        switch = {
            "!add":self.onAdd,
            "!color":self.onChangeColor,
            "!desc":self.onSetDescription,
            "!help":self.onWriteHelp,
            "!delete":self.onDelete,
            "!remove":self.onDelete,
            "!clear":self.onClearChannel
        }
        func = switch.get(command, lambda: "Invalid Command")
        await func(message, args)

    async def onAdd(self, message, args):
        [a, role_name] = message.content.split(' ', 1)
        print("Adding Role " + role_name + " to " + str(message.guild) + " by " + str(message.author))
        await message.guild.create_role(name=role_name, mentionable=True,  reason="Added by " + str(message.author))

    async def onChangeColor(self, message, args):
        role = message.role_mentions[0]
        color_val = int(args[1][2:], 16)
        print("Changing Color of " + role.name + " to " + args[1])
        await role.edit(colour=color_val)

    async def onSetDescription(self, message, args):
        role = message.role_mentions[0]
        [command, tag, desc] =  message.content.split(' ', 2)
        print("Setting Description of " + role.name + " to " + desc)

        channel = await self.getTagChannel(role.guild)
        async for msg in channel.history(limit=200):
            if msg.role_mentions[0] == role:
                a = role.mention + " " + desc
                await msg.edit(content=a)

    async def onDelete(self, message, args):
        print("Removing Role")
        role_id = args[3:-1]
        role = message.guild.get_role(int(role_id))
        if role != None:
            await role.delete()

    async def onClearChannel(self, message, argument):
        print("Clearing Channel")
        await message.channel.purge()
        
    async def onWriteHelp(self, message, argument):
        a = """```!add [name of tag]
!color @[tag] [Hex Code]
!desc @[tag] [tag description]
!delete @[tag]```"""
        await message.channel.send(content=a, delete_after=10)




client = TagBot()
client.run('NzY1MjM4ODU5NDA3Mjk0NDc1.X4R6OQ.y4nscXaRWJ1thtzY5UsuvviJNMg')
#client.run(sys.argv[1])
