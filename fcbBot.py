# fcbBot.py

import os
import json
import discord
import logging
import discord
import fcbBotUtils

from urllib.request import Request, urlopen

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

@bot.command(name='hallo', help='Respone with hello')
async def nine_nine(ctx):
    response = f'Hallo'
    await ctx.send(response)

@bot.command(name='metar', help='get metar information for icao airport')
async def metar(ctx, icao_code: str):

    if len(icao_code) != 4:
        await ctx.send("" + icao_code + " is not a valid icao code")
        return

    request = Request('https://avwx.rest/api/metar/' +  icao_code.lower(), headers=avwx_headers)
    response_body = urlopen(request).read()

    python_obj = json.loads(response_body)
    raw_metar = python_obj["raw"]
    print("metar : " + raw_metar)
    print(response_body)
    
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

    embed = discord.Embed(title="Information for " + icao_code.upper())
    embed.add_field(name="metar", value=raw_metar, inline=False)
    embed.add_field(name="wind information", value=wind_info, inline=False)
    embed.add_field(name="pressure", value=pressure_info)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(DISCORD_TOKEN)


#{"meta":{"timestamp":"2020-05-27T12:30:39.335959Z",
#"stations_updated":"2019-05-21",
#"cache-timestamp":"2020-05-27T12:30:33.547000Z"},
#"altimeter":{"repr":"Q1032","value":1032,"spoken":"one zero three two"},
#"clouds":[],"flight_rules":"VFR","other":[],
#"sanitized":"EDDS 271220Z VRB04KT CAVOK 20/05 Q1032 NOSIG",
#"visibility":{"repr":"CAVOK","value":9999,"spoken":"ceiling and visibility ok"},
#"wind_direction":{"repr":"VRB","value":null,"spoken":"variable"},
#"wind_gust":null,"wind_speed":{"repr":"04","value":4,"spoken":"four"},
#"wx_codes":[],"raw":"EDDS 271220Z VRB04KT CAVOK 20/05 Q1032 NOSIG",
#"station":"EDDS","time":{"repr":"271220Z","dt":"2020-05-27T12:20:00Z"},
#"remarks":"NOSIG","dewpoint":{"repr":"05","value":5,"spoken":"five"},
#"remarks_info":{"dewpoint_decimal":null,"temperature_decimal":null},
#"runway_visibility":[],"temperature":{"repr":"20","value":20,"spoken":"two zero"},
#"wind_variable_direction":[],
#"units":{"altimeter":"hPa","altitude":"ft","temperature":"C","visibility":"m",
#"wind_speed":"kt"}}

#b'{"meta":{"timestamp":"2020-05-28T13:57:37.561124Z","stations_updated":"2019-05-21","cache-timestamp":"2020-05-28T13:56:42.424000Z"},"altimeter":{"repr":"A3009","value":30.09,"spoken":"three zero point zero nine"},"clouds":[{"repr":"FEW023","type":"FEW","altitude":23,"modifier":null,"direction":null},{"repr":"FEW070","type":"FEW","altitude":70,"modifier":null,"direction":null},{"repr":"SCT250","type":"SCT","altitude":250,"modifier":null,"direction":null}],"flight_rules":"VFR","other":[],"sanitized":"KMIA 281353Z 12009KT 10SM FEW023 FEW070 SCT250 29/24 A3009 RMK AO2 SLP188 T02890239","visibility":{"repr":"10","value":10,"spoken":"one zero"},"wind_direction":{"repr":"120","value":120,"spoken":"one two zero"},"wind_gust":null,"wind_speed":{"repr":"09","value":9,"spoken":"nine"},"wx_codes":[],"raw":"KMIA 281353Z 12009KT 10SM FEW023 FEW070 SCT250 29/24 A3009 RMK AO2 SLP188 T02890239","station":"KMIA","time":{"repr":"281353Z","dt":"2020-05-28T13:53:00Z"},"remarks":"RMK AO2 SLP188 T02890239","dewpoint":{"repr":"24","value":24,"spoken":"two four"},"remarks_info":{"dewpoint_decimal":{"repr":"23.9","value":23.9,"spoken":"two three point nine"},"temperature_decimal":{"repr":"28.9","value":28.9,"spoken":"two eight point nine"}},"runway_visibility":[],"temperature":{"repr":"29","value":29,"spoken":"two nine"},"wind_variable_direction":[],
#"units":{"altimeter":"inHg","altitude":"ft","temperature":"C","visibility":"sm","wind_speed":"kt"}}'


