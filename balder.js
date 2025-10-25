/*
balder.js


*/

// -----------------------------------
//Global constants are set in html file by server on 
//<script 
// var url=...

// </script>


let socket;
let statusline_element;
let loggerdiv;
let current_device = '';
let statusitems = [];
  
// -----------------------------------
function logger(s) {
  //if (credentials.log == 'screen') loggerdiv.innerHTML += ( s + '<br>' )
  //if (credentials.log != 'none')   
    console.log(s)
}

// -----------------------------------
function statusline(s) {
  statusitems.push(s)
  if (statusitems.length>5) statusitems.shift()
  statusline_element.innerHTML = '<p>' + statusitems.join('  -  ') + '</p>';

}

// -----------------------------------
function setup( wsurl ) {
    statusline_element = document.getElementById("statusline")
    loggerdiv = document.getElementById("log_items")
    logger( 'setup' )
    statusline('awaiting connection'); 
    
    socket = new WebSocket(wsurl);
    
    socket.addEventListener('open', 
      function () {
        logger("Connected to server, sending start");
        let obj = { "op":"begin", "data":{} }
        send( obj );
        statusline('connected');
      });
  
    socket.addEventListener('close', 
      function () {
        logger("Close!"); 
        statusline('disconnected'); 
        socket.close(); 
        // setTimeout( recover_timeout, 4000 );
      });
  
    socket.addEventListener('message', receive);
    
    document.getElementById('user_input' ).addEventListener( 'click',  on_user_input ); 
}

// -----------------------------------
function reload() {
  statusline('reloading');
  socket.close();
  setTimeout( function() { location.reload(); }, 2000 );
}

// -----------------------------------
function showhide( div ) {
  elem = document.getElementById(div);
  elem.style.display = (elem.style.display === 'none') ? 'block' : 'none';
}

 

// -----------------------------------
// event from a div (with id), containing inputs/selects (with data-click=#) and a set of buttons named with data-click=...
// if there are multiple inputs/selects with data-click=#, their values are concatenated with commas
function on_user_input(e) {  
  let div =  e.target.parentElement;
  let obj = { clientid:clientid, device:current_device, op:'user_input', div:div.id, button:'', value:'', values:{} };
  let elems = div.children;
  for (let i=0; i<elems.length; i++) {
      if (elems[i] == e.target) 
        obj.button = elems[i].getAttribute('data-click'); //clicked button
      if (elems[i].hasAttribute('data-value'))  {
              obj.value = elems[i].value; // element holding a value
              obj.values[elems[i].getAttribute('data-value')] = obj.value; // key:value is (type of input):value
          }  
  }        
  if ( !obj.button ) return; // clicked element was not a button (marked with data-click) 
  statusline('button:' + obj.button ); 
  
  logger( `on_user_input: ${JSON.stringify( obj )} `)
  send( obj );
}      


// -----------------------------------
function receive(event) {
  logger("Receiving: " + event.data);
  logger("Receiving bytes: " + event.data.length );
  ev = JSON.parse( event.data )
    
    let op = ev.op;
    //statusline('op='+op); 
    
 
    logger( 'operation: ' + op )
    if (op == 'replace') {
        let elem = document.getElementById(ev.data.element)
        elem.innerHTML = ev.data.html;
    }    
    
    else if ( op == 'before' ) { 
        let elem = document.getElementById(ev.data.element)
        elem.innerHTML =  ev.data.text + elem.innerHTML;
    }
    
    else if ( op == 'after' ) { 
        let elem = document.getElementById(ev.data.element)
        elem.innerHTML +=  ev.data.text ;
    }
    
    else if ( op == 'reload' ) { 
    logger( 'reload' );  
    //socket.close(); 
    location.reload();
    
}
}

// -----------------------------------
function send(obj) {
  if (socket.readyState === WebSocket.OPEN) {
    console.log(obj);
    str = JSON.stringify(obj)
    logger("Sending json: " + str);
    socket.send(str);
  } 
  else {
    logger("Could not send to server: " + obj)
  }  
}





