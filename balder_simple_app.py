import asyncio
import machine
from balder_base import Base

# ----------------------------------------------------------------------------------------------    
# ----------------------------------------------------------------------------------------------    
class App(Base):

# ----------------------------------------------------------------------
    def init( self ): 
        self.enable = asyncio.Event()  # start/stop
        self.info('Initial app configuration and command set posted to server.')
        #asyncio.create_task(self.blink_task(2))
        self.n = 0
        
            
# ----------------------------------------
    def get_coros( self ):
        return {'ole':self.blink_task('LED_RED', 3.1), 'dole':self.blink_task('LED_BLUE', 2.2), 'doff':self.blink_task('LED_GREEN', 2.7)}
         
# ----------------------------------------------------------------------
#    async def handle_message( self, msg ): 
            
           
                
# ----------------------------------------------------------------------
    def command_items_setup( self  ): 
    
        def fs(): 
            self.debug('set')
            self.enable.set()
        self.command_items.set_name_func('startblink', 'Start blinking', fs )    

        def fc(): 
            self.debug('clear')
            self.enable.clear()
        self.command_items.set_name_func('stopblink', 'Stop blinking', fc )    

        # ----------------------------------------------------------------------
    def state_items_setup( self ): 
        self.state_items.set_name_func( 'count', 'Number of changes', lambda: self.n )
        
        self.state_items.set_name_func( 'state', 'Current state', lambda : 'running' if self.enable.is_set() else 'stopped')


# an app consists of multiple coros
#
 # ----------------------------------------
    async def blink_task( self, led, t ):
        self.info(f'Blink task started, t = {t}')
        blue_led = machine.Pin(led, machine.Pin.OUT, value=0)  # Initialize blue LED on GPIO2 (D4 on NodeMCU) as output, set to high (off)
        while True:
            try:
                await self.enable.wait()
                self.n += 1
                #if n > 20:
                #    raise Exception( self.error( 'Blink task counter overflow' ))

                if blue_led.value() == 1:
                    blue_led.value( 0)
                    #self.debug( f'{t} off')

                else:
                    blue_led.value( 1)  
                    #self.debug( f'{t} on')
  
                await asyncio.sleep(t)
            except Exception as ex:  
                self.enable.clear()
                await self.enable.wait()
                self.n = 0

 
            
     
