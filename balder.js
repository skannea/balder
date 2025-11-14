/*
balder.js

*/

// -----------------------------------
//Global constants are set in html file by server on 
//<script 
// var url=...
// 
// </script>


let socket;
let statusline_element;
let loggerdiv;
let current_device = '';
let statusitems = [];

let test_element ;
  
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
        let obj = {}

        obj.section = 'command_items'
        obj.key = 'begin'
        to_server( 'nosection', 'begin' );
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
    test_element = document.getElementById("test")
    test_element.innerHTML = '<button onclick = "onPermissionClick()">Allow device orientation</button>';

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
// send_section_item_button_value
function to_server( section, item, button='', value='' ) {
  if (button) send({ 'section':section, 
                     'button': button, 
                     'key':    item.parentElement.id, 
                     'value':  item.parentElement.children[1].value } )
  else        send({ 'section':section, 
                     'button': item,  
                     'key': item,   
                     'value': '' } )   
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



function handleOrientation(event) {
  const absolute = event.absolute;
  const alpha = Math.round(event.alpha);
  const beta = Math.round(event.beta);
  const gamma = Math.round(event.gamma);

  // Do stuff with the new orientation data  
  test_element.innerHTML =  `alpha: ${alpha}<br>beta: ${beta}<br>gamma: ${gamma}<br>`;
  

}



function onPermissionClick() {
  if (typeof DeviceMotionEvent.requestPermission === 'function') {
    // Handle iOS 13+ devices.
    DeviceMotionEvent.requestPermission()
      .then((state) => {
        if (state === 'granted') {
          window.addEventListener('deviceorientation', handleOrientation);
        } else {
          console.error('Request to access the orientation was rejected');
          test_element.innerHTML = 'Not permitted';
        }
      })
      .catch(console.error);
  } else {
    // Handle regular non iOS 13+ devices.
    window.addEventListener('deviceorientation', handleOrientation);
  }
}


 













