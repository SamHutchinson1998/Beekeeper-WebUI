function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell){ // A user could right-click on a blank area
      if(isCellDevice(cell)){
        if(cell.children[1]){
          menu.addItem('Connect to the internet', null, function(){
            connectToTheInternet();
          });
        } else {
          menu.addItem('Disconnect from the internet', null, function(){
            connectToTheInternet();
          });
        }

        menu.addItem('SSH (to be completed)', null, function(){
          alert('SSH');
        });
        menu.addItem('VNC', null, function(){
          getVNC(cell);
        });
        menu.addItem('Deploy (to be completed)', null, function(){
          alert('Deploy');
        });
        menu.addItem('Delete', null, function(){
          removeDevices(graph);
        });
      }
    }
  }
}

function connectToTheInternet(graph, cell)
{
  children = cell.children;
  var id = cell.getId();
  image = getVector('nat')
  var style = `port;shape=image;image=${image};spacingLeft=12;`;
  if(children){
    graph.getModel().setStyle(children[1], style);
  }
}

function disconnectFromTheInternet(graph, cell)
{
  children = cell.children;
  var style = ''
  if(children){
    graph.getModel().setStyle(children[1], style)
  }
}

function getSSH()
{
  
}

function getVNC(cell)
{
  var id = cell.getId();
  //window.location = '/get_device_vnc?cell_id='+id
  window.open( '/get_device_vnc?cell_id='+id, '_blank');
}

function deployDevice()
{

}

