function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell.isVertex()){
      menu.addItem('SSH', null, function(){
        alert('SSH');
      });
      menu.addItem('VNC', null, function(){
        alert('VNC');
      });
      menu.addItem('Delete', null, function(){
        alert('Delete');
      });
      menu.addItem('Deploy', null, function(){
        alert('Deploy');
      });
    }
  }
}