

let device_orientation = { alpha:0, beta:0, gamma:0, stop:false };



// -----------------------------------
function app_receive( op, data) {
  logger("App operation: " + op);
    if ( op == 'appstop' ) { 
    device_orientation.stop = true;
}
    else if ( op == 'appgo' ) { 
    device_orientation.stop = false;
}
}


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


 













