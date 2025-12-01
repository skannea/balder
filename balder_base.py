import asyncio
import requests
import json
import items
import log



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class Base() :
    wslist = [] 

    # ----------------------------------------------------------------------
# not to be overridden, use init instead

    def __init__( self, levels ): 
        self.levels = levels 
        self.name = self.levels[0] # to be used as prefix in HTML section element IDs
        
        self.loglevel('DIE')
        self.init()

        self.config_items = items.ConfigItems()
        self.config_items.retrieve( f'{self.name}_config.json' )
        self.config_items_setup()   # set default     
        self.config_items.store(    f'{self.name}_config.json' )
        
        self.command_items = items.CommandItems()
        self.command_items_setup()  
        
        self.state_items = items.StateItems()
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
    def supersection_html(self, id, text, show=False, content=''):       
        """
        Like section but for supersection
        """
        return f'''<button class="supersection" onclick="showhide('{id}')">{text}</button><br>
        <div id="{id}" style="display:{ 'block' if show else 'none'}">
        {content}
        </div>'''


# ----------------------------------------------------------------------
    def standard_sections_html( self ): 
        ''' return HTML code for all three sections: config, command, state ... when required '''
        s=''
        if self.overrides(self, 'config_items_setup') :
            s+=self.section_html(f'{self.name}_config_items' , 'Configuration')+'\n'
        if self.overrides(self, 'command_items_setup') :
            s+=self.section_html(f'{self.name}_command_items', 'Commands')+'\n'
        if self.overrides(self, 'state_items_setup') :
            s+=self.section_html(f'{self.name}_state_items'  , 'States')+'\n'
        return s
    


# ----------------------------------------------------------------------
    async def standard_sections_update( self ): 
        ''' send replace messages for all three sections: config, command, state '''
        self.debug(f'standard_sections_update {self.name}'   )
        await self.config_section_update()
        await self.command_section_update()
        await self.state_section_update()
       
# ----------------------------------------------------------------------
    async def config_section_update( self ): 
        section = f'{self.name}_config_items'
        items = self.config_items
        code = ''
        for key in items.iter():
            code += f'''
              <div id="{key}">
                <input class="short" disabled value="{items.name(key)}"/>
                <input class="long" type="text" value="{items.value(key)}" />
                <button onclick="on_config_click( '{section}', this, 'save'   )">Save</button>
                <button onclick="on_config_click( '{section}', this, 'remove' )">Remove</button>
              </div>'''
        await self.send_replace( section, code )

 # ----------------------------------------------------------------------
    async def command_section_update( self ): 
        section = f'{self.name}_command_items'
        items = self.command_items
        code = ''
        for key in items.iter():
            code += f'''<button class="long" onclick="on_command_click( '{section}', '{key}')">{ items.name(key) }</button><br>'''
        await self.send_replace( section, code )
        
# ----------------------------------------------------------------------
    async def state_section_update( self ): 
        section = f'{self.name}_state_items'
        items = self.state_items
        items.evaluate_all()
        code = f'''<button onclick="on_command_click( '{section}', 'update')">{ 'Update' }</button><br>'''
        for key in items.iter():
                code +=  f'''<input class="short" disabled value="{items.name(key)}"/>
                            <input class="long" disabled type="text" value="{items.value(key)}"/><br>'''
        await self.send_replace( section, code )

# ----------------------------------------------------------------------
    async def send( self, op, data={} ): 
        for ws in Base.wslist:
            try:
                await ws.send( json.dumps({ 'op':op, 'data':data, 'name':self.name }) )
            except Exception as ex:
                self.error( f'send exception: {ex}' )
                Base.wslist.remove( ws )    
            
# ----------------------------------------------------------------------
    async def disconnect( self): 
        for ws in Base.wslist:
            try:
                await ws.close() 

            except Exception as ex:
                print( f'disconnect exception: {ex}' )
                pass
             
# ----------------------------------------------------------------------
    async def send_replace( self, elem, code ): 
        await self.send( "replace",  {"element": f'{elem}', "html": code } )

# ----------------------------------------------------------------------
    async def receive( self, ws ): 
        Base.wslist.append(ws)
        self.debug( f'receive, clients: {len(Base.wslist)}' )
        while True:
            try:
                msg = json.loads(await ws.receive()) # wait for message
                #self.debug( msg )
            except Exception as ex:
                self.error( f'receive exception: {ex}' )
                Base.wslist.remove( ws )    
                break
            
            await self.forward_message( msg )

# ----------------------------------------------------------------------
    def make_request( self, requesturl, headers = {} ) :
        return requests.get( requesturl, headers=headers )

