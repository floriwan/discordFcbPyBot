
from urllib.request import Request, urlopen
import fcbBotUtils

print(fcbBotUtils.knotsToKmh(15))

print(fcbBotUtils.knotsToKmh(None))

print(fcbBotUtils.hPaToInHg(1012))
print(fcbBotUtils.degToDir(90))


#avwx_headers = {
#  'Authorization': '2bl1MQ7zDlim-Bxzq53-zUEYSszYfXda2irMb2llkGQ'
#}
#
#request = Request('https://avwx.rest/api/metar/edds', headers=avwx_headers)
#response_body = urlopen(request).read()
#print(response_body)
