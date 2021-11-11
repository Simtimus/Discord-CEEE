import discord
import os
import asyncio
import main
import config
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
import validator as valid


def create_embed(ctx: discord.Message, title: str, description: str, colour: hex = discord.Colour.blue()) -> discord.Embed:
	embed = discord.Embed(
		title=title,
		description=description,
		colour=colour
	)
	embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
	return embed


# Initierea clasului
class RolesManagement(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Asocierea rolurilor si canalelor
	@commands.command()
	@commands.has_role('Admin')
	async def unconfirm(self, ctx):
		await ctx.channel.purge(limit=1)
		for member in ctx.guild.members:
			for role in ctx.guild.roles:
				if role.name == config.unconfirmed_member_name:
					await member.add_roles(role)
		embed = create_embed(ctx, 'Procesul de unconfirmare', 'Finisat', discord.Colour.purple())
		await ctx.channel.send(embed=embed)

	# Channel cleaning command
	@commands.command(aliases=['delrole'])
	@commands.has_role('Admin')
	async def delete_unused_roles(self, ctx):
		await ctx.channel.purge(limit=1)
		for role in ctx.guild.roles:
			if role.name not in config.important_roles_name:
				if len(role.members) == 0:
					await role.delete()
		embed = create_embed(ctx, 'Stergerea rolurilor neutilizate', 'Finisat', discord.Colour.purple())
		await ctx.channel.send(embed=embed)

	# Channel cleaning command
	@commands.command(aliases=['posrole'])
	@commands.has_role('Admin')
	async def position_roles(self, ctx):
		await ctx.channel.purge(limit=1)
		pass


def setup(client):
	client.add_cog(RolesManagement(client))
