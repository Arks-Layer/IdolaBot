# -*- coding: utf-8 -*-
import os
import traceback

import discord
from discord.ext import commands, tasks

from datetime import datetime

from lib.api import IdolaAPI


IDOLA_USER_AGENT = os.getenv("IDOLA_USER_AGENT")
IDOLA_APP_VER = os.getenv("IDOLA_APP_VER")
IDOLA_DEVICE_ID = os.getenv("IDOLA_DEVICE_ID")
IDOLA_DEVICE_TOKEN = os.getenv("IDOLA_DEVICE_TOKEN")
IDOLA_TOKEN_KEY = os.getenv("IDOLA_TOKEN_KEY")
IDOLA_UUID = os.getenv("IDOLA_UUID")

idola = IdolaAPI(
    IDOLA_USER_AGENT,
    IDOLA_APP_VER,
    IDOLA_DEVICE_ID,
    IDOLA_DEVICE_TOKEN,
    IDOLA_TOKEN_KEY,
    IDOLA_UUID,
)


class IDOLA(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.border_fails = 0

        self.arena_border_100_channel = os.getenv("ARENA_BORDER_100_CHANNEL")
        self.arena_border_500_channel = os.getenv("ARENA_BORDER_500_CHANNEL")
        self.arena_border_1000_channel = os.getenv("ARENA_BORDER_1000_CHANNEL")
        self.suppression_border_100_channel = os.getenv("SUPPRESSION_BORDER_100_CHANNEL")
        self.suppression_border_1000_channel = os.getenv("SUPPRESSION_BORDER_1000_CHANNEL")
        self.suppression_border_5000_channel = os.getenv("SUPPRESSION_BORDER_5000_CHANNEL")
        self.creation_border_100_channel = os.getenv("CREATION_BORDER_100_CHANNEL")
        self.creation_border_1000_channel = os.getenv("CREATION_BORDER_1000_CHANNEL")
        self.creation_border_5000_channel = os.getenv("CREATION_BORDER_5000_CHANNEL")
        
        self.border_message_channel = os.getenv("BORDER_MESSAGE_CHANNEL")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Game("Ready!"))
        for guild in self.client.guilds:
            print(f"{self.client.user} is connected to the following guild:\n" f"{guild.name}(id: {guild.id})")

        # Start looping tasks
        self.relog.start()
        self.border_status_update.start()
        self.border_channel_update.start()
        self.border_pinned_update.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        traceback.print_exception(type(error), error, error.__traceback__)
        await ctx.send("An error occurred")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        try:
            idola.start()
            await ctx.send("IdolaBot has been restarted")
        except Exception as e:
            print(e, traceback.format_exc())
            await ctx.send("An error occurred, IdolaBot could not be restarted")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def save_profiles(self, ctx):
        try:
            idola.save_profile_cache()
            await ctx.send("Profile cache saved")
        except Exception as e:
            print(traceback.format_exc())
            await ctx.send(f"Error: Could not save profile cache - {e}")

    @tasks.loop(seconds=60)
    async def border_status_update(self):
        try:
            border_score = idola.get_top_100_raid_suppression_border()
            print(f"{border_score:,d} - SuppressionBorderTop100")
            await self.client.change_presence(activity=discord.Game(f"{border_score:,d} - SuppressionBorderTop100"))
        except Exception as e:
            print(e, traceback.format_exc())

    @tasks.loop(hours=4)
    async def relog(self):
        print("Relogging")
        idola.start()

    @tasks.loop(seconds=180)
    async def border_pinned_update(self):
        try:
            if not self.border_message_channel: return
            
            channel = self.client.get_channel(int(self.border_message_channel))
            print(f"Updating pinned message in {channel.name}")
            pinned_messages = await channel.pins()
            border_message = None
            for pinned_message in pinned_messages:
                if pinned_message.author.id == self.client.user.id:
                    border_message = pinned_message
                    print(f"Updating existing pinned message with ID {border_message.id}")
                    break
                    
            embed = discord.Embed(title="Idola Borders", color=discord.Colour.blue())
            
            #Arena
            border_score_point_100 = idola.get_top_100_arena_border()
            border_score_point_500 = idola.get_top_500_arena_border()
            border_score_point_1000 = idola.get_top_1000_arena_border()
            
            border_output=f"🥇100: {border_score_point_100:,d} points\n" if border_score_point_100 else "🥇100: Unknown\n"
            border_output+=f"🥇500: {border_score_point_500:,d} points\n" if border_score_point_500 else "🥇500: Unknown\n"
            border_output+=f"🥇1000: {border_score_point_1000:,d} points\n" if border_score_point_1000 else "🥇1000: Unknown\n"
            embed.add_field(name="Idola Arena Border", value=border_output, inline=False)
                
            #Suppression
            border_score_point_100 = idola.get_top_100_raid_suppression_border()
            border_score_point_500 = idola.get_top_500_raid_suppression_border()
            border_score_point_1000 = idola.get_top_1000_raid_suppression_border()
            border_score_point_5000 = idola.get_top_5000_raid_suppression_border()
            
            border_output=f"🥇100: {border_score_point_100:,d} points\n" if border_score_point_100 else "🥇100: Unknown\n"
            border_output+=f"🥇500: {border_score_point_500:,d} points\n" if border_score_point_500 else "🥇500: Unknown\n"
            border_output+=f"🥇1000: {border_score_point_1000:,d} points\n" if border_score_point_1000 else "🥇1000: Unknown\n"
            border_output+=f"🥇5000: {border_score_point_5000:,d} points\n" if border_score_point_5000 else "🥇5000: Unknown\n"
            embed.add_field(name="Idola Raid Suppression Border", value=border_output, inline=False)
        
            #Creation
            border_score_point_100 = idola.get_top_100_raid_creation_border()
            border_score_point_500 = idola.get_top_500_raid_creation_border()
            border_score_point_1000 = idola.get_top_1000_raid_creation_border()
            border_score_point_5000 = idola.get_top_5000_raid_creation_border()

            border_output=f"🥇100: {border_score_point_100:,d} points\n" if border_score_point_100 else "🥇100: Unknown\n"
            border_output+=f"🥇500: {border_score_point_500:,d} points\n" if border_score_point_500 else "🥇500: Unknown\n"
            border_output+=f"🥇1000: {border_score_point_1000:,d} points\n" if border_score_point_1000 else "🥇1000: Unknown\n"
            border_output+=f"🥇5000: {border_score_point_5000:,d} points\n" if border_score_point_5000 else "🥇5000: Unknown\n"
            embed.add_field(name="Idola Creation Border", value=border_output, inline=False)
        
            #Time
            current_time = idola.get_current_time()
            end_date = idola.get_raid_event_end_date()
            time_left = idola.datetime_difference(current_time, end_date)

            embed.add_field(name="Time Left", value=time_left, inline=False )
            embed.add_field(name="Current Time", value=idola.datetime_jp_format(current_time), inline=True)
            embed.add_field(name="Ending at", value=idola.datetime_jp_format(end_date), inline=True)
            
            if not border_message == None:
                await border_message.edit(embed=embed)
            else:
                border_message = await channel.send(embed=embed)
                await border_message.pin()
        except Exception as e:
            print(traceback.format_exc())
        
    @tasks.loop(seconds=120)
    async def border_channel_update(self):
        print("Updating channel borders")
        try:
            # Arena
            if self.arena_border_100_channel:
                arena_border_score_100 = idola.get_top_100_arena_border()
                channel = self.client.get_channel(int(self.arena_border_100_channel))
                await channel.edit(name=f"🥇100: {arena_border_score_100:,d}" if arena_border_score_100 else f"🥇100: Unknown")
            if self.arena_border_500_channel:
                arena_border_score_500 = idola.get_top_500_arena_border()
                channel = self.client.get_channel(int(self.arena_border_500_channel))
                await channel.edit(name=f"🥈500: {arena_border_score_500:,d}" if arena_border_score_500 else f"🥈500: Unknown")
            if self.arena_border_1000_channel:
                arena_border_score_1000 = idola.get_top_1000_arena_border()
                channel = self.client.get_channel(int(self.arena_border_1000_channel))
                await channel.edit(name=f"🥉1K: {arena_border_score_1000:,d}" if arena_border_score_1000 else f"🥉1K: Unknown")
            # Suppression
            if self.suppression_border_100_channel:
                raid_suppression_border_100 = idola.get_top_100_raid_suppression_border()
                channel = self.client.get_channel(int(self.suppression_border_100_channel))
                await channel.edit(name=f"🥇100: {raid_suppression_border_100:,d}" if raid_suppression_border_100 else f"🥇100: Unknown")
            if self.suppression_border_1000_channel:
                raid_suppression_border_1000 = idola.get_top_1000_raid_suppression_border()
                channel = self.client.get_channel(int(self.suppression_border_1000_channel))
                await channel.edit(name=f"🥈1K: {raid_suppression_border_1000:,d}" if raid_suppression_border_1000 else f"🥈1K: Unknown")
            if self.suppression_border_5000_channel:
                raid_suppression_border_5000 = idola.get_top_5000_raid_suppression_border()
                channel = self.client.get_channel(int(self.suppression_border_5000_channel))
                await channel.edit(name=f"🥉5K: {raid_suppression_border_5000:,d}" if raid_suppression_border_5000 else f"🥉5K: Unknown")
            # Creation
            if self.creation_border_100_channel:
                raid_creation_border_100 = idola.get_top_100_raid_creation_border()
                channel = self.client.get_channel(int(self.creation_border_100_channel))
                await channel.edit(name=f"🥇100: {raid_creation_border_100:,d}" if raid_creation_border_100 else f"🥇100: Unknown")
            if self.creation_border_1000_channel:
                raid_creation_border_1000 = idola.get_top_1000_raid_creation_border()
                channel = self.client.get_channel(int(self.creation_border_1000_channel))
                await channel.edit(name=f"🥈1K: {raid_creation_border_1000:,d}" if raid_creation_border_1000 else f"🥈1K: Unknown")
            if self.creation_border_5000_channel:
                raid_creation_border_5000 = idola.get_top_5000_raid_creation_border()
                channel = self.client.get_channel(int(self.creation_border_5000_channel))
                await channel.edit(name=f"🥉5K: {raid_creation_border_5000:,d}" if raid_creation_border_5000 else f"🥉5K: Unknown")
        except Exception as e:
            print(traceback.format_exc())

    @commands.command()
    async def arena_border(self, ctx):
        """Shows the Top 100 border for arena"""
        border_score_point_100 = idola.get_top_100_arena_border()
        border_score_point_500 = idola.get_top_500_arena_border()
        border_score_point_1000 = idola.get_top_1000_arena_border()

        current_time = idola.get_current_time()
        end_date = idola.get_raid_event_end_date()
        time_left = idola.datetime_difference(current_time, end_date)

        embed = discord.Embed(
            title="Idola Arena Border",
            color=discord.Colour.blue(),
        )
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/iXyk/IdolaBot/master/idola/lib/assets/arena.png"
        )
        embed.add_field(
            name="Top 100",
            value=f"{border_score_point_100:,d} points" if border_score_point_100 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 500",
            value=f"{border_score_point_500:,d} points" if border_score_point_500 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 1000",
            value=f"{border_score_point_1000:,d} points" if border_score_point_1000 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Time Left",
            value=time_left,
            inline=False
        )
        embed.add_field(
            name="Current Time",
            value=idola.datetime_jp_format(current_time),
            inline=True,
        )
        embed.add_field(
            name="Ending at",
            value=idola.datetime_jp_format(end_date),
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def suppression_border(self, ctx):
        """Shows the border for Idola Raid Suppression"""
        border_score_point_100 = idola.get_top_100_raid_suppression_border()
        border_score_point_500 = idola.get_top_500_raid_suppression_border()
        border_score_point_1000 = idola.get_top_1000_raid_suppression_border()
        border_score_point_5000 = idola.get_top_5000_raid_suppression_border()

        current_time = idola.get_current_time()
        end_date = idola.get_raid_event_end_date()
        time_left = idola.datetime_difference(current_time, end_date)

        embed = discord.Embed(
            title="Idola Raid Suppression Border",
            color=discord.Colour.blue(),
        )
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/iXyk/IdolaBot/master/idola/lib/assets/raid.png"
        )
        embed.add_field(
            name="Top 100",
            value=f"{border_score_point_100:,d} points" if border_score_point_100 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 500",
            value=f"{border_score_point_500:,d} points" if border_score_point_500 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 1000",
            value=f"{border_score_point_1000:,d} points" if border_score_point_1000 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 5000",
            value=f"{border_score_point_5000:,d} points" if border_score_point_5000 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Time Left",
            value=time_left,
            inline=False
        )
        embed.add_field(
            name="Current Time",
            value=idola.datetime_jp_format(current_time),
            inline=True,
        )
        embed.add_field(
            name="Ending at",
            value=idola.datetime_jp_format(end_date),
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def creation_border(self, ctx):
        """Shows the border for Idola Raid Creation"""
        border_score_point_100 = idola.get_top_100_raid_creation_border()
        border_score_point_500 = idola.get_top_500_raid_creation_border()
        border_score_point_1000 = idola.get_top_1000_raid_creation_border()
        border_score_point_5000 = idola.get_top_5000_raid_creation_border()

        current_time = idola.get_current_time()
        end_date = idola.get_raid_event_end_date()
        time_left = idola.datetime_difference(current_time, end_date)

        embed = discord.Embed(
            title="Idola Raid Creation Border",
            color=discord.Colour.blue()
        )
        embed.set_thumbnail(url="https://raw.githubusercontent.com/iXyk/IdolaBot/master/idola/lib/assets/raid.png")
        embed.add_field(
            name="Top 100",
            value=f"{border_score_point_100:,d} points" if border_score_point_100 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 500",
            value=f"{border_score_point_500:,d} points" if border_score_point_500 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 1000",
            value=f"{border_score_point_1000:,d} points" if border_score_point_1000 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Top 5000",
            value=f"{border_score_point_5000:,d} points" if border_score_point_5000 else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Time Left",
            value=time_left,
            inline=False
        )
        embed.add_field(
            name="Current Time",
            value=idola.datetime_jp_format(current_time),
            inline=True,
        )
        embed.add_field(
            name="Ending at",
            value=idola.datetime_jp_format(end_date),
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def arena_team(self, ctx, profile_id: int):
        """Shows the latest ranked arena team for a given profile_id"""
        arena_team = idola.get_arena_team_composition(profile_id)
        embed = discord.Embed(
            title=f"Team Score: {arena_team['team_score']:,d}",
            description=f"**Idomag**\nLaw: {arena_team['law_idomag']}\nChaos: {arena_team['chaos_idomag']}",
            color=discord.Colour.blue(),
        )
        embed.set_author(name=f"{arena_team['player_name']}")
        embed.set_thumbnail(url=arena_team["avatar_url"])

        embed.add_field(
            name="Law Characters",
            value=arena_team["law_characters"],
            inline=True,
        )
        embed.add_field(
            name="Weapon Symbols",
            value=arena_team["law_weapon_symbols"],
            inline=True,
        )
        embed.add_field(
            name="Soul Symbols",
            value=arena_team["law_soul_symbols"],
            inline=True,
        )
        embed.add_field(
            name="Chaos Characters",
            value=arena_team["chaos_characters"],
            inline=True,
        )
        embed.add_field(
            name="Weapon Symbols",
            value=arena_team["chaos_weapon_symbols"],
            inline=True,
        )
        embed.add_field(
            name="Soul Symbols",
            value=arena_team["chaos_soul_symbols"],
            inline=True,
        )
        embed.set_footer(text=78 * "\u200b")
        await ctx.send(embed=embed)

    @commands.command()
    async def arena_team_name(self, ctx, profile_name):
        """Shows the matching arena_team using their name if the profile_id has already been cached"""
        arena_team = idola.get_arena_team_composition_from_name(profile_name)
        if not arena_team:
            await ctx.send(
                "Could not find a player by that name in the cache, to update the cache run 'arena_team' using your profile id first"
            )
            return
        embed = discord.Embed(
            title=f"Team Score: {arena_team['team_score']:,d}",
            description=f"**Idomag**\nLaw: {arena_team['law_idomag']}\nChaos: {arena_team['chaos_idomag']}",
            color=discord.Colour.blue(),
        )
        embed.set_author(name=f"{arena_team['player_name']}")
        embed.set_thumbnail(url=arena_team["avatar_url"])

        embed.add_field(
            name="Law Characters",
            value=arena_team["law_characters"],
            inline=True,
        )
        embed.add_field(
            name="Weapon Symbols",
            value=arena_team["law_weapon_symbols"],
            inline=True,
        )
        embed.add_field(
            name="Soul Symbols",
            value=arena_team["law_soul_symbols"],
            inline=True,
        )
        embed.add_field(
            name="Chaos Characters",
            value=arena_team["chaos_characters"],
            inline=True,
        )
        embed.add_field(
            name="Weapon Symbols",
            value=arena_team["chaos_weapon_symbols"],
            inline=True,
        )
        embed.add_field(
            name="Soul Symbols",
            value=arena_team["chaos_soul_symbols"],
            inline=True,
        )
        embed.set_footer(text=78 * "\u200b")
        await ctx.send(embed=embed)

    @commands.command()
    async def arena_top_100(self, ctx):
        """Shows the Top 100 Arena players"""
        players = idola.show_arena_ranking_top_100_players()
        msg = []
        for profile_id, ranking_information in sorted(players.items(), key=lambda item: item[1]["arena_score_point"],):
            arena_score_rank = ranking_information["arena_score_rank"]
            arena_score_point = ranking_information["arena_score_point"]
            name = ranking_information["name"]
            msg.insert(
                0, f"{arena_score_rank}: {arena_score_point:,d} - {name}({profile_id})",
            )
        for j, chunks in enumerate([msg[i : i + 50] for i in range(0, len(msg), 50)]):
            text = "\n".join(chunks)
            embed = discord.Embed(
                title="Idola Arena Top 100" if j == 0 else "\u200b",
                description=f"```{text}```",
                color=discord.Colour.blue(),
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def suppression_top_100(self, ctx):
        """Shows the Top 100 Idola Raid Suppression players"""
        msg = idola.show_raid_suppression_top_100_players()
        msg = msg.split("\n")
        for j, chunks in enumerate([msg[i : i + 50] for i in range(0, len(msg), 50)]):
            text = "\n".join(chunks)
            embed = discord.Embed(
                title="Idola Raid Suppression Top 100" if j == 0 else "\u200b",
                description=f"```{text}```",
                color=discord.Colour.blue(),
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def creation_top_100(self, ctx):
        """Shows the Top 100 Idola Creation players"""
        msg = idola.show_raid_creation_top_100_players()
        msg = msg.split("\n")
        for j, chunks in enumerate([msg[i : i + 50] for i in range(0, len(msg), 50)]):
            text = "\n".join(chunks)
            embed = discord.Embed(
                title="Idola Raid Creation Top 100" if j == 0 else "\u200b",
                description=f"```{text}```",
                color=discord.Colour.blue(),
            )
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(IDOLA(client))
