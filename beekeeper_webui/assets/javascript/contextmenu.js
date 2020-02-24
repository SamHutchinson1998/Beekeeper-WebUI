function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell.isVertex()){
      menu.addItem('SSH (to be completed)', null, function(){
        alert('SSH');
      });
      menu.addItem('VNC (in progress)', null, function(){
        getVNC(graph);
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
function getVNC(graph)
{
  var i;
  var selected_cells = graph.getSelectionCells();
  for(i = 0; i < selected_cells.length; i++){
    // openVNC method?
    // for each device, open a new vnc tab?
    var id = selected_cells[i].getId();
    get_device_vnc(cell_id);
  }
}

function get_device_vnc(cell_id)
{
  $.ajax({
    url: 'get_device_vnc',
    data: {'cell_id':cell_id},
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

function deployDevice()
{

}
