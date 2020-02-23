function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell.isVertex()){
      menu.addItem('SSH (to be completed)', null, function(){
        alert('SSH');
      });
      menu.addItem('VNC (to be completed)', null, function(){
        alert('VNC');
      });
      menu.addItem('Delete (to be completed)', null, function(){
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
function getVNC()
{

}
function deployDevice()
{
  
}
