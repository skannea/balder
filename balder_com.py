import asyncio
import base64

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

        if await self.handle_command_message( msg ):
            return
        if await self.handle_config_message( msg ):
            return
        
        section = msg.get('section','')
        if section == 'files': # file list update
            filelist = msg.get('filelist',[])
            print ('Received file list:', filelist) 
            await self.send_replace( 'files', self.file_select_html( filelist ) )
            return

        if section == 'file': # file upload
            file = msg.get('file',[])
            content = (base64.b64decode(msg.get('content','')))
            print ('Received file:', file) 
            print ('Received bytes:', len(content)) 
            with open( 'y'+file, 'wb') as f:
                f.write( content ) 
            return
# note ubinascii.a2b_base64(data)


        if section == 'begin': # browser has started, awaits sections content
            await self.standard_sections_update()
            # not return 
        
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
  <link rel="icon" type="image/x-icon" href="{self.config_items.value('resourceurl')}/balder.svg">
  <link rel="stylesheet" href="{self.config_items.value('resourceurl')}/balder.css?x=3">
  
  <script src="{self.config_items.value('resourceurl')}/balder_list.js"></script>
  <script src="{self.config_items.value('resourceurl')}/balder.js?x=29"></script>
  
</head>
<body onload="setup( '{self.config_items.value('wsurl')}' );">
   <h1>Balder</h1>

   <div id="sections">
   
   {self.section_html('connection', 'Server Connection', True, 
   '<div id="statusline">---</div><button onclick="reload();">Reload</button>'
   )} 

   {self.section_html('files', 'Files')}
    
   {self.supersection_html('com_section', '----- Communication --------', False, self.standard_sections_html()) }
   {self.supersection_html('exe_section', '----- Execution ------------', False, self.exec.standard_sections_html()) }
   
   {self.supersection_html('app_section', '----- Application ----------', False) }

   {self.section_html('log_items', 'Log', True, '<div class="logs"><table id="log_table"></table></div>')}

   </div>

</body>
</html>
'''

# ----------------------------------------------------------------------
    def file_select_html(self, filelist ) : # [ {file:x.py, desc:blabla}, ... ]
        code = ''
        for f in filelist:
            file = f['file']
            desc = f['desc']
            code += f'''
              <div>
                <input class="short" disabled value="{file}"/>
                <input class="long"  disabled value="{desc}" />
                <button onclick="on_file_click( '{file}' )">Upload</button>
              </div>'''
        return code

   
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
    def xselect_file_html(self):       
        return f'''<input type="file" onchange="on_file_select(this)">'''
    

# ----------------------------------------------------------------------
    def config_items_setup( self ): 
        # read from file
        self.config_items.set_name_value('name',   'Namn', 'Balder')
        self.config_items.set_name_value('ssid',   'WiFi', 'Monarki') 
        self.config_items.set_name_value('connect_retries', 'Retries', '5') 
        self.config_items.set_name_value('resourceurl', 'Resource URL', 'https://skannea.github.io/balder')
        self.config_items.set_name_value('pageurl', 'Page URL',  'https://vicker.tplinkdns.com:443/balder/page')
        self.config_items.set_name_value('wsurl', 'WebSocket URL', 'https://vicker.tplinkdns.com:443/balder/ws')
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




