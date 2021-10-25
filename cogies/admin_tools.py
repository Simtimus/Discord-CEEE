import discord
import os
from discord.ext import commands


# Initierea clasului
class Admin(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Channel cleaning command
	@commands.command(aliases=['purge', 'clean', 'cls'])
	@commands.has_role('Admin')
	async def clear(self, ctx, amount=2):
		await ctx.channel.purge(limit=amount)


def setup(client):
	client.add_cog(Admin(client))