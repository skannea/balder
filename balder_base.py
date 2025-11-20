import asyncio
import json
import balder_items

    
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class Base() :
    
    ws = None # Base.ws
    wslist = [] 

# ----------------------------------------------------------------------
# not to be overridden, use init instead

    def __init__( self, name='NONAME' ): 
        self.name = name # to be used as prefix in HTML section element IDs
        self.init()
        self.config_items = balder_items.ConfigItems()
        self.config_items_setup()        
        self.command_items = balder_items.CommandItems()
        self.command_items_setup()  
        self.state_items = balder_items.StateItems()
        self.state_items_setup()
    
# ----------------------------------------------------------------------
    def init( self ): 
        pass

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
    def section_html(self, id, text, show=False, content=''):       
        """
        Generates  HTML for toggling (hide/show) section div. 
        - section id 
        - button text
        - show: if True, section is shown initially
        - content: HTML content of section
        """
        return f'''<button class="section" onclick="showhide('{id}')">{text}</button><br>
        <div id="{id}" style="display:{ 'block' if show else 'none'}">
        {content}
        </div>'''

# ----------------------------------------------------------------------
    def standard_sections_html( self ): 
        ''' return HTML code for all three sections: config, command, state '''
        config_items = f'{self.name}_config_items'
        command_items = f'{self.name}_command_items'
        state_items   = f'{self.name}_state_items'
        return f'''
           {self.section_html(config_items, 'Configuration')}
           {self.section_html(command_items, 'Commands')}
           {self.section_html(state_items, 'States')}  '''      

# ----------------------------------------------------------------------
    async def standard_sections_update( self ): 
        ''' send replace messages for all three sections: config, command, state '''
        section = f'{self.name}_config_items'
        await self.send_replace( section, self.config_items.html(section) )
        section = f'{self.name}_command_items'
        await self.send_replace( section, self.command_items.html(section) )
        section = f'{self.name}_state_items'
        print(f'state update section: {section}')
        await self.send_replace( section, self.state_items.html(section) )

# ----------------------------------------------------------------------
    async def send( self, op, data={} ): 
        for ws in Base.wslist:
            try:
                await ws.send( json.dumps({ 'op':op, 'data':data, 'name':self.name }) )
            except Exception as ex:
                print( ex )
                Base.wslist.remove( ws )    
            
            
# ----------------------------------------------------------------------
    async def send_replace( self, elem, code ): 
        await self.send( "replace",  {"element": f'{elem}', "html": code } )

# ----------------------------------------------------------------------
    async def receive( self, ws ): 
        Base.wslist.append(ws)
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
        #if self.handle_command_message( msg ):
        #    return
        #if self.handle_config_message( msg ):
        #   return
        pass

# ----------------------------------------------------------------------
    async def handle_config_message( self, msg ):
        section = msg['section'] 
         # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        if section !=  f'{self.name}_config_items' :
            return False
        button = msg.get('button','')
        key = msg.get('key','')
        if button == 'save':
            self.config_items.set_value( key, msg.get('value',''))
        if button == 'remove':
            self.config_items.remove( key )
        return True

# ----------------------------------------------------------------------
    async def handle_command_message( self, msg ):
        section = msg['section'] 
         # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        if section != f'{self.name}_command_items' : 
            return False
        key = msg.get('key','')
        if self.command_items.isasync(key):
            print('await')
            await self.command_items.func(key)()
        else:    
            print('direct')
            self.command_items.func( key )()
        return True


# ----------------------------------------------------------------------
    async def task( self, pause = 5 ): 
        '''dummy task to be overridden'''
        while True:
            await asyncio.sleep(pause)
            print( f'{self.name} heartbeat')

# ----------------------------------------------------------------------
    def start_tasks( self  ): 
        asyncio.create_task( self.task() )


