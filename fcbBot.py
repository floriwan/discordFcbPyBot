# fcbBot.py

import os
import json
import discord
import logging
import discord
import fcbBotUtils

from urllib.request import URLError, HTTPError, Request, urlopen

from dotenv import load_dotenv
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
load_dotenv()

AVWX_TOKEN = os.getenv('AVWX_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

avwx_headers = {
  'Authorization': AVWX_TOKEN
}


bot = commands.Bot(command_prefix='!')

def requestMetarJson(icao_code):
    request = Request('https://avwx.rest/api/metar/' +  icao_code.lower(), headers=avwx_headers)
    response_body = urlopen(request).read()
    #print(response_body)
    return json.loads(response_body)

def requestAirportInfoJson(icao_code):
    request = Request('https://avwx.rest/api/station/' +  icao_code.lower(), headers=avwx_headers)
    response_body = urlopen(request).read()
    #print(response_body)
    return json.loads(response_body)

def requestCharts(icao_code):
    url = 'https://vau.aero/navdb/chart/' +  icao_code.upper() + '.pdf'
    print("chart url:" + url)

    user_agent = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    request = Request(url, headers={'User-Agent': user_agent})

    try:
        response = urlopen(request)
        return url

    except HTTPError as e:
        print ("chart reqeust error code: " + str(e.getcode()))
        return "no charts available for " + icao_code.upper()
        

@bot.command(name='hallo', help='respone with hello')
async def nine_nine(ctx):
    response = f'Hallo'
    await ctx.send(response)

#@bot.command(name='commands', help='get a list of all bot commands')
#async def commands(ctx):
#    response = f'!metar <icaocode>'
#    await ctx.send(response)

@bot.command(name='zulu', help='respond with the zulu time')
async def zulu(ctx):

    from datetime import datetime
    utctime = datetime.utcnow()
    await ctx.send("it is " + str(utctime.hour)  + str(utctime.minute) + "z")

@bot.command(name='charts', help='get charts for icao airport')
async def charts(ctx, icao_code: str):
    response = f'' + requestCharts(icao_code)

    embed = discord.Embed(title="charts for " + icao_code.upper())
    if response.startswith("no "):
        embed.add_field(name="charts", value=response)
    else:
        embed.add_field(name="charts", value="[Click here for " + icao_code.upper() + " charts](" + response + ")")
    await ctx.author.send(embed=embed)

    await ctx.send("link to the charts of " + icao_code.upper() + " is send to you")

@bot.command(name='metar', help='get metar information for icao airport')
async def metar(ctx, icao_code: str):

    if len(icao_code) != 4:
        await ctx.send("" + icao_code + " is not a valid icao code")
        return
    
    python_airportInfo = requestAirportInfoJson(icao_code.lower())
    python_obj = requestMetarJson(icao_code.lower())

    raw_metar = python_obj["raw"]
    print("metar : " + raw_metar)

    raw_date = python_obj["time"]["dt"]
    cur_date = raw_date[:10]
    cur_time = raw_date[12:]

    if python_obj["wind_direction"]["repr"] == "VRB":
        wind_info = "wind variable with " + \
            str(python_obj["wind_speed"]["repr"]) + " knots (" + \
            str(fcbBotUtils.knotsToKmh(python_obj["wind_speed"]["value"])) + \
            " km/h)"
    else:
        wind_info = "wind from " + \
            fcbBotUtils.degToDir(python_obj["wind_direction"]["value"]) + \
            " (" + str(python_obj["wind_direction"]["repr"]) + \
            " degrees) with " + \
            str(python_obj["wind_speed"]["repr"]) + " knots (" + \
            str(fcbBotUtils.knotsToKmh(python_obj["wind_speed"]["value"])) + \
            " km/h)"

    if python_obj["units"]["altimeter"] == "hPa":
        pressure_info = str(python_obj["altimeter"]["value"]) + \
            " hPa (" + str(fcbBotUtils.hPaToInHg(python_obj["altimeter"]["value"])) + \
            " inHg)"
    else:
        pressure_info = str(python_obj["altimeter"]["value"]) + \
            " inHg (" + str(fcbBotUtils.inhgToHpa(python_obj["altimeter"]["value"])) + \
            " hPa)"

    temp_info = str(python_obj["temperature"]["value"]) + "°" + python_obj["units"]["temperature"]
    dewp_info = str(python_obj["dewpoint"]["value"]) + "°" + python_obj["units"]["temperature"]

    embed = discord.Embed(title="Information for " + \
        python_airportInfo["name"] + " (" + icao_code.upper() + ")\nissued " + cur_date + " at " + cur_time)
    embed.add_field(name="metar", value=raw_metar, inline=False)
    embed.add_field(name="wind information", value=wind_info, inline=False)
    embed.add_field(name="pressure", value=pressure_info)
    embed.add_field(name="temperatur", value=temp_info)
    embed.add_field(name="dewpoint", value=dewp_info)


    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(DISCORD_TOKEN)


