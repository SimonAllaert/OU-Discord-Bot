#!/usr/bin/env python
import discord
from discord.ext import commands
import sqlite3 as lite

prefix = '$'

with open('token.txt', 'r') as file:
	token = file.readline()

bot = commands.Bot(command_prefix = prefix)
bot.remove_command('help')


"""
=======================================================================================================================
	Static variables
=======================================================================================================================
"""


GNCHANNEL = 581652748257198080
ROLECHANNEL = 570939014329401345
PRIVATECATEGORY = 580166156095062027

GNROLE = 570939688165310484
BOTROLE = 593126690042150913
PLEBIANROLE = 570937022643175434

BOT = 590170545845305346


"""
=======================================================================================================================
	Basics
=======================================================================================================================
"""


@bot.event
async def on_ready():
	print(discord.__version__)
	print('Oppai Bot is ready!')


@bot.event
async def on_resume():
	print("Oppai Bot is resumed!")


# Gives members who join the server the Plebian role
@bot.event
async def on_member_join(member):
	if not member.bot:
		role = member.guild.get_role(PLEBIANROLE) # Doesnt do bots cause permission problem
	# else:
	# 	role = discord.utils.get(member.guild.roles, name = "Server Assistant")
		await member.add_roles(role)


@bot.command(pass_context = True)
async def help(ctx):
	embed = discord.Embed(title = '**Commands**', color = discord.Colour.from_rgb(48, 114, 168))
	embed.add_field(name = "room", value = "Creates a voice channel that only you can join. You can invite others with $room_invite.", inline = False)
	embed.add_field(name = "room_invite *<mention any number of people you want to invite>*", value = "Invite any number of people by mentioning them.", inline = False)
	embed.add_field(name = "room_delete", value = "Delete your voice channel", inline = False)
	embed.add_field(name = "chat", value = "Creates a text channel that only you can join. You can invite others with $chat_invite.", inline = False)
	embed.add_field(name = "chat_invite *<mention any number of people you want to invite>*", value = "Invite any number of people by mentioning them.", inline = False)
	embed.add_field(name = "chat_delete", value = "Delete your voice channel", inline = False)
	embed.add_field(name = "ip", value = "Gives the IP of the server where games like gmod or SCP will be hosted on.", inline = False)
	embed.add_field(name = "prefix", value = "Gives the prefix of the bot.", inline = False)

	avatar_url = ctx.author.avatar_url
	if not avatar_url:
		avatar_url = ctx.author.default_avatar_url
	embed.set_thumbnail(url = avatar_url)

	avatar = await (bot.fetch_user(BOT))
	embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)

	await ctx.channel.send(embed = embed)


@bot.command(pass_context = True)
async def help_hidden(ctx):
	if authorised(ctx):
		embed = discord.Embed(title = '**Authorised Commands**', color = discord.Colour.from_rgb(48, 114, 168))
		embed.add_field(name = "create_manual_role *<input message with a role mention>*", value = "Creates a message with an emote. People who click the emoji join the mentioned role.", inline = False)
		embed.add_field(name = "addgn *<name (with underscores instead of spaces!)> <emoji> <description (optional, no use currently)>*", value = "Adds a game to the database", inline = False)
		embed.add_field(name = "delgn *<emoji>*", value = "Deletes the game with the given emoji from the database.", inline = False)
		embed.add_field(name = "allgn", value = "Shows all games in the database in alphabetical order", inline = False)
		embed.add_field(name = "gn *<custom message>*", value = "Creates the announcement vote for Game night with all games in the database. Also returns an id number, use this to end the vote with $votesgn <id number>", inline = False)
		embed.add_field(name = "votesgn *<id given by the $gn command>", value = "Counts all votes from the last message in the game-night channel and posts the results there.", inline = False)

		avatar_url = ctx.author.avatar_url
		if not avatar_url:
			avatar_url = ctx.author.default_avatar_url
		embed.set_thumbnail(url = avatar_url)

		avatar = await (bot.fetch_user(BOT))
		embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)

		await ctx.channel.send(embed = embed)

"""
=======================================================================================================================
	Manual role management
=======================================================================================================================
"""


@bot.command(pass_context = True, hidden=True)
async def create_manual_role(ctx, *input):
	output = to_string(input)
	message = await ctx.channel.send(output)
	await message.add_reaction("📩")
	await ctx.channel.delete_messages([ctx.message])


