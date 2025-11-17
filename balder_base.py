import json
import balder_items

    
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class Base() :
    
    ws = None # Base.ws

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
        if Base.ws :
            await self.ws.send( json.dumps({ 'op':op, 'data':data }) )
            
# ----------------------------------------------------------------------
    async def send_replace( self, elem, code ): 
        await self.send( "replace",  {"element": f'{elem}', "html": code } )

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
        pass



