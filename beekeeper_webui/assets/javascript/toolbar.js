function populateToolbar(graph)
{
  toolbar = document.getElementById('toolbarcontainer')
}

function addToolbarIcon(toolbar, graph, tool)
{
  var funct = function(graph, evt, cell, x, y)
  {
    var parent = graph.getDefaultParent();
    var model = graph.getModel();
    
    var cable = null;
    var stylesheet = `shape=image;image=${image};` +
    `verticalLabelPosition=bottom;verticalAlign=top;`;
    model.beginUpdate();
    try
    {
      cable = graph.insertVertex(parent, null, '', x, y);
      cable.setConnectable(true);
    }
    finally
    {
      model.endUpdate();
    }
    graph.setSelectionCell(cable);
  }

  var icon = document.createElement('img');
  icon.setAttribute('src', tool);
  icon.setAttribute('id', 'sidebarItem');
  icon.title = 'Drag this onto the canvas to create a new ethernet connection';
  toolbar.appendChild(icon);

  var dragElement = document.createElement('div');
  dragElement.style.border = 'dashed black 1px';
  dragElement.style.width = '150px';
  dragElement.style.height = '150px';

  var ds = mxUtils.makeDraggable(icon,graph,funct,dragElement,0,0,true,true);
  ds.setGuidesEnabled(true);
}
window.dragMoveListener = dragMoveListener
