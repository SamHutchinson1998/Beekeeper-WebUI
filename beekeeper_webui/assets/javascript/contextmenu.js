function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell){ // A user could right-click on a blank area
      if(isCellDevice(cell)){
        if(cell.children[1]){
          menu.addItem('Disconnect to the internet', null, function(){
            connectToTheInternet(graph, cell);
          });
        } else {
          menu.addItem('Connect from the internet', null, function(){
            connectToTheInternet(graph, cell);
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
  image = getVector('nat')
  var style = `port;shape=image;image=${image};spacingLeft=12;`;
  var nat_logo = graph.insertVertex(cell, null, '', 1, 0.3, 16, 16, style, true);
  nat_logo.geometry.offset = new mxPoint(-8, -8);
}

function disconnectFromTheInternet(graph, cell)
{
  nat_cell = cell.children[1]; // The cell which is the nat icon
  graph.removeCell(nat_cell);
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

