import asyncio
import json
import items
#import log

#  så att det fungerar på PC
# importing module
import sys
# appending a path
sys.path.append('../External/microdot')



from microdot import Microdot
from microdot.websocket import with_websocket
#from balder_app import App

# dot - Microdot - server functions
# com - Com - communication setup and functions
# exe - Exec - executor setup and functions
# app - App - dynamicly selected app, setup and functions
# ---  Base - base class for Com Exec App


dot = Microdot()

speed = 345
array = [12,34,56,78,90]
state = 'running' 

# ----------------------------------------------------------------------
@dot.get('/page')
async def on_page(request):
    return com.get_page(request), 200, {'Content-Type': 'text/html'} 


@dot.route('/ws')
@with_websocket
async def on_ws(request, ws):
    await com.receive( ws ) # loops until disconnect

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class ConfigItems( items.ConfigItems ):

# ----------------------------------------------------------------------
    def html(self, id ):
        code = ''
        for key in self.iter():
            code += f'''
              <div id="{key}">
                <input class="short" disabled value="{self.name(key)}"/>
                <input class="long" type="text" value="{self.value(key)}" />
                <button onclick="to_server( '{id}', this, 'save'   )">Save</button>
                <button onclick="to_server( '{id}', this, 'remove' )">Remove</button>
              </div>'''
        return code
    
# ----------------------------------------------------------------------
    def action( self, msg):
        button = msg.get('button','')
        key = msg.get('key','')
        if button == 'save':
            self.set_value( key, msg.get('value',''))
        if button == 'remove':
            self.remove( key )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class CommandItems( items.CommandItems ):

# ----------------------------------------------------------------------
    def html( self, id='' ):
        code = ''
        for key in self.iter():
                code += f'''<button class="long" onclick="to_server( '{id}', '{key}')">{self.name(key)}</button><br>'''
        return code        

# ----------------------------------------------------------------------
    async def run( self, msg ):
        key = msg.get('key','')
        if self.isasync(key):
            print('await')
            await self.func(key)()
        else:    
            print('direct')
            self.func( key )()

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class StateItems( items.StateItems ):

# ----------------------------------------------------------------------
    def html(self, id=''):
        self.evaluate_all()
        
        code = ''
        for key in self.iter():
                code +=  f'''<input class="short" disabled value="{self.name(key)}"/>
                            <input class="long" type="text" value="{self.value(key)}"/><br>'''
        return code
    
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class Base() :
    
    ws = None # Base.ws

 # ----------------------------------------------------------------------
    def config_items_setup( self ): 
        pass

# ----------------------------------------------------------------------
    def command_items_setup( self ): 
        pass

# ----------------------------------------------------------------------
    def state_items_setup( self ): 
        pass

# ----------------------------------------------------------------------
    def sections_html( self, id ): 
        return ''

# ----------------------------------------------------------------------
    async def send( self, op, data ): 
        if Base.ws :
            print('send')
            await self.ws.send( json.dumps({ 'op':op, 'data':data }) )
            print('after send')

# ----------------------------------------------------------------------
    async def receive( self, ws ): 
        Base.ws = ws
        while True:
            try:
                msg = json.loads(await ws.receive()) # wait for message
                print( msg )
            except Exception as ex:
                print( ex )
                break
            
            await self.handle_message( msg )

# ----------------------------------------------------------------------
    async def handle_message( self, msg ): 
        return

# ----------------------------------------------------------------------
    async def send_replace( self, elem, code ): 
        await self.send( "replace",  {"element": elem, "html": code } )


# ----------------------------------------------------------------------
class Com(Base) :

    
# ----------------------------------------------------------------------
    def __init__( self ): 
        
        self.exe = Exec()

        self.config_items = ConfigItems()
        self.config_items_setup()        
        self.command_items = CommandItems()
        self.command_items_setup()  
        self.state_items = StateItems()
        self.state_items_setup()
    
        self.log_items = []

# ----------------------------------------------------------------------
    async def handle_message( self, msg ):
        section = msg['section'] 

        if section == 'server_files' : 
            print( f'Filename: {msg['key']}   Size: { len(msg['value'])} bytes' )
            return


        # { section:command_items, key:commandkey  }


        if section == 'command_items' : 
            await self.command_items.run( msg )
            return
                    
         # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        elif section ==  'config_items' :
            self.config_items.action(  msg )
            return
        elif msg.get('key','') == 'begin': # browser has started, awaits sections content
            await self.send_replace( 'config_items', self.config_items.html('config_items') )
            await self.send_replace( 'command_items', self.command_items.html('command_items') )
            await self.send_replace( 'state_items', self.state_items.html('state_items') )
        # if not yet returned, forward to exec  ----->
        await self.exe.handle_message( msg ) 
            

            
