let socket;
let statusline_element;
let statusitems = [];

let loggerdiv;

let current_device = '';
let test_element ;
  
// -----------------------------------
function logger(s) {
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
    
    wsurl = window.location.href;
    wsurl = wsurl.replace( 'http', 'ws' );
    wsurl = wsurl.replace( 'page', 'ws' );
    
    socket = new WebSocket(wsurl);
    logger("wsurl=" + wsurl); 
    socket.addEventListener('open', 
      function () {
        logger("Connected to server, sending start");
        send({ 'section':'begin' } );
        send({ 'section':'files', 'filelist': filelist } );
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
    
    //document.getElementById('user_input' ).addEventListener( 'click',  on_user_input ); 
    //test_element = document.getElementById("test")
    //test_element.innerHTML = '<button onclick = "onPermissionClick()">Allow device orientation</button>';

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
function on_config_click( section, elem, button ) {
  send({ 'section':section, 
         'button': button, 
         'key':    elem.parentElement.id, 
         'value':  elem.parentElement.children[1].value } )
  }

// -----------------------------------
function on_command_click( section, key ) {
  send({ 'section':section, 
         'key': key, 
       })
  }



// -----------------------------------
async function on_file_click( file ) {
  logger( 'on_file: '+ file ); 
  send({ 'section':'file', 'file': file  } )

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
        elem.innerHTML =  ev.data.html + elem.innerHTML;
    }
    
    else if ( op == 'after' ) { 
        let elem = document.getElementById(ev.data.element)
        elem.innerHTML +=  ev.data.html ;
    }
    
    else if ( op == 'reload' ) { 
    logger( 'reload' );  
    //socket.close(); 
    location.reload();
    
}
    else if ( op == 'appstop' ) { 
    device_orientation.stop = true;
}
    else if ( op == 'appgo' ) { 
    device_orientation.stop = false;
}
}

// -----------------------------------
function send(obj) {
  if (socket.readyState === WebSocket.OPEN) {
    str = JSON.stringify(obj)
    logger("Sending json: " + str);
    socket.send(str);
  } 
  else {
    logger("Could not send to server: " + obj)
  }  
}






// -----------------------------------
function on_file_select( input ) {
  let file = input.files[0];
  const reader = new FileReader();
  reader.onload = () => {
 //    send({ 'section':'server_files', 
 //           'button': 'upload', 
 //           'key':    file.name, 
 //           'value':  reader.result} )

    logger( file.name + " uploaded bv" );
    b = new Uint8Array( reader.result, 0, 40  );
    s =  new TextDecoder().decode(b)
    logger( s ) ;
    logger(JSON.stringify( s ))
    logger(JSON.stringify( b ))
    
    
  };
  reader.onerror = () => {
    logger("Error reading the file.");
  };
  
  //reader.readAsText(file);
  reader.readAsArrayBuffer(file);
}


let device_orientation = { alpha:0, beta:0, gamma:0, stop:false };


// -----------------------------------
function handleOrientation(event) {
  if (device_orientation.stop) return;
  const alpha = Math.round(event.alpha);
  const beta = Math.round(event.beta);
  const gamma = Math.round(event.gamma);

  // Do stuff with the new orientation data  
  
  if ( device_orientation.alpha != alpha ||
       device_orientation.beta  != beta  ||
       device_orientation.gamma != gamma ) {  
        
    device_orientation.alpha = alpha;
    device_orientation.beta = beta;
    device_orientation.gamma = gamma;
  send({ 'section':'app_orientation', 
         'alpha': alpha,
         'beta':  beta,
         'gamma': gamma } )  
 
  }  

}


// -----------------------------------
function onPermissionClick() {
  if (typeof DeviceMotionEvent.requestPermission === 'function') {
    // Handle iOS 13+ devices.
    DeviceMotionEvent.requestPermission()
      .then((state) => {
        if (state === 'granted') {
          window.addEventListener('deviceorientation', handleOrientation);
        } else {
          logger('Request to access the orientation was rejected');
          test_element.innerHTML = 'Not permitted';
        }
      })
      .catch(console.error);
  } else {
    // Handle regular non iOS 13+ devices.
    window.addEventListener('deviceorientation', handleOrientation);
  }
}


 