@bot.event
async def on_raw_reaction_add(payload):
	if payload.channel_id == ROLECHANNEL and not bot.get_user(payload.user_id).bot:
		channel = discord.utils.get(bot.get_all_channels(), id = payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		role = message.role_mentions[0]
		member = bot.get_guild(payload.guild_id).get_member(payload.user_id)
		if not discord.utils.get(member.roles, id = role.id):
			await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
	if payload.channel_id == ROLECHANNEL and not bot.get_user(payload.user_id).bot:
		channel = discord.utils.get(bot.get_all_channels(), id = payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		role = message.role_mentions[0]
		member = bot.get_guild(payload.guild_id).get_member(payload.user_id)
		if discord.utils.get(member.roles, id = role.id):
			await member.remove_roles(role)


"""
=======================================================================================================================
	Private voice/text channels
=======================================================================================================================
"""


@bot.command(pass_context = True)
async def room(ctx):
	if discord.utils.get(ctx.guild.voice_channels, name = ctx.author.name + "'s room"):
		await ctx.channel.send("You already have a private room 😤")
	else:
		channel = await ctx.guild.create_voice_channel(ctx.author.name + "'s room", category = discord.utils.get(ctx.guild.categories, id = PRIVATECATEGORY))
		await channel.set_permissions(ctx.guild.default_role, connect = False, speak = False)
		await channel.set_permissions(ctx.author, manage_channels = True, read_messages = True, connect = True, speak = True, move_members = True)
		await ctx.message.add_reaction('✅')


@bot.command(pass_context = True)
async def room_invite(ctx, *mentions):
	channel = discord.utils.get(ctx.guild.voice_channels, name = ctx.author.name + "'s room")
	if channel:
		for mention in ctx.message.mentions:
			invite = await channel.create_invite(max_uses = 1)
			await channel.set_permissions(mention, read_messages = True, connect = True, speak = True)
			await mention.send("Invite from " + ctx.author.name + ":\nhttp://discord.gg/" + invite.code)
		await ctx.message.add_reaction('✅')
	else:
		await ctx.channel.send("You don't have a private room 😤")


@bot.command(pass_context = True)
async def room_delete(ctx):
	channel = discord.utils.get(ctx.guild.voice_channels, name = ctx.author.name + "'s room")
	if channel:
		await channel.delete()
		await ctx.message.add_reaction('✅')
	else:
		await ctx.channel.send("You don't have a private room 😤")


@bot.command(pass_context = True)
async def chat(ctx):
	if discord.utils.get(ctx.guild.text_channels, name = str(ctx.author.name).lower() + "s-chat"):
		await ctx.channel.send("You already have a private chat 😤")
	else:
		channel = await ctx.guild.create_text_channel(str(ctx.author.name).lower() + "s-chat", category = discord.utils.get(ctx.guild.categories, id = PRIVATECATEGORY))
		await channel.set_permissions(ctx.guild.default_role, read_messages = False, send_messages = False)
		await channel.set_permissions(ctx.author, manage_channels = True, read_messages = True, send_messages = True)
		await ctx.message.add_reaction('✅')


@bot.command(pass_context = True)
async def chat_invite(ctx, *mentions):
	channel = discord.utils.get(ctx.guild.text_channels, name = str(ctx.author.name).lower() + "s-chat")
	if channel:
		for mention in ctx.message.mentions:
			invite = await channel.create_invite(max_uses = 1)
			await channel.set_permissions(mention, read_messages = True, send_messages = True)
			await mention.send("Invite from " + ctx.author.name + ":\nhttp://discord.gg/" + invite.code)
		await ctx.message.add_reaction('✅')
	else:
		await ctx.channel.send("You don't have a private chat 😤")


@bot.command(pass_context = True)
async def chat_delete(ctx):
	channel = discord.utils.get(ctx.guild.text_channels, name = str(ctx.author.name).lower() + "s-chat")
	if channel:
		await channel.delete()
		await ctx.message.add_reaction('✅')
	else:
		await ctx.channel.send("You don't have a private chat 😤")

"""
=======================================================================================================================
	Auto game night
=======================================================================================================================
"""


@bot.command(pass_context = True)
async def ip(ctx):
	await ctx.channel.send("`94.224.117.42`")


@bot.command(pass_context = True)
async def prefix(ctx):
	await ctx.channel.send("Seems kinda obvious :thinking:")


# @bot.command(pass_context = True, hidden = True)
# async def creategn(ctx):
# 	if await authorised(ctx):
# 		connection = lite.connect('oppai.db')
# 		with connection:
# 			cursor = connection.cursor()
# 			cursor.execute("CREATE TABLE Gamenight(name TEXT, emoji TEXT, description TEXT)")
# 		connection.close()
# 		await ctx.message.add_reaction('✅')


@bot.command(pass_context = True, hidden = True)
async def addgn(ctx, name, emoji, *description):
	if await authorised(ctx):
		connection = lite.connect('oppai.db')
		descriptionstr = to_string(description)
		with connection:
			cursor = connection.cursor()
			sql = "INSERT INTO Gamenight VALUES(?, ?, ?)"
			cursor.execute(sql, (name, emoji, descriptionstr))
		connection.close()
		await ctx.message.add_reaction('✅')


@bot.command(pass_context = True, hidden = True)
async def delgn(ctx, emoji):
	if await authorised(ctx):
		connection = lite.connect('oppai.db')
		with connection:
			cursor = connection.cursor()
			sql = "DELETE FROM Gamenight WHERE emoji LIKE ?"
			cursor.execute(sql, (emoji,))
		connection.close()
		await ctx.message.add_reaction('✅')


@bot.command(pass_context = True, hidden = True)
async def allgn(ctx):
	if await authorised(ctx):
		connection = lite.connect('oppai.db')
		with connection:
			cursor = connection.cursor()
			sql = "SELECT * FROM Gamenight ORDER BY name"
			cursor.execute(sql)
			output = cursor.fetchall()
		connection.close()

		embed = discord.Embed(title = "Game night games", color = discord.Colour.from_rgb(48, 114, 168))
		games = output
		for game in games:
			name = to_string(game[0].split('_'))
			embed.add_field(name = name, value = game[1])

		avatar_url = ctx.author.avatar_url
		if not avatar_url:
			avatar_url = ctx.author.default_avatar_url
		embed.set_thumbnail(url = avatar_url)

		avatar = await (bot.fetch_user(BOT))
		embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)
		await ctx.channel.send(embed = embed)


@bot.command(pass_context = True, hidden = True)
async def gn(ctx, *input):
	if await authorised(ctx):
		channel = ctx.guild.get_channel(GNCHANNEL)
		role = ctx.guild.get_role(GNROLE)
		embed = discord.Embed(title = "Game night vote", color = 1146986, description = "Vote for what games you want to play:")

		games = gngames()
		emoji = []
		for game in games:
			name = to_string(game[0].split('_'))
			embed.add_field(name = name, value = " " + str(game[1]))
			emoji.append(game[1])

		avatar = await (bot.fetch_user(BOT))
		embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)
		output = to_string(input)
		result = await channel.send(role.mention + " " + output, embed = embed)
		for e in emoji:
			if len(e.split(":")) > 1:
				await result.add_reaction(discord.utils.get(ctx.guild.emojis, name= e.split(":")[1]))
			else:
				await result.add_reaction(e)
		await ctx.channel.send(result.id)


