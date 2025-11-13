from collections import OrderedDict

class Items():

    def __init__(self):
        self.dict = OrderedDict()
       
    def set( self, key, prop1, prop2=None, prop3=None ):
        self.dict[key] = [ prop1, prop2, prop3 ] 

    def remove( self, key ):
        self.dict.pop( key ) 

    def keylist(self):
        res = []
        for key in self.dict:
            res.append(key)
        return res    

    def iter(self):
        return self.dict    

    def name( self, key ):
        return self.dict[key][0]


class CommandItems(Items):
    '''func is async func() -> None'''
    def set_name_func( self, key, name, func ):
        self.set( key, name, func, False ) 

    def set_name_async( self, key, name, func ):
        self.set( key, name, func, True ) 

    def isasync( self, key ):
        return self.dict[key][2] 

    def func( self, key ):
        return self.dict[key][1] 
       

class ConfigItems(Items):

    def set_name_value( self, key, name, value ):
        self.set( key, name, str(value)) 

    def set_value( self, key, value ):
        self.dict[key][1] = str(value) 

    def value( self, key ):
        return self.dict[key][1] 

    def float( self, key ):
        try:
            return float(self.value(key))
        except: 
            return 0.0 

    def int( self, key ):
        try:
            return int(self.value(key))
        except: 
            return 0 


class StateItems(Items):
    ''' [ name, value_func, value ] where func() returns str, for examlpe: g where g=lambda: f'{ mydata }' '''
    def set_name_func( self, key, name, value_func ):
        self.set( key, name, value_func, str(value_func()) ) 

    def func( self, key ):  
        return self.dict[key][1] 

    def value( self, key ):
        return self.dict[key][2] 

    def evaluate(self, key):
        s = str( self.func( key )() )
        self.dict[key][2] = s
        return s
    
    def evaluate_all(self):
        for key in self.dict:
            self.dict[key][2] = str( self.func( key )() )



if __name__ == '__main__':
    import asyncio
        
        
    commands = CommandItems()
    
    def start():
        print('Start')
    
    commands.set_name_func( 'start', 'Starta', start )
    
    def arg( data='NODATA' ):
        print('Arg ' +data)
    
    commands.set_name_func( 'arg', 'Arg', arg )
    
    def stop():
        print('Stop')
    
    commands.set_name_func( 'stop', 'Stoppa', stop )
    


    states = StateItems()

    
    dura = 175
    x = lambda : f'{dura} hours'
    states.set_name_func( 'duration', 'Varaktighet', x  )
    print (states.name('duration'))
    print (states.value('duration'))
    dura = 234
    states.evaluate_all()
    print (states.value('duration'))
    
    ur = [13,15]
    #x = lambda : f'{ur[0]}:{ur[1]} '
    states.set_name_func( 'time', 'Tidpunkt', lambda : f'{ur[0]}:{ur[1]} '  )
    print (states.name('time'))
    print (states.value('time'))

    data = 'abrakadabra'
    def x():
        return data.upper()
    
    states.set_name_func( 'abra', 'Kadabra', x  )
    print (states.name('abra'))
    print (states.value('abra'))

    
    commands.func('stop')()
    
    #print( commands.dict )
    print( commands.keylist() )
    for k in commands.iter():
        print(commands.name(k))
        commands.func(k)()
    commands.remove('stop')
    print( commands.keylist() )
    
    
    conf = ConfigItems()
    
    conf.set_name_value( 'x2','two', 2)     
    conf.set_name_value( 'x3','three', '3')     
    conf.set_name_value( 'x4','four', {'f':4})     
    
    for k in conf.keylist():
        print(conf.name(k))
        print(conf.value(k))
        print(conf.float(k))
        print(conf.int(k))
  
    import asyncio
    async def coro() :
        print('before')
        await asyncio.sleep(2)
        print('after')
    commands.set_name_func( 'coro', 'Co routine', coro )
    asyncio.run( commands.func( 'coro' )() )

    commands.func('arg')('EXTRA')   
    