# ----------------------------------------------------------------------
    def get_page( self, request ): 
    # return HTML page 
        return f'''

<!DOCTYPE html>
<head>
  <meta charset="UTF-8">
  <title >Balder</title>
  <link rel="icon" type="image/x-icon" href="https://skannea.github.io/balder/balder.svg">
  <link rel="stylesheet" href="https://skannea.github.io/balder/balder.css?x=23">
  
  <script src="https://skannea.github.io/balder/balder.js?x=25"></script>
  
</head>
<body onload="setup( 'wss://blue.skannea.duckdns.org:443/ws' );">
   <h1>Balder</h1>

   <div id="sections">
   
   {self.section_html('connection', 'Server Connection', True, 
   '<div id="statusline">---</div><button onclick="reload();">Reload</button>'
   )} 

   {self.section_html('server_files', 'Server Files', False, self.select_file_html() )}
    
   {self.section_html('device_files', 'Device Files')}
    
   {self.section_html('config_items', 'Configuration')}

   {self.section_html('command_items', 'Commands')}
 
   {self.section_html('state_items', 'States')}

   {self.section_html('exe_config_items', 'Exec Configuration')}
   
   {self.section_html('exe_command_items', 'Exec Commands')}

   {self.section_html('exe_state_items', 'Exec States')}

   {self.section_html('app_orientation', 'App Orientation')}

   {self.section_html('app_config_items', 'App Configuration')}
   
   {self.section_html('app_command_items', 'App Commands')}

   {self.section_html('app_state_items', 'App States')}

   {self.section_html('log_items', 'Log', True, '<div class="logs"><table id="log_table"></table></div>')}

   </div>

</body>
</html>
'''

# ----------------------------------------------------------------------
    def section_html(self, id, text, show=False, content=''):       
        """
        Generates  HTML for toggling div
        """
        return f'''<button class="section" onclick="showhide('{id}')">{text}</button><br>
        <div id="{id}" style="display:{ 'block' if show else 'none'}">
        {content}
        </div>'''


# ----------------------------------------------------------------------
    def xselect_file_html(self):       
        """
        Generates  HTML for file selection
        """
        return f'''<form action="javascript:;" onsubmit="logger( getElementById('sfile').value );">
                   <label for="sfile">Select a file:</label>
                   <input type="file" id="sfile" name="sfile"><br>
                   <input type="submit">
                   </form>'''

# ----------------------------------------------------------------------
    def select_file_html(self):       
        return f'''<input type="file" onchange="on_file_select(this)">'''


 # ----------------------------------------------------------------------
    def config_items_setup( self ): 
        # read from file
        self.config_items.set_name_value('name',   'Namn', 'Balder')
        self.config_items.set_name_value('ssid',   'WiFi', 'Monarki') 
        self.config_items.set_name_value('connect_retries', 'Retries', '5') 
        self.config_items.set_name_value('serverproto', 'http/s', 'http')
        self.config_items.set_name_value('serverhost', 'Host', 'lothar.local')

        self.secrets = { 'Monarki': 'hedradittland' } # wifi credentials


    # ----------------------------------------------------------------------
    def command_items_setup( self ): 
    
        # user command operations without data

        def reboot():
            print('Reboot command was received.')
            #log.end()  # End logging
            #os.sync()  # Ensure all changes are written to the filesystem
            #machine.reset()  # Reboot 
        self.command_items.set_name_func('reboot', 'Reboot device', reboot )
        
        def log_debug():
            self.log_items_add( 'D', 'A debug message')
        self.command_items.set_name_func('log_debug', 'Issue a debug message', log_debug )
        
        def log_info():
            self.log_items_add('I', 'An info message')
        self.command_items.set_name_func('log_info', 'Issue an info message', log_info )
        
        def log_error():
            self.log_items_add('E', 'An error message')
        self.command_items.set_name_func('log_error', 'Issue an error message', log_error )

        async def log_send():
            await self.log_items_send()
            self.log_items_clear() 
        self.command_items.set_name_async('log_send', 'Send and clear log', log_send )

        async def update_states():
            await self.send_replace( 'state_items', self.state_items.html( 'state_items'))
        self.command_items.set_name_async('updstates', 'Update states', update_states )

        def change_states():
            global speed, array, state
            speed = 456
            state = 'stopping'
        self.command_items.set_name_func('chgstates', 'Change states', change_states )

        
        self.exe.command_items_setup( )   # ---->

