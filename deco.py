





class CC:

    def __init__(self):
        self.value = 'y'

    def simple_decorator(self, func):
      def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
      return wrapper


    @simple_decorator
    def say_hello( self, n='x'):
        print("Hello!"+ n)


    def say(self):        
        self.say_hello()

cc = CC()
cc.say_hello()