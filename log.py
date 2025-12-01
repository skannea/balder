import time

logfifo = []
unsent = 0
logfile = ''

#--------------------------------------------------------------------
def begin( filename ):
    global logfifo, unsent, logfile
    logfile = filename
    logfifo = []
    try: 
         import ntptime
         ntptime.settime()
    except:
        pass    
    try:
        with open( logfile, 'r', encoding="utf-8") as f:
            logfifo = f.readlines()
    except:
        makepost(f"Logging started. No log found. ", 'I', 'log' )
    info( f'Opening log after reading {len(logfifo)} log entries from file {logfile}', 'log' )

#--------------------------------------------------------------------
def end():
    global logfifo, logfile
    info( f'Closing log after writing {len(logfifo)} log entries to file {logfile}', 'log' )
    with open( logfile, 'w', encoding="utf-8") as f:
        for s in logfifo:
             f.write( s ) 

#--------------------------------------------------------------------
def reset(  ):
    global unsent, logfifo
    unsent = len( logfifo ) 

#--------------------------------------------------------------------
def line( ):
    global unsent, logfifo
    if unsent > 0 :
        ix = len( logfifo ) - unsent # oldest unsent post
        unsent -= 1
        return logfifo[ix]
    return None

#-------------------------------------
def makepost( text, type, name='' ):   
    global unsent, logfifo
    
    tim = time.localtime( time.mktime( time.localtime())+3600) # trick to adjust for timezone
    # E-exec  2025-10-22 13:47:34   Message text
    # 0 2     8    13 16 19      27 30
    post = f'{type:1}-{name:6}{tim[0]:04}-{tim[1]:02}-{tim[2]:02} {tim[3]:02}:{tim[4]:02}:{tim[5]:02}   {text}\n' 
    
    logfifo.append( post )
    unsent += 1
    while len(logfifo) > 40: 
        logfifo.pop(0)   # remove oldest     
    

# ----------------------------------------
def debug( message, name='', log_level='DIE' ):
        if 'D' in log_level : 
           makepost(message, 'D', name )
        return message    
    
# ----------------------------------------
def info( message, name='', log_level='DIE'):
        if 'I' in log_level : 
             makepost(message, 'I', name )
        return message
    
# ----------------------------------------
def error( message, name='', log_level='DIE'):
        if 'E' in log_level : 
            makepost(message, 'E', name )
        return message


