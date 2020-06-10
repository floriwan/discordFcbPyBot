# utils.py

import math
import os.path
import time
from urllib.request import URLError, HTTPError, Request, urlopen

IVAO_STATUS_FILE = 'ivao_status.txt'
IVAO_WHAZZUP_FILE = 'ivao_whazzup.txt'
ivaoWhazzup = ''

def getDeparture(icaoCode, departure=True):

    resultArray = []

    for line in str(ivaoWhazzup).split('\n'):
        split_line = line.split(':')

        try:
            if departure:
                check_code = split_line[11] # departure
            else:
                check_code = split_line[13] # arrival

            if check_code == icaoCode:

                if departure:
                    resultArray.append("**" + "{:<9}".format(split_line[0]) + "**" + \
                        split_line[13] + "   " + 
                        split_line[22][:2] + ":" + split_line[22][2:] + " UTC")
                else:
                    resultArray.append("**" + "{:<9}".format(split_line[0]) + "**" + \
                        split_line[11] + "   " + 
                        split_line[22][:2] + ":" + split_line[22][2:] + " UTC")

        except IndexError:
            pass
            #print("ignore line : " + line)

    return resultArray

def updateIvao():

    global ivaoWhazzup
    
    ivaoWhazzupUrl = getIvaoWhazappUrl()
    print("ivao whazzup url: " + str(ivaoWhazzupUrl))

    if ivaoWhazzupUrl == '':
        print ("no valid ivao whazzup url found, abort ...")
        return

    ivaoWhazzup = requestIvaoWhazzupFile(ivaoWhazzupUrl)

    #print(ivaoWhazzup)

def requestIvaoWhazzupFile(ivao_whazzp_url):
    user_agent = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    request = Request(ivao_whazzp_url, headers={'User-Agent': user_agent})

    try:
        response = urlopen(request)
        response_content = response.read()
    except HTTPError as e:
        print ("ivao status request error: " + str(e.getcode()))


    return response_content.decode('ISO-8859-1')


def getIvaoWhazappUrl():

    if is_file_older_than_days(IVAO_STATUS_FILE, 30):
        requestIvaoStatusFile('http://www.ivao.aero/whazzup/status.txt')
    
    print("read ivao status file: " + IVAO_STATUS_FILE)
    with open(IVAO_STATUS_FILE, 'r') as content_file:
        content = content_file.read()

    for line in content.split('\n'):
        if line.startswith('url0'):
            return line.split('=')[1]
    
    return ''

def requestIvaoStatusFile(ivao_status_url):
    user_agent = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    request = Request(ivao_status_url, headers={'User-Agent': user_agent})

    print("request ivao status: " + ivao_status_url)

    try:
        response = urlopen(request)
        response_content = response.read().decode('utf-8')

        ivao_status_file = open(IVAO_STATUS_FILE,'w')
        print("write ivao status file:" + IVAO_STATUS_FILE)
        ivao_status_file.write(response_content)
 
    except HTTPError as e:
        print ("ivao status request error: " + str(e.getcode()))

def is_file_older_than_days(file, days=1): 
    file_time = os.path.getmtime(file) 
    # Check against 24 hours 
    if (time.time() - file_time) / 3600 > 24*days: 
        return True
    else: 
        return False

def knotsToKmh(knots):
    if knots is None: return 0
    return round(knots * 1.852, 2)

def degToDir(degrees):
    if degrees is None: return "UNKNOWN"
    dirIndex = math.floor((degrees / 22.5) + 0.5)
    dirArr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
    return dirArr[(dirIndex % 16)]

def hPaToInHg(hpa):
    if hpa is None: return 0
    return round((hpa * 0.030), 2)

def inhgToHpa(inhg):
    if inhg is None: return 0
    return round((inhg * 33.7685))

