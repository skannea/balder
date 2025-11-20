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
                <button onclick="on_config_click( '{id}', this, 'save'   )">Save</button>
                <button onclick="on_config_click( '{id}', this, 'remove' )">Remove</button>
              </div>'''
        return code
    

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class CommandItems( items.CommandItems ):

# ----------------------------------------------------------------------
    def html( self, section='' ):
        code = ''
        for key in self.iter():
                code += f'''<button class="long" onclick="on_command_click( '{section}', '{key}')">{ self.name(key) }</button><br>'''
        return code        

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
    