@bot.command(pass_context = True, hidden = True)
async def votesgn(ctx, id):
	if await authorised(ctx):
		channel = ctx.guild.get_channel(GNCHANNEL)
		role = ctx.guild.get_role(GNROLE)
		message = await channel.fetch_message(id)
		embed = discord.Embed(title = "Game night vote results", color = 1146986, description = "Results of the game night votes:")
		reactions = sort_reactions(message.reactions)

		for react in reactions:
			name = get_game(react.emoji)[0][0]
			embed.add_field(name = name, value = react.emoji + ": **" + str(react.count - 1) + "**", inline = False)

		avatar = await (bot.fetch_user(BOT))
		embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)
		await channel.send(role.mention, embed = embed)


# get all games from database
def gngames():
	connection = lite.connect('oppai.db')
	with connection:
		cursor = connection.cursor()
		sql = "SELECT * FROM Gamenight"
		cursor.execute(sql)
		output = cursor.fetchall()
	connection.close()
	return output


# get game by emoji
def get_game(emoji):
	connection = lite.connect('oppai.db')
	with connection:
		cursor = connection.cursor()
		sql = "SELECT * FROM Gamenight WHERE emoji LIKE ?"
		cursor.execute(sql, (emoji,))
		output = cursor.fetchall()
	connection.close()
	return output


# Bubble sort reactions, highest count first
def sort_reactions(reacts):
	def swap(i, j):
		reacts[i], reacts[j] = reacts[j], reacts[i]

	n = len(reacts)
	swapped = True

	x = -1
	while swapped:
		swapped = False
		x += 1
		for i in range(1, n - x):
			if reacts[i - 1].count < reacts[i].count:
				swap(i - 1, i)
				swapped = True
	return reacts

"""
=======================================================================================================================
	Help functions
=======================================================================================================================
"""


async def authorised(ctx):
	if ctx.author.top_role.position < ctx.guild.get_role(BOTROLE).position:
		await ctx.channel.send("unauthorised command 😤")
		return False
	return True


def to_string(input):
	res = ""
	for string in input:
		res += str(string) + " "
	res = res[:-1]
	return res


bot.run(token)
# bot.close()
