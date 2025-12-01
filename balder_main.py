import asyncio
import log
import network
import asyncio

import sys
import time 

# appending a path for desktop testing
sys.path.append('../External/microdot')

from microdot import Microdot
from microdot.websocket import with_websocket

from balder_com import Com

# main configuration
hostname = 'balder.local' # not working
ssid = 'Monarki'
password = 'hedradittland'
logfile = 'balder_log.txt'
levels =  [        # id:s to be used
'com',  # 0 communication setup and functions
'exec', # 1 executor setup and functions
'app'   # 2 dynamicly selected app, setup and functions
 ]

dot = Microdot()
com = None # will be set in main program


# ----------------------------------------------------------------------
@dot.get('/page')
async def on_page(request):
    return com.get_page(request), 200, {'Content-Type': 'text/html'} 

# ----------------------------------------------------------------------
@dot.route('/ws')
@with_websocket
async def on_ws(request, ws):
    await com.receive( ws ) # loops until disconnect

# ---------------------------------------------------------------------- Main task
async def main_task():
    # start the server in a background task
    await asyncio.create_task( dot.start_server( debug=True) )

# ---------------------------------------------------------------------- Init
def init_wifi_and_log():

    wlan = network.WLAN( )
    wlan.active(True)  # Activate the WLAN interface
    mac = ''.join([f'{b:02X}' for b in wlan.config('mac')]) 
    
    wlan.connect( ssid, password )
    trials = 0
    while not wlan.isconnected():
        time.sleep( 1)
        trials += 1
    
    log.begin(logfile) # enable logging, sync datetime
    log.info( f'Connected to WiFi. {ssid=}, {trials=}', 'main' )
    log.info( f'{network.hostname()=}', 'main' )
    log.info( f'{wlan.ipconfig("addr4")=}', 'main' )
    log.info( f'{mac=}' , 'main' )
    log.info( f'{logfile=}', 'main' )
    
# ---------------------------------------------------------------------- Main program
init_wifi_and_log()
# setup and start tasks for page and websockets
com = Com( levels )
asyncio.run(main_task())
                





