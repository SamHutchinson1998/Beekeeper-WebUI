function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell){ // A user could right-click on a blank area
      if(isCellDevice(cell)){
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

function isCellDevice(cell)
{
  var output = null;
  var cell_id = cell.getId();
  $.ajax({
    url: "lookup_device",
    async: false,
    data: {'cell_id': cell_id},
    success: function(result){
      if(result['response'] == "Found"){
        output = true;
      }
      else{
        output = false;
      }
    }
  });
  return output;
}
