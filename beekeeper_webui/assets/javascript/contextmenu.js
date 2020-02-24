function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell.isVertex()){
      menu.addItem('SSH (to be completed)', null, function(){
        alert('SSH');
      });
      menu.addItem('VNC (in progress)', null, function(){
        getVNC(cell);
      });
      menu.addItem('Delete', null, function(){
        removeDevices(graph);
      });
      menu.addItem('Deploy (to be completed)', null, function(){
        alert('Deploy');
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
  window.location = '/get_device_vnc?cell_id='+id
}

function get_device_vnc(cell_id)
{

}

function deployDevice()
{

}
