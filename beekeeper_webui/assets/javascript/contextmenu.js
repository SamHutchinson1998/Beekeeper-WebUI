function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell.isVertex()){
      if(cell.getAttribute('type', '') != 'textbox'){
        menu.addItem('SSH (to be completed)', null, function(){
          alert('SSH');
        });
        menu.addItem('VNC', null, function(){
          getVNC(cell);
        });
        menu.addItem('Deploy (to be completed)', null, function(){
          alert('Deploy');
        });
      }
      menu.addItem('Delete', null, function(){
        removeDevices(graph);
      });
    }
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
