#!/usr/bin/env python
import discord
from discord.ext import commands
import sqlite3 as lite

prefix = '$'

with open('demotoken.txt', 'r') as file:
	token = file.readline()

bot = commands.Bot(command_prefix = prefix)
bot.remove_command('help')

@bot.event
async def on_ready():
	print(discord.__version__)
	print('Demo Oppai Bot is ready!')


@bot.event
async def on_resume():
	print("Demo Oppai Bot is resumed!")


@bot.event
async def on_guild_join(guild):
	await guild.create_role(name = "Demo Oppai Bot", managed = True)


@bot.event              # Gives members who join the server the Plebian role
async def on_member_join(member):
	if not member.bot:
		role = member.guild.get_role(590179116687556628) # Doesnt do bots cause permission problem
	# else:
	# 	role = discord.utils.get(member.guild.roles, name = "Server Assistant")
		await member.add_roles(role)


@bot.command(pass_context = True)
async def help(ctx):
	embed = discord.Embed(title = '**Commands**', color = discord.Colour.from_rgb(48, 114, 168))
	embed.add_field(name = "room", value = "Creates a voice channel that only you can join. You can invite others with room_invite.", inline = False)
	embed.add_field(name = "room_invite *<mention any number of people you want to invite>*", value = "Invite any number of people by mentioning them.", inline = False)
	embed.add_field(name = "room_delete", value = "Delete your voice channel", inline = False)

	avatar_url = ctx.author.avatar_url
	if not avatar_url:
		avatar_url = ctx.author.default_avatar_url
	embed.set_thumbnail(url = avatar_url)

	avatar = await (bot.fetch_user(590170545845305346))
	embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)

	await ctx.channel.send(embed = embed)


@bot.command(pass_context = True)
async def help_hidden(ctx):
	embed = discord.Embed(title = '**Authorised Commands**', color = discord.Colour.from_rgb(48, 114, 168))
	embed.add_field(name = "create_manual_role *<input message with a role mention>*", value = "Creates a message with an emote. People who click the emoji join the mentioned role.", inline = False)
	embed.add_field(name = "addgn *<name (with underscores instead of spaces!)> <emoji> <description (optional, no use currently)>*", value = "Adds a game to the database", inline = False)
	embed.add_field(name = "delgn *<emoji>*", value = "Deletes the game with the given emoji from the database.", inline = False)
	embed.add_field(name = "allgn", value = "Shows all games in the database in alphabetical order", inline = False)
	embed.add_field(name = "gn", value = "Creates the announcement vote for Game night with all games in the database.")

	avatar_url = ctx.author.avatar_url
	if not avatar_url:
		avatar_url = ctx.author.default_avatar_url
	embed.set_thumbnail(url = avatar_url)

	avatar = await (bot.fetch_user(590170545845305346))
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
	if payload.channel_id == 590184386297856032 and not bot.get_user(payload.user_id).bot:
		channel = discord.utils.get(bot.get_all_channels(), id = payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		role = message.role_mentions[0]
		member = bot.get_guild(payload.guild_id).get_member(payload.user_id)
		await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
	if payload.channel_id == 590184386297856032 and not bot.get_user(payload.user_id).bot:
		channel = discord.utils.get(bot.get_all_channels(), id = payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		role = message.role_mentions[0]
		member = bot.get_guild(payload.guild_id).get_member(payload.user_id)
		await member.remove_roles(role)

"""
=======================================================================================================================
	Private voice channels
=======================================================================================================================
"""


@bot.command(pass_context = True)
async def room(ctx):
	if discord.utils.get(ctx.guild.voice_channels, name = ctx.author.name + "'s room"):
		await ctx.channel.send("You already have a private room 😤")
	else:
		channel = await ctx.guild.create_voice_channel(ctx.author.name + "'s room", category = discord.utils.get(ctx.guild.categories, id = 590174900539490315))
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

"""
=======================================================================================================================
	Auto game night
=======================================================================================================================
"""


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

		avatar = await (bot.fetch_user(590170545845305346))
		embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)
		await ctx.channel.send(embed = embed)


@bot.command(pass_context = True, hidden = True)
async def gn(ctx):
	if await authorised(ctx):
		role = ctx.guild.get_role(590185613433634846)
		embed = discord.Embed(title = "Game night vote", color = 1146986, description = "Vote for what games you want to play:")

		games = gngames()
		emoji = []
		for game in games:
			name = to_string(game[0].split('_'))
			embed.add_field(name = name, value = game[1])
			emoji.append(game[1])

		avatar = await (bot.fetch_user(590170545845305346))
		embed.set_footer(text = "powered by Oppai United", icon_url = avatar.avatar_url)
		result = await ctx.channel.send(role.mention, embed = embed)
		await ctx.channel.delete_messages([ctx.message])
		for e in emoji:
			await result.add_reaction(e)


def gngames():
	connection = lite.connect('oppai.db')
	with connection:
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM Gamenight")
		output = cursor.fetchall()
	connection.close()
	return output


"""
=======================================================================================================================
	Help functions
=======================================================================================================================
"""


async def authorised(ctx):
	if ctx.author.top_role.position < ctx.guild.get_role(590175228567748619).position:
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