# ----------------------------------------------------------------------
    def fetch_file( self, fetchfile, storefile ) :
        resp = requests.get( fetchfile )
        with open( storefile, 'wb') as fd:
            fd.write(resp.content) 
        self.debug ( f'Downloaded file: {fetchfile}, size: {len(resp.content)} bytes, stored file: {storefile}' )

# ----------------------------------------------------------------------
    async def fetch_task( self, fetchfile, storefile ) :
        resp = requests.get( fetchfile )
        with open( storefile, 'wb') as fd:
            fd.write(resp.content) 
        self.debug ( f'Downloaded file: {fetchfile}, size: {len(resp.content)} bytes, stored file: {storefile}' )
    
    
# # ----------------------------------------------------------------------
#     async def forward_message( self, msg ): 
#         # if a standard message, handle it and return
#         # else call handle_message to handle specific messages
#         if await self.handle_command_message( msg ):
#             return
#         if await self.handle_config_message( msg ):
#             return

#         if msg.get('section','') == 'begin': # browser has started, awaits sections content
#             await self.standard_sections_update()
#             # not return 
        
#         await self.handle_message( msg )

# # ----------------------------------------------------------------------
#     async def handle_message( self, msg ): 
#         pass

# # ----------------------------------------------------------------------
#     async def handle_config_message( self, msg ):
#         section = msg['section'] 

#          # { section:config_items, key:itemid, button:clickedbutton, value:value} 
#         if section !=  f'{self.name}_config_items' :
#             return False
#         button = msg.get('button','')
#         key = msg.get('key','')
#         if button == 'save':
#             self.config_items.set_value( key, msg.get('value',''))
#             self.debug( f'config_item key:{key} set to {self.config_items.value(key)}' )
#         if button == 'remove':
#             self.config_items.remove( key )
#             self.debug( f'item with key:{key} removed' )

#         self.config_items.store( f'{self.name}_config.json' )
#         return True

            
# # ----------------------------------------------------------------------
#     async def handle_command_message( self, msg ):
#         # { section:  , key:  } 
#         section = msg['section']
        
#         # handle state items update button 
#         if section == f'{self.name}_state_items' : 
#             self.debug(f'handle_command_message for {self.name} {section=}')
#             await self.state_section_update()
#             return True
        
#         # handle command item buttons
#         if section == f'{self.name}_command_items' : 
#             key = msg.get('key','')
#             if self.command_items.isasync(key):
#                 await self.command_items.func(key)()
#             else:    
#                 self.command_items.func( key )()
#             return True

#         return False


# ----------------------------------------------------------------------
    async def forward_message( self, msg ): 
        # if a standard message, handle it and return
        # else call handle_message to handle specific messages
        section = msg['section']
        
        # handle state items update button 
        if section == f'{self.name}_state_items' : 
            await self.state_section_update()
            return
        
        # handle command item buttons
        if section == f'{self.name}_command_items' : 
            key = msg.get('key','')
            if self.command_items.isasync(key):
                await self.command_items.func(key)()
            else:    
                self.command_items.func( key )()
            return

        # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        if section ==  f'{self.name}_config_items' :
            button = msg.get('button','')
            key = msg.get('key','')
            if button == 'save':
                self.config_items.set_value( key, msg.get('value',''))
                self.debug( f'config_item key:{key} set to {self.config_items.value(key)}' )
            if button == 'remove':
                self.config_items.remove( key )
                self.debug( f'item with key:{key} removed' )

            self.config_items.store( f'{self.name}_config.json' )
            return 

        if section == 'begin': # browser has started, awaits sections content
            await self.standard_sections_update()
            # not return 
        
        await self.handle_message( msg ) 

#

# ----------------------------------------------------------------------
    async def task( self, pause = 5 ): 
        '''dummy task to be overridden'''
        while True:
            await asyncio.sleep(pause)
            self.debug( f'{self.name} heartbeat was sent')

# ----------------------------------------------------------------------
    def start_tasks( self  ): 
        asyncio.create_task( self.task() )

# ----------------------------------------
    def loglevel( self, DIE ):
        self.log_level = DIE

# ----------------------------------------
    def debug( self, message ):
        return log.debug( message, self.name, self.log_level)
        
# ----------------------------------------
    def info( self, message):
        return log.info( message, self.name, self.log_level)
    
# ----------------------------------------
    def error( self,message):
        return log.error( message, self.name, self.log_level)

# ----------------------------------------------------------------------
    def overrides( self, obj, method_name ):
        ''' check if method is overridden in subclass '''
        base_method = getattr( Base, method_name, None )
        sub_method  = getattr( obj.__class__, method_name, None )
        return sub_method is not None and sub_method != base_method
    
    def tell(self, meth ):
        x = '' if self.overrides( self, meth ) else 'not'
        self.debug( f'{self.name}.{meth} is {x} overridden.')