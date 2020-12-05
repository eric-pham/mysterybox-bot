import discord
import random
import time
import json
from datetime import datetime
from discord.ext import commands

path = "./Images/"

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print('Bot is ready.')


@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

    update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)


@commands.cooldown(1, 15, commands.BucketType.guild)
@client.command()
async def spin(context):
    with open('users.json', 'r') as f:
        users = json.load(f)

    outcome = spin_valid(users, context.message.author.id)

    if outcome == 1:
        await context.send(
            "You are not in the system please try \".startgame\"")
    elif 2 <= outcome <= 3:
        await actual_spin(context, users)
    elif outcome == 4:
        await context.send("It hasn't been 10 minutes from your last spin!")

    with open('users.json', 'w') as f:
        json.dump(users, f)


async def actual_spin(context, users):
    message = await context.send(file=discord.File(path + "mysterybo.gif"))
    time.sleep(5)

    weapon = choose_random()
    name = weapon

    if weapon == "HAHAHHAHA BYE BYE":
        name = "HAHAHHAHA... BYE BYE!!"

    file = discord.File(path + weapon + '.png', filename='image.png')
    embed = discord.Embed(
        title=name,
        color=discord.colour.Color.from_rgb(76, 214, 189)
    )

    embed.set_image(url="attachment://image.png")
    await context.send("<@{}>, you got:".format(context.message.author.id))
    picture = await context.send(file=file, embed=embed)
    if embed.title == "HAHAHHAHA... BYE BYE!!":
        return
    await picture.add_reaction("✅")
    await picture.add_reaction('🚫')
    await picture.add_reaction("🔁")

    time.sleep(1)
    await message.delete()
    time.sleep(10)
    cache_msg = await context.fetch_message(picture.id)
    r_users = cache_msg.reactions
    reaction = await check_reacts(r_users, context.message.author.id)
    if reaction is None:
        await context.send("Times up, <@{}>! Try again in 10 minutes.".format(
            context.message.author.id))
        return
    if reaction.emoji == "✅":
        if len(users[str(context.message.author.id)]["Weapons"]) >= 2:
            await context.send("You already have 2 weapons")
            await swap_weapons(context, users, context.message.author.id,
                               weapon)
        else:
            add_to_inventory(users, context.message.author.id, weapon)
            await context.send(str(weapon) + ' added to loadout')
    elif reaction.emoji == "🚫":
        await context.send(str(weapon) + ' has been skipped')
    elif reaction.emoji == "🔁":
        if len(users[str(context.message.author.id)]["Weapons"]) < 2:
            add_to_inventory(users, context.message.author.id, weapon)
            await context.send(
                "You have less than 2 weapons so " + str(weapon) +
                ' has been added to your loadout')
        else:
            await swap_weapons(context, users, context.message.author.id,
                               weapon)
    else:
        await context.send("Times up, <@{}>! Try again in 10 minutes.".format(
            context.message.author.id))


@client.command()
async def startgame(context):
    with open('users.json', 'r') as f:
        users = json.load(f)

    update_data(users, context.message.author)
    await context.send("<@{}> has joined the game".format(
        context.message.author.id))

    with open('users.json', 'w') as f:
        json.dump(users, f)


@client.command()
async def loadout(context):
    with open('users.json', 'r') as f:
        users = json.load(f)

    inv = print_inventory(users, context.message.author.id)
    weapons = ''
    for weapon in inv:
        weapons = weapons + "**" + weapon + "**" + " & "
    weapons = weapons[:-3]
    await context.send("<@{}>'s loadout: ".format(
        context.message.author.id) + str(weapons))
    for weapon in inv:
        file = discord.File(path + weapon.strip() + '.png',
                            filename='image.png')
        embed = discord.Embed(
            title=weapon,
            color=discord.colour.Color.from_rgb(128, 128, 128)
        )
        embed.set_image(url="attachment://image.png")
        await context.send(file=file, embed=embed)

    with open('users.json', 'w') as f:
        json.dump(users, f)


