# utils.py

import math

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

