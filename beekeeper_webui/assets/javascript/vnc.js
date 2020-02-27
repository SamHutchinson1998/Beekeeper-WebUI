// RFB holds the API to connect and communicate with a VNC server
import RFB from './novnc/3/core/rfb.js';

let rfb;
let desktopName;


// credit to noVNC for this method https://github.com/novnc/noVNC/blob/master/vnc_lite.html
function readQueryVariable(name, defaultValue) {
  
  // A URL with a query parameter can look like this:
  // https://www.example.com?myqueryparam=myvalue
  //
  // Note that we use location.href instead of location.search
  // because Firefox < 53 has a bug w.r.t location.search
  const re = new RegExp('.*[?&]' + name + '=([^&#]*)'),
        match = document.location.href.match(re);
  if (typeof defaultValue === 'undefined') { defaultValue = null; }

  if (match) {
    // We have to decode the URL since want the cleartext value
    return decodeURIComponent(match[1]);
  }

  return defaultValue;
}

const host = readQueryVariable('host', window.location.hostname);
let port = readQueryVariable('port', window.location.port);
const password = readQueryVariable('password', '');
const token = readQueryVariable('token', '');
const path = readQueryVariable('path', `websockify/?token=${token}`);

// | | |         | | |
// | | | Connect | | |
// v v v         v v v

// Build the websocket URL used to connect
let url;
if (window.location.protocol === "https:") {
  url = 'wss';
} else {
  url = 'ws';
}
url += '://' + host;
if(port) {
  url += ':' + port;
}
url += '/' + path;

createRfbConnection();

document.getElementById('ctrlAltDelbtn').onclick = sendCtrlAltDel();
document.getElementById('reconnectbtn').onclick = createRfbConnection();


function sendCtrlAltDel()
{
  rfb.sendCtrlAltDel();
}

function createRfbConnection()
{
  // Creating a new RFB object will start a new connection
  rfb = new RFB(document.getElementById('screen'), url,
              { credentials: { password: password } });
}

// keep these around for later

//rfb.viewOnly = readQueryVariable('view_only', false);
//rfb.scaleViewport = readQueryVariable('scale', false);
