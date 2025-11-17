import asyncio
#  så att det fungerar på PC
# importing module
import sys
# appending a path
sys.path.append('../External/microdot')

from microdot import Microdot
from microdot.websocket import with_websocket

# dot - Microdot - server functions
# com - Com - communication setup and functions
# exe - Exec - executor setup and functions
# app - App - dynamicly selected app, setup and functions
# ---  Base - base class for Com Exec App

from balder_com  import Com

dot = Microdot()
com = None # will be set in main()


# ----------------------------------------------------------------------
@dot.get('/page')
async def on_page(request):
    return com.get_page(request), 200, {'Content-Type': 'text/html'} 

# ----------------------------------------------------------------------
@dot.route('/ws')
@with_websocket
async def on_ws(request, ws):
    await com.receive( ws ) # loops until disconnect

# ----------------------------------------------------------------------
async def main():
    global com
    # setup and start tasks for page and websockets
    com = Com('com')
    # start the server in a background task
    await asyncio.create_task( dot.start_server( debug=True) )

# ----------------------------------------------------------------------
asyncio.run(main())



