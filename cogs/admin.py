from datetime import datetime

import aiosqlite as sql
import discord
from discord.ext import commands
from discord.utils import get


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Check Member Info")
    async def check(self, ctx, member: discord.Member = None):
        """
        Check Member Info
        """
        member = ctx.author if not member else member
        roles = [i.mention for i in member.roles if i.name != "@everyone"]
        roles = '\n'.join(roles[::-1])
        created = member.created_at.split(".")[0]
        joined = member.joined_at.split(".")[0]
        card = discord.Embed(
            title=f"Info about {member}",
            timestamp=datetime.utcnow()
        )
        card.set_thumbnail(url=member.avatar_url_as(static_format='png'))
        card.add_field(name="Joined at", value=f"Member joined this server at **{joined}**")
        card.add_field(name="Joined discord at", value=f"User joined discord at **{created}**")
        card.add_field(name="Member roles", value=roles)
        await ctx.send(embed=card)

    @commands.command(aliases=["creds"])
    async def credits(self, ctx):
        """
        Show credits about the bot
        """
        creator = self.bot.get_user(716503311402008577)

        card = discord.Embed(
            colour=0x0064ff,
            title="Credits for Systema bot",
            timestamp=datetime.utcnow()
        )
        card.add_field(name="Creator", value=f"{creator} created this bot")
        owner = self.bot.get_user(self.bot.owner_id)
        card.set_footer(text=f"Copyright© {datetime.utcnow().year} {owner}",
                        icon_url=creator.avatar_url_as(static_format='png'))
        await ctx.send(embed=card)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, name, *, rgb):
        """
        Create roles with name and colors!. *note rgb is separated with comma(,) ex: 255,255,255
        """
        rgb = rgb.split(",")
        rgb = [int(i) for i in rgb]
        role = await ctx.guild.create_role(name=name, colour=discord.Colour.from_rgb(rgb[0], rgb[1], rgb[2]))
        await ctx.send(f"Created role, Info:\nName: {role.name}\nColour: {role.colour}\nID: {role.id}")

    @commands.command()
    async def permissions(self, ctx):
        """
        Shows bot permission integer
        """
        await ctx.send(ctx.guild.me.guild_permissions)

    @commands.command(aliases=["clear", "yeet"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 5):
        """
        Purge messages default to 5 message
        """
        if amount > 1000:
            amount = 1000

        def check(m):
            return False if m.pinned else True

        async with ctx.channel.typing():
            deleted = await ctx.channel.purge(limit=amount, check=check)
        card = discord.Embed(
            colour=discord.Colour.from_rgb(0, 255, 100),
            title=f"Purged {len(deleted)} messages"
        )
        await ctx.send(embed=card, delete_after=3)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member):
        """
        Mute member. *note: it is permanent and to unmute, admin will do it manually by executing a command
        """
        role = get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        await ctx.send(f"🔇 Muted {member.display_name}")
        async with sql.connect("./db/data.sql") as db:
            await db.execute("INSERT INTO muted (id,name,date) VALUES (?,?,?)",
                             (member.id, member.name, datetime.utcnow(),))
            await db.commit()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """
        Unmute member
        """
        roles = [i.name for i in member.roles]
        role = get(ctx.guild.roles, name="Muted")
        if "Muted" in roles:
            await ctx.send(f"🔈 Unmuted {member.display_name}")
            await member.remove_roles(role)
            async with sql.connect("./db/data.sql") as db:
                await db.execute("DELETE FROM muted WHERE id = ?", (member.id,))
                await db.commit()
        else:
            await ctx.send("Member is not muted")

    @commands.command()
    @commands.is_owner()
    async def dc(self, ctx):
        """
        Disconnect the bot (owner of bot only)
        """
        await ctx.send("Disconnected!")
        await self.bot.logout()

    @commands.Cog.listener()
    async def wait_until_ready(self):
        async with sql.connect("./db/data.sql") as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS muted(id INTEGER PRIMARY KEY,userid INTEGER,name TEXT,date DATETIME")
            await db.commit()


def setup(bot):
    print("#Loaded admin")
    bot.add_cog(Admin(bot))
