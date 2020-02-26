import RFB from './noVNC/core/rfb.js';

let rfb;
let desktopName;

try
{
  rfb = new RFB(document.getElementById('screen'), 'ws://150.237.94.18:5901/websockify');
}
catch(err)
{
  console.log(err.message);
}
