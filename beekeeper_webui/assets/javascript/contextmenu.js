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
  $.ajax({
    url: 'get_device_vnc',
    data: {'cell_id':id},
    success: function(result){
      if(result.status == 200){ // if the task was successful
        console.log('success', result);
      }
      else{
        // handle error code here
        console.log('error', result);
      }
    }  
  });
}

function get_device_vnc(cell_id)
{

}

function deployDevice()
{

}
