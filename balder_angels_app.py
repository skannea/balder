import asyncio
from balder_base import Base

# ----------------------------------------------------------------------------------------------    
# ----------------------------------------------------------------------------------------------    
class App(Base):

# ----------------------------------------------------------------------
    def init( self ): 

        self.orientation_changes = 0
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        self.stop = False
        self.speed = 123
        self.array = [1,2,3,4,5]
        self.state = 'running'
        self.reports = 0
        #asyncio.create_task( self.report_task() )
        
 
# ----------------------------------------------------------------------
    async def handle_message( self, msg ): 
        if await self.handle_command_message( msg ):
            return
        if await self.handle_config_message( msg ):
            return
        
        section = msg.get('section','')

        if section == 'begin': # browser has started, awaits sections content
            await self.send_replace( 'app_section', self.standard_sections_html() + self.permit_html() )
            await self.standard_sections_update()
        # { section:'orientation', alpha:int, beta:int, gamma:int  }
        elif section == f'{self.name}_orientation' : 
            self.orientation_changes += 1
            if self.stop :
                return
            self.alpha = msg.get('alpha',0)
            self.beta  = msg.get('beta',0)
            self.gamma = msg.get('gamma',0) 
            html = f'''Riktning: {self.alpha} grader<br>
                       Lutning: {self.beta} grader<br>
                       Rotation: {self.gamma} grader<br>
                       Antal: {self.orientation_changes}'''
    
            await self.send_replace( f'{self.name}_orientation', html)
            return
                    
   
        
            
                
# ----------------------------------------------------------------------
    def command_items_setup( self  ): 
        
                
        def lognoD():
            self.loglevel('IE')
        self.command_items.set_name_func('lognod', 'Log level I+E', lognoD )
        
        def lognoI():
            self.loglevel('E')
        self.command_items.set_name_func('lognoi', 'Log level only E', lognoI )

        def f(): asyncio.create_task( self.report_task() )
        self.command_items.set_name_func('starttask', 'Start report task', f )    
                
        def f(): self.stop = True
        self.command_items.set_name_func('servstop', 'Stop in server', f )    
            
        def f(): self.stop = False
        self.command_items.set_name_func('servgo', 'Go in server', f )    

        async def af(): await self.send('appstop')
        self.command_items.set_name_async('appstop', 'Stop', af )    
            
        async def af(): await self.send('appgo')
        self.command_items.set_name_async('appgo', 'Go', af )    

        async def update_states():
            await self.send_replace( f'{self.name}_state_items', self.state_items.html( f'{self.name}_state_items'))
        self.command_items.set_name_async('updstates', 'Update states', update_states )

# ----------------------------------------------------------------------
    def state_items_setup( self ): 
 
        self.state_items.set_name_func( 'reports', 'Rapporter', lambda : f'{self.reports} ' )
        self.state_items.set_name_func( 'alpha', 'Lutning', lambda : f'{self.alpha} grader' )
        self.state_items.set_name_func( 'beta', 'Riktning', lambda : f'{self.beta} grader' )
        self.state_items.set_name_func( 'gamma', 'Rotation', lambda : f'{self.gamma} grader' )
        self.state_items.set_name_func( 'changes', 'Antal ändringar', lambda : f'{self.orientation_changes}' )
        
        self.state_items.set_name_func( 'simple', 'Simple integer', lambda : f'{self.speed} km/h' )
        self.state_items.set_name_func( 'array', 'List of numbers', lambda : f'{self.array}' )
        self.state_items.set_name_func( 'state', 'Current state', lambda : self.state )

# ----------------------------------------------------------------------
    def permit_html( self ): 
        return f'''{self.section_html('app_orientation', 'Angels app', True, 
        '<button onclick = "onPermissionClick()">Allow device orientation</button>')}'''

    async def report_task(self, pause=5):
        while True:
            await asyncio.sleep(pause)
            self.reports += 1
            await self.state_section_update()
            