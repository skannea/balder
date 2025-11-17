import asyncio
from balder_base import Base
from balder_exec import Exec

# ----------------------------------------------------------------------
class Com(Base) :
    
# ----------------------------------------------------------------------
    def init( self ): 
        asyncio.create_task( self.task(3) )
        
        self.exec = Exec('exec')
        self.log_items = []
    
# ----------------------------------------------------------------------
    async def handle_message( self, msg ):
        section = msg['section'] 

        if section == 'server_files' : 
            print( f'Filename: {msg['key']}   Size: { len(msg['value'])} bytes' )
            return


        # { section:command_items, key:commandkey  }

        if section == f'{self.name}_command_items' : 
            await self.command_items.run( msg )
            return
                    
         # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        elif section ==  f'{self.name}_config_items' :
            self.config_items.action(  msg )
            return
        elif msg.get('key','') == 'begin': # browser has started, awaits sections content
            await self.standard_sections_update()
            
        # if not yet returned, forward to exec  ----->
        await self.exec.handle_message( msg ) 
            

            
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

   {self.section_html('com_section', '----- Communication --------', False, self.standard_sections_html()) }
   {self.section_html('exe_section', '----- Execution ------------', False, self.exec.standard_sections_html()) }
   
   {self.section_html('app_section', '----- Application ----------', False) }

   {self.section_html('log_items', 'Log', True, '<div class="logs"><table id="log_table"></table></div>')}

   </div>

</body>
</html>
'''


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

        self.secrets = { 'Monarki': '' } # wifi credentials

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

        
        self.exec.command_items_setup( )   # ---->

# ----------------------------------------------------------------------
    def state_items_setup( self ): 
 
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
 
# ----------------------------------------------------------------------
    def xxstart_tasks( self  ): 
        asyncio.create_task( self.task(3) )
        asyncio.create_task( self.exec.task(4) )




