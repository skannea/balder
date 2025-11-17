import asyncio
from balder_base import Base
from balder_angels_app import App


# ----------------------------------------------------------------------------------------------    
# ----------------------------------------------------------------------------------------------    
class Exec(Base):

# ----------------------------------------------------------------------
    def init( self ): 
        self.failure  = asyncio.Event()   # event variable that is set when an app error occurs
        self.resume   = asyncio.Event()   # event variable that is set to resume app exeution
        self.fallback = False
        self.auto = False
        self.app = App('app')


# ----------------------------------------------------------------------
    async def handle_message( self, msg ): 
        section = msg['section']
        # { section:command_items, key:commandkey  }
        if section == f'{self.name}_command_items' : 
            await self.command_items.run(  msg )
            return
                    
         # { section:config_items, key:itemid, button:clickedbutton, value:value} 
        elif section ==  f'{self.name}_config_items' :
            self.config_items.action( msg )
            return
        elif msg.get('key','') == 'begin': # browser has started, awaits sections content
            await self.standard_sections_update()
            
            
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
     
        async def af():
            await self.send( 'permit', {}  )
        self.command_items.set_name_async('permit', 'funkar inte Give permission', af )