@client.command()
async def mbhelp(context):
    command_text = "**.startgame** - this command will put you in the game. " \
                   "You can not spin unless you are first registered in the " \
                   "game\n" \
                   "**.spin** - spin the box (timer set to one spin every 10 " \
                   "minutes)\n" \
                   "**.loadout** - view the current guns in your loadout\n\n"

    how_to_play = "When you spin the box, you will get a weapon that you can " \
                  "either add to your loadout or discard.\n\n"

    note = "__**Do not try to spin while someone else is using the command. " \
           "You must wait 15 seconds between spins on the server to avoid " \
           "crashing the bot**__\n\n"
    credits = "Created by Eric & Bailey"
    embed = discord.Embed(
        description="__**COMMANDS**__\n" + command_text +
                    "__**HOW TO PLAY**__\n" + how_to_play + note + credits,
        colour=discord.Color.from_rgb(255, 219, 88)
    )
    await context.send(embed=embed)


def update_data(users, user):
    user_string = str(user.id)

    if user_string not in users:
        users[user_string] = {}
        users[user_string]['Last'] = ''
        users[user_string]['Weapons'] = []


def choose_random() -> str:
    wonder = [
        "Ray Gun Mark II", "Wunderwaffe DG-2", "Ray Gun", "Thundergun",
        "Paralyzer", "Winter's Howl", "Gersch Device", 'Matryoshka Doll',
        "Apothicon Servant", "Monkey Bombs", "Scavenger"
    ]

    regular = [
        "Galil", "Spectra",
        "CZ-75", "MP-40", "STG-44", "M1911", "AK74u",
        "Blundergat", "Ballistic Knife", "Crossbow",
        "China Lake", "RPG", "RPK", "AUG",
        "HAHAHHAHA BYE BYE", "War Machine", "Type 25", "MTAR", "FAL", "HK21",
        "SPAS-12", "MPL", "M16", "Famas", "Olympia", "M14", "Stakeout",
        "Dragunov", "HS-10", "L96AI", "M60", "M72 LAW", "Python", "Executioner",
        "Commando", "EMP Grenade", "AN-94",
        "M1927 Tommy Gun", "Remington New Model Army", "Kar98k",
        "Thompson", "Chicom CQB", "Five Seven",
        "Five Seven Dual Wield", "M2 Flamethrower", "SCAR-H",
    ]
    weapons = wonder + regular + regular + regular + regular
    # print(weapons)
    choice = random.choice(weapons)
    # print(len(weapons))
    return choice


def spin_valid(users: dict, i_author: int) -> int:
    current_time = datetime.now()
    author = str(i_author)
    user_current = current_time.strftime("%H:%M")
    fmt = '%H:%M'

    if author not in users:
        return 1

    if users[author]['Last'] == '':
        users[author]['Last'] = user_current
        return 2

    user_last = users[author]['Last']
    tdelta = datetime.strptime(user_current, fmt) - datetime.strptime(user_last,
                                                                      fmt)
    if tdelta.total_seconds() >= 600 or tdelta.total_seconds() < 0:
        users[author]['Last'] = user_current
        return 3
    else:
        return 4


async def check_reacts(reactions, o_user):
    for reaction in reactions:
        users = await reaction.users().flatten()
        for user in users:
            if o_user == user.id:
                return reaction


def add_to_inventory(users: dict, user, item):
    users[str(user)]["Weapons"].append(item)


def print_inventory(users, user):
    return users[str(user)]["Weapons"]


async def swap_weapons(context, users, user, weapon):
    weapons = users[str(user)]["Weapons"]
    choices = await context.send("Swap **[1]" + weapons[0] + "** or **[2]" +
                                 weapons[1] + "**")
    await choices.add_reaction("1️⃣")
    await choices.add_reaction("2️⃣")

    time.sleep(5)
    cache_msg = await context.fetch_message(choices.id)
    r_users = cache_msg.reactions
    reaction = await check_reacts(r_users, context.message.author.id)

    if reaction is None:
        await context.send("Times up, <@{}>! Try again in 10 minutes.".format(
            context.message.author.id))
        return

    if reaction.emoji == "1️⃣":
        users[str(user)]["Weapons"].pop(0)
        users[str(user)]["Weapons"].insert(0, weapon)
        await context.send(str(weapon) + ' added to loadout')
    elif reaction.emoji == "2️⃣":
        users[str(user)]["Weapons"].pop(1)
        users[str(user)]["Weapons"].append(weapon)
        await context.send(str(weapon) + ' added to loadout')

    else:
        await context.send("Times up, <@{}>! Try again in 10 minutes.".format(
            context.message.author.id))


# Put your discord bot token here
client.run('INSERT YOUR TOKEN HERE')
