import RFB from './noVNC/core/rfb.js';


// Credit to noVNC: https://github.com/novnc/noVNC/blob/master/vnc_lite.html

let rfb;
let desktopName;

// This function extracts the value of one variable from the
// query string. If the variable isn't defined in the URL
// it returns the default value instead.
function readQueryVariable(name, defaultValue) {
    // A URL with a query parameter can look like this:
    // https://www.example.com?myqueryparam=myvalue
    //
    // Note that we use location.href instead of location.search
    // because Firefox < 53 has a bug w.r.t location.search
    const re = new RegExp('.*[?&]' + name + '=([^&#]*)'),
          match = document.location.href.match(re);

    if (match) {
        // We have to decode the URL since want the cleartext value
        return decodeURIComponent(match[1]);
    }

    return defaultValue;
}

//const host = readQueryVariable('host', window.location.hostname);
//let port = readQueryVariable('port', window.location.port);
var host = '127.0.0.1';
var port = 6080;
const password = readQueryVariable('password');
//const path = readQueryVariable('path', 'websockify');
var path = readQueryVariable('path', 'websockify/?token=token1');
// | | |         | | |
// | | | Connect | | |
// v v v         v v v

status("Connecting");

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

// Creating a new RFB object will start a new connection
rfb = new RFB(document.getElementById('screen'), url,
              { credentials: { password: password } });

// Set parameters that can be changed on an active connection
rfb.viewOnly = readQueryVariable('view_only', false);
rfb.scaleViewport = readQueryVariable('scale', false);
