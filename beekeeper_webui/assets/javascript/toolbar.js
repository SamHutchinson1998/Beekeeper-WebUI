function populateToolbar(graph)
{
  var toolbar = document.getElementById('toolbarContainer');
  addToolbarItem(toolbar, graph, '../static/devices/ethernet_cable.svg', 'cable');
  addToolbarItem(toolbar, graph, '../static/devices/Label.svg', 'textbox');
  addToolbarButton(toolbar, '../static/devices/start_button.svg', 'start', graph);
  addToolbarButton(toolbar, '../static/devices/stop_button.svg', 'stop', graph);
}

function addToolbarItem(toolbar, graph, tool, tooltype)
{
  var funct = function(graph, evt, cell, x, y)
  {
    var parent = graph.getDefaultParent();
    var model = graph.getModel();
    var cell = null;
    var style = null;
    model.beginUpdate();
    try
    {
      switch(tooltype)
      {
        case 'textbox':
          style = `verticalLabelPosition=center;verticalAlign=center;` +
            `fontFamily=helvetica;fontStyle=1;fontColor=black;fontSize=20;` +
            `strokeColor=none;fillColor=none;`;
          cell = graph.insertVertex(parent, null, 'Text Here', x, y, 120, 30, style);
          cell.setConnectable(false);
        break;
        case 'cable':
          style = `strokeWidth=7;strokeColor=black;endArrow=none;html=1;`;
          cell = new mxCell('Test Cable', new mxGeometry(0, 0, 150, 150), style); // last two values are height and width respectively
          cell.geometry.setTerminalPoint(new mxPoint(0, 170), true); // source point
          cell.geometry.setTerminalPoint(new mxPoint(180, 0), false); // target point
          cell.geometry.relative = true;
          cell.edge = true;
          graph.importCells([cell], x, y, parent);
        break;
        default:
          cell = null;
      }
    }
    finally
    {
      model.endUpdate();
    }
    graph.setSelectionCell(cell);
  }

  var icon = document.createElement('img');
  icon.setAttribute('src', tool);
  icon.setAttribute('id', 'toolbarItem');
  icon.title = `Drag this onto the canvas to create a new ${tooltype}`;
  toolbar.appendChild(icon);

  var dragElement = document.createElement('div');
  dragElement.style.border = 'dashed black 1px';
  dragElement.style.width = '100px';
  dragElement.style.height = '100px';

  var ds = mxUtils.makeDraggable(icon,graph,funct,dragElement,0,0,true,true);
  ds.setGuidesEnabled(true);
}

function addToolbarButton(toolbar, image, type, graph)
{
  var button = document.createElement('button');
  button.setAttribute('class', 'btn btn-outline-secondary');
  button.style.height = '25px';
  button.style.width = '25px';
  button.setAttribute('id', 'toolbarItem');
  button.title = `${type} selected/all devices`;
  var img = document.createElement('img');
  img.setAttribute('src', image);
  img.style.width = '10px';
  img.style.height = '10px';
  img.style.Align = 'center';
  //img.style.marginRight = '2px';
  button.appendChild(img);

  switch(type)
  {
    case 'start':
      startVirtualMachines(button, graph);
    break;
    case 'stop':
      stopVirtualMachines(button, graph);
    break;
  }
  // click_function is a custom object passed through as a param in addToolbarButton
  toolbar.appendChild(button);
}

function startVirtualMachines(button, graph)
{
  button.addEventListener("click", function(){
    console.log(graph.getSelectionCells());
    console.log('Starting VMs');
  })
}

function stopVirtualMachines(button, graph)
{
  button.addEventListener("click", function(){
    console.log(graph.getSelectionCells());
    console.log('Stopping VMs');
  })
}
