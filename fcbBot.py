# fcbBot.py

import os
import json
import discord
import logging
import discord
import fcbBotUtils

from urllib.request import URLError, HTTPError, Request, urlopen
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
load_dotenv()

AVWX_TOKEN = os.getenv('AVWX_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
IVAO_STATUS_URL = os.getenv('IVAO_STATUS_URL')

avwx_headers = {
  'Authorization': AVWX_TOKEN
}


bot = commands.Bot(command_prefix='!')

def requestTafJson(icao_code):
    request = Request('https://avwx.rest/api/taf/' +  icao_code.lower() + '?options=info,translate,speech', headers=avwx_headers)
    response_body = urlopen(request).read()
    #print(response_body)
    return json.loads(response_body)

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
        print ("chart request error code: " + str(e.getcode()))
        return "no charts available for " + icao_code.upper()
        

@bot.command(name='hallo', help='respone with hello')
async def nine_nine(ctx):
    response = f'Hallo'
    await ctx.send(response)

#@bot.command(name='commands', help='get a list of all bot commands')
#async def commands(ctx):
#    response = f'!metar <icaocode>'
#    await ctx.send(response)

@bot.command(name='ivao', help='responde with arrival and departures')
async def ivao(ctx, icao_code: str):

    if len(icao_code) != 4:
        await ctx.send(icao_code + " is not a valid icao code")

    python_airportInfo = requestAirportInfoJson(icao_code.lower())
    fcbBotUtils.updateIvao()
    arrivalList = fcbBotUtils.getDeparture(icao_code.upper())
    departureList = fcbBotUtils.getDeparture(icao_code.upper(), False)

    print(arrivalList)
    print(departureList)

    embed = discord.Embed(title="IVAO information for " + \
        python_airportInfo["name"] + " (" + icao_code.upper() + ")")

    inboundString = ''
    if len(arrivalList) > 0:
        for flight in arrivalList:
            inboundString += flight + "\n"
    else:
        inboundString = "no flights"

    outboundString = ''
    if len(departureList) > 0:
        for flight in departureList:
            outboundString += flight + "\n"
    else:
        outboundString = "no flights"

    embed.add_field(name="outbound flights", value=inboundString)
    embed.add_field(name="inbound flights", value=outboundString)

    await ctx.send(embed=embed)

@bot.command(name='zulu', help='respond with the zulu time')
async def zulu(ctx):
    utctime = datetime.utcnow()
    await ctx.send("it is " + utctime.strftime("%H") + ":" + utctime.strftime("%M") + "z")

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

@bot.command(name='taf', help='get terminal aerodrome forecast (TAF) for icao airport')
async def taf(ctx, icao_code: str):
    if len(icao_code) != 4:
        await ctx.send("" + icao_code + " is not a valid icao code")
        return
    
    #python_airportInfo = requestAirportInfoJson(icao_code.lower())
    python_obj = requestTafJson(icao_code.lower())
    #print(python_obj)
    raw_taf = python_obj["raw"]
    #print("taf : " + raw_taf)

    embed = discord.Embed(title="TAF Information for " + \
        python_obj["info"]["name"] + " (" + icao_code.upper() + ")")

    
    report_string = "**Time:** " + python_obj["time"]["dt"].replace('T', ' ') + "\n" + \
        "**Report:** " + python_obj["speech"]

    embed.add_field(name="raw taf", value=python_obj["raw"], inline=False)
    embed.add_field(name="Report", value=report_string, inline=False)
    await ctx.send(embed=embed)

@bot.command(name='metar', help='get meteorological aerodrome report (METAR) for icao airport')
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
    embed.add_field(name="raw metar", value=raw_metar, inline=False)
    embed.add_field(name="wind information", value=wind_info, inline=False)
    embed.add_field(name="pressure", value=pressure_info)
    embed.add_field(name="temperatur", value=temp_info)
    embed.add_field(name="dewpoint", value=dewp_info)


    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(DISCORD_TOKEN)


