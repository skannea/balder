import machine
#from arduino_alvik import ArduinoAlvik
import asyncio
import log
import os
from balder_base import Base
from balder_exec import Exec

# ----------------------------------------------------------------------
class Com(Base) :
    
# ----------------------------------------------------------------------
    def init( self ):
        asyncio.create_task( self.send_log_task() )
        
        self.exec = Exec( self.levels[1:] ) 
        
    
# ----------------------------------------------------------------------
    async def handle_message( self, msg ):
        
        section = msg.get('section','')
        
        if section == 'file': # file upload request --> start task thet fetches file and writes to disk 
            #asyncio.create_task( self.fetch_task( msg.get('file','') ) )
            file =  msg.get('file','')
            url =  f"{self.config_items.value('resourceurl')}/{file}"
            self.fetch_file( url, file ) 
            return


        if section == 'begin': # a browser has started, awaits sections content
            log.reset() # mark all stored log items as unsent
            await self.send_replace( "log_table", '' ) # clear log table
            self.debug( 'log_table was cleared') 
            # not return 
        
        # if not yet returned, forward to exec  ----->
        await self.exec.forward_message( msg ) 


    async def xxxfetch_task( self, filename ) :
        resp = requests.get( f"{self.config_items.value('resourceurl')}/{filename}" )
        self.debug ( f'Downloading file: z_{filename} size {len(resp.content)} bytes' )
        with open( filename, 'wb') as fd:
            fd.write(resp.content) 
          
            
# ----------------------------------------------------------------------
    def get_page( self, request ): 
    # return HTML page 
        resourceurl = self.config_items.value('resourceurl')
        com_sect = self.levels[0] + '_section'
        exe_sect = self.levels[1] + '_section'
        app_sect = self.levels[2] + '_section'
        log_sect = 'log_section'
        
        return f'''

<!DOCTYPE html>
<head>
  <meta charset="UTF-8">
  <title >Baldur</title>
  <link rel="icon" type="image/x-icon" href="{resourceurl}/balder.svg">
  <link rel="stylesheet" href="{resourceurl}/balder.css">
  
  <script src="{resourceurl}/balder_app.js"></script>
  <script src="{resourceurl}/balder.js"></script>
  
</head>
<body onload="setup();">
   <h1>Balder</h1>

   <div id="sections">
   
    
   {self.supersection_html( com_sect, 'Communication', True, 
        self.standard_sections_html() +
        self.section_html('connection', 'Server Connection', True, 
           '<div id="statusline">---</div><button onclick="reload();">Reload</button>'
        ))}

   {self.supersection_html( exe_sect, 'Execution', False, 
        self.exec.standard_sections_html() +
        self.section_html('files', 'Files', False, self.file_select_html() ))}
   
   {self.supersection_html( app_sect, 'Application', False) }

   {self.section_html( log_sect, 'Log', True, '<div class="logs"><table id="log_table"></table></div>')}

   </div>

</body>
</html>
'''

# ----------------------------------------------------------------------
    def file_select_html(self ) : # [ {file:x.py, desc:blabla}, ... ]
        #return '' # §§
        resp = self.make_request( self.config_items.value('listurl'), {'User-Agent': 'balder'} )
        print( resp.text)
        code = ''
        for file in resp.json()['tree']:
            filename = file['path']
            desc = filename 
            code += f'''
              <div>
                <input class="short" disabled value="{filename}"/>
                <input class="long"  disabled value="{desc}" />
                <button onclick="on_file_click( '{filename}' )">Upload</button>
              </div>'''
        return code

 
   
 

# ----------------------------------------------------------------------
    def config_items_setup( self ): 
        self.config_items.default_name_value('name',   'Namn', 'Balder')
        self.config_items.default_name_value('ssid',   'WiFi', 'Monarki') 
        self.config_items.default_name_value('connect_retries', 'Retries', '5') 
        self.config_items.default_name_value('resourceurl', 'Resource URL', 'https://skannea.github.io/balder')
        self.config_items.default_name_value('listurl', 'List URL', 'https://api.github.com/repos/skannea/balder/git/trees/main')
        self.config_items.default_name_value('pageurl', 'Page URL',  'https://vicker.tplinkdns.com:443/balder/page')
        self.config_items.default_name_value('wsurl', 'WebSocket URL', 'https://vicker.tplinkdns.com:443/balder/ws')
        self.secrets = { 'Monarki': '' } # wifi credentials


# ----------------------------------------------------------------------
    def command_items_setup( self ): 
    
        # user command operations without data

        async def reboot():
            self.debug('reboot command was received - rebooting now')
            await self.disconnect()
            log.end()  # End logging
            os.sync()  # Ensure all changes are written to the filesystem
            await asyncio.sleep(1)  # give time to write file  
            machine.reset()  # Reboot 
            
        self.command_items.set_name_async('reboot', 'Reboot device', reboot )
        
        def lognoD():
            self.loglevel('IE')
        self.command_items.set_name_func('lognod', 'Log level I+E', lognoD )
        
        def lognoI():
            self.loglevel('E')
        self.command_items.set_name_func('lognoi', 'Log level only E', lognoI )


        def logend():
            log.end('balder_log.txt') 
        self.command_items.set_name_func('logend', 'Store log', logend )

        def end():
            log.end('balder_log.txt')
            exit(0) 
        self.command_items.set_name_func('end', 'Exit', end )
    

        def log_debug():
            self.debug( 'A debugtest message')
        self.command_items.set_name_func('log_debug', 'Issue a debug message', log_debug )
        
        def log_info():
            self.info('An info test message')
        self.command_items.set_name_func('log_info', 'Issue an info message', log_info )
        
        def log_error():
            self.error('An error test message')
        self.command_items.set_name_func('log_error', 'Issue an error message', log_error )

        async def log_send():
            await self.log_items_update()
        self.command_items.set_name_async('log_send', 'Send log', log_send )

        
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
    async def send_log_task( self ): 
        while True:
            line = log.line() 
            if line: 
                level = line[0]
                name = line[2:8]
                tim = line[8:27]
                msg   = line[30:]
                html = f'<tr><td>{level}</td><td>{name}</td><td>{tim}</td><td>{msg}</td></tr>' 
                await self.send( "before",  {"element": "log_table", "html": html } )
            await asyncio.sleep(0)

         




