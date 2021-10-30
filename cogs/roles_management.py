import discord
import os
import asyncio
import main
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle


# Initierea clasului
class RolesManagement(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Channel cleaning command
	@commands.command()
	@commands.has_role('Admin')
	async def delete_unused_roles(self, ctx):
		pass


def setup(client):
	client.add_cog(RolesManagement(client))
