import items


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class ConfigItems( items.ConfigItems ):

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
    def action( self, msg):
        button = msg.get('button','')
        key = msg.get('key','')
        if button == 'save':
            self.set_value( key, msg.get('value',''))
        if button == 'remove':
            self.remove( key )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class CommandItems( items.CommandItems ):

# ----------------------------------------------------------------------
    def html( self, id='' ):
        code = ''
        for key in self.iter():
                code += f'''<button class="long" onclick="to_server( '{id}', '{key}')">{self.name(key)}</button><br>'''
        return code        

# ----------------------------------------------------------------------
    async def run( self, msg ):
        key = msg.get('key','')
        if self.isasync(key):
            print('await')
            await self.func(key)()
        else:    
            print('direct')
            self.func( key )()

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class StateItems( items.StateItems ):

# ----------------------------------------------------------------------
    def html(self, id=''):
        self.evaluate_all()
        
        code = ''
        for key in self.iter():
                code +=  f'''<input class="short" disabled value="{self.name(key)}"/>
                            <input class="long" type="text" value="{self.value(key)}"/><br>'''
        return code
    
