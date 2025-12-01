import asyncio
import sys
import gc
from balder_base import Base



# ----------------------------------------------------------------------------------------------    
# ----------------------------------------------------------------------------------------------    
class Exec(Base):

# ----------------------------------------------------------------------
    def init( self ): 
        
        self.failure  = asyncio.Event()   # event variable that is set when an app error occurs  
        self.resume   = asyncio.Event()   # event variable that is set to resume app exeution
        self.fallback = False
        self.auto = False
        self.app = None
        asyncio.create_task( self.execute_task(  ) )
            
# ----------------------------------------------------------------------
    def config_items_setup( self ): 
        self.config_items.default_name_value('runapp',   'App to run', '')
        self.config_items.default_name_value('backupapp',   'Fallback app', '')

# ----------------------------------------------------------------------
    async def handle_message( self, msg ): 

        if msg.get('section','') == 'file': # file upload request --> start task thet fetches file and writes to disk 
            asyncio.create_task( self.fetch_task( msg.get('file','') ) )
            return



        if self.app: 
            await self.app.forward_message(msg)
        
        

                
# ----------------------------------------------------------------------
    def command_items_setup( self  ): 
        
        #async def update_states():
        #    await self.send_replace( 'state_items', self.state_items.html( 'state_items'))
        #self.command_items.set_name_async('xupdstates', 'Update states', update_states )

    
                
        def gcrap():
            alloc = gc.mem_alloc()
            free  = gc.mem_free()
            tot = alloc + free
            self.info( f'{alloc=}  {free=}  {tot=} used={alloc/tot*100:0.1f}%' )
        self.command_items.set_name_func('gc', 'Memory info', gcrap )
        
        def lognoD():
            self.loglevel('IE')
        self.command_items.set_name_func('lognod', 'Log level I+E', lognoD )
        
        def lognoI():
            self.loglevel('E')
        self.command_items.set_name_func('lognoi', 'Log level only E', lognoI )

        #def f(): self.fallback = False
        #self.command_items.set_name_func('fb0', 'Normal mode', f )    
            
        #def f(): self.fallback = True
        #self.command_items.set_name_func('fb1', 'Fallback mode', f )    
        
        #def f(): self.auto = False
        #self.command_items.set_name_func('auto0', 'Manual mode', f )    
            
        #d#ef f(): self.auto = True
        #self.command_items.set_name_func('auto1', 'Auto mode', f )    
             
        def f(): self.resume.clear()
        self.command_items.set_name_func('res0', 'Hold', f )    
            
        def f(): self.resume.set()
        self.command_items.set_name_func('res1', 'Resume', f )    
             
        def f(): self.failure.clear()
        self.command_items.set_name_func('fail0', '(Fail clear)', f )    
            
        def f(): self.failure.set()
        self.command_items.set_name_func('fail1', '(Fail set)', f )    
     
        #async def af():
        #    await self.send( 'permit', {}  )
        #self.command_items.set_name_async('permit', 'funkar inte Give permission', af )


# ----------------------------------------
    async def execute_task( self ):
        '''handle app tasks'''
        self.debug(f'execute_task started')
        self.auto = False #self.config_items.bool('autoexec') 
        while True:
            self.coros = {}  # name:coro
            tasks = {}  # name:task
            
            if not self.auto : # manual start, wait for resume command
                self.debug('manual resume - wait')
                await self.resume.wait()
                await asyncio.sleep(0.1)  # let other tasks run
                self.resume.clear()
                await asyncio.sleep(0.1)  # let other tasks run
                self.debug('manual resume - resume.clear')
                await asyncio.sleep(0.1)  # let other tasks run
            else:
                self.debug('auto resume ')
                
            # replace/select app module
            
            try:
                loaded_app = app.__name__ 
            except:
                loaded_app = ''  

            if loaded_app in sys.modules:
                self.debug( f'removing app module: {loaded_app}' )
                sys.modules.pop(loaded_app)

            #ap = self.config_items.value('backupapp')
            #if not ap:
            ap = self.config_items.value('runapp')

            if ap:  
                try:
                    self.debug(f'from {ap} import App')
                    vars = { 'v':self.levels[1:] }   # levels=[ exec, app ]
                    code = f'''from {ap} import App;app = App(v)'''
                    exec(code, {}, vars)
                    self.app = vars['app']
                except Exception as ex:
                    self.error(f'could not import module {ap}: {ex}')
                    await asyncio.sleep(1)
                    continue  
            else:
                self.debug('no app module specified, skipping import')
                await asyncio.sleep(1)
                continue    


            try:
                # initialize 
                await self.app.send_replace( 'app_section', self.app.standard_sections_html() )
                await self.app.standard_sections_update()
                self.failure.clear()
                for name, coro in self.app.get_coros().items():
                    self.debug(f'App task {name} is created')
                    tasks[name] = asyncio.create_task( self.app_task( coro, name ))   
                    # app tasks are runnning
                
                self.debug('App tasks are running, wait for failure flag')
                await self.failure.wait()
                # failure -> cancel app tasks
                for name, task in tasks.items() :
                    try:
                        task.cancel()
                    except:
                        self.debug(f'task {name} was already cancelled') 
                    else: 
                        self.debug(f'task {name} was cancelled')
                     
                self.debug( "All app tasks are cancelled, other tasks are still running")
            
            except Exception as ex:
                self.error(f'Error when starting app tasks: {ex}')
                continue
                
# ----------------------------------------
    # overcoat to run an app coro as a task
    async def app_task( self, coro, name ):
        try:
            await coro
            raise Exception(f'unexpected return from app coro {name}') 
        except Exception as ex:
            self.debug(f'Error in task {name}: {ex}')
            self.failure.set()
     
 

 
    