# ----------------------------------------------------------------------
    def state_items_setup( self ): 
 
        self.state_items.set_name_func( 'simple', 'Simple integer', lambda : f'{speed} km/h' )
        self.state_items.set_name_func( 'array', 'List of numbers', lambda : f'{array}' )
        self.state_items.set_name_func( 'state', 'Current state', lambda : state )
        def listcommands():
            s = ''
            v = self.command_items
            for key in v.iter():
                s += f'<{v.name(key)}>  ' 
            return s    
        self.state_items.set_name_func( 'coms', 'Commands', listcommands )
         
# ----------------------------------------------------------------------
    def log_items_add(self , level, msg ):
        self.log_items.append( f'<tr><td>{level}</td><td>{msg}</td></tr>' )

# ----------------------------------------------------------------------
    def log_items_clear(self ):
        self.log_items.clear()

# ----------------------------------------------------------------------
    def log_items_html(self ):
        """
        Generates  HTML for log items 
        """
        code = "".join( reversed( self.log_items ) )
        return code


# ----------------------------------------------------------------------
    async def log_items_send( self ): 
        await self.send( "before", {"element":"log_table", 'html': self.log_items_html() }) 
 

            

# ----------------------------------------------------------------------------------------------    
class Exec(Base):

# ----------------------------------------------------------------------
    def __init__( self ): 
        
        self.orientation_changes = 0
        self.alpha = 0
        self.beta = 0
        self.gamma = 0

  
        #self.config_items = ConfigItems()
        #self.config_items_setup()        
        self.command_items = CommandItems()
        self.command_items_setup()  
        
        #self.state_items = StateItems()
        #self.state_items_setup()

        self.failure  = asyncio.Event()   # event variable that is set when an app error occurs
        self.resume   = asyncio.Event()   # event variable that is set to resume app exeution
        self.fallback = False
        self.auto = False
        self.app = None


# ----------------------------------------------------------------------
    async def handle_message( self, msg ): 
        section = msg['section']
        # { section:command_items, key:commandkey  }
        if section == 'exe_command_items' : 
            await self.command_items.run(  msg )
            return
        # { section:'orientation', alpha:int, beta:int, gamma:int  }
        if section == 'app_orientation' : 
            self.orientation_changes += 1
            self.alpha = msg.get('alpha',0)
            self.beta  = msg.get('beta',0)
            self.gamma = msg.get('gamma',0) 
            html = f'''Riktning: {self.alpha} grader<br>
                       Lutning: {self.beta} grader<br>
                       Rotation: {self.gamma} grader<br>
                       Antal: {self.orientation_changes}'''
    
            await self.send_replace( 'app_orientation', html)
            return
                    
         # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        elif section ==  'config_items' :
            self.config_items.action( msg )
            return
        elif msg.get('key','') == 'begin': # browser has started, awaits sections content
            #await self.send_replace( 'exe_config_items', self.config_items.html() )
            await self.send_replace( 'exe_command_items', self.command_items.html('exe_command_items') )
            #await self.send_replace( 'exe_state_items', self.state_items.html() )
        # if not yet returned, forward to app  ----->
        if self.app: 
            await self.app.handle_message( msg ) 
                
# ----------------------------------------------------------------------
    def command_items_setup( self  ): 
        
        #async def update_states():
        #    await self.send_replace( 'state_items', self.state_items.html( 'state_items'))
        #self.command_items.set_name_async('xupdstates', 'Update states', update_states )

        def f(): self.fallback = False
        self.command_items.set_name_func('fb0', 'Normal mode', f )    
            
        def f(): self.fallback = True
        self.command_items.set_name_func('fb1', 'Fallback mode', f )    
        
        def f(): self.auto = False
        self.command_items.set_name_func('auto0', 'Manual mode', f )    
            
        def f(): self.auto = True
        self.command_items.set_name_func('auto1', 'Auto mode', f )    
             
        def f(): self.resume.clear()
        self.command_items.set_name_func('res0', 'Hold', f )    
            
        def f(): self.resume.set()
        self.command_items.set_name_func('res1', 'Resume', f )    
             
        def f(): self.failure.clear()
        self.command_items.set_name_func('fail0', '(Fail clear)', f )    
            
        def f(): self.failure.set()
        self.command_items.set_name_func('fail1', '(Fail set)', f )    


com = Com()

async def main():

    # start the server in a background task

    await asyncio.create_task(dot.start_server( debug=True))

    # ... do other asynchronous work here ...

    # cleanup before ending the application
    print('end')
asyncio.run(main())



