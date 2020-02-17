function populateToolbar(graph)
{
  var toolbar = document.getElementById('toolbarContainer');
  addToolbarItem(toolbar, graph, '../static/devices/ethernet_cable.svg', 'cable');
  addToolbarItem(toolbar, graph, '../static/devices/label.svg', 'textbox')
}

function addToolbarItem(toolbar, graph, tool, tooltype)
{
  var funct = function(graph, evt, cell, x, y)
  {
    var parent = graph.getDefaultParent();
    var model = graph.getModel();
    var cell = null;
    model.beginUpdate();
    try
    {
      switch(tooltype)
      {
        case 'cable':
          cell = createCable();
        case 'textbox':
          cell = createTextBox();
      }
      graph.importCells([cell], x, y, parent);
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
  icon.title = 'Drag this onto the canvas to create a new ethernet cable';
  toolbar.appendChild(icon);

  var dragElement = document.createElement('div');
  dragElement.style.border = 'dashed black 1px';
  dragElement.style.width = '100px';
  dragElement.style.height = '100px';

  var ds = mxUtils.makeDraggable(icon,graph,funct,dragElement,0,0,true,true);
  ds.setGuidesEnabled(true);
}

function createCable()
{
  var style = `strokeWidth=7;strokeColor=black;endArrow=none;html=1;`;
  cell = new mxCell('Test Cable', new mxGeometry(0, 0, 150, 150), style); // last two values are height and width respectively
  cell.geometry.setTerminalPoint(new mxPoint(0, 170), true); // source point
  cell.geometry.setTerminalPoint(new mxPoint(180, 0), false); // target point
  cell.geometry.relative = true;
  cell.edge = true;
  return cell;
}

function createTextBox()
{
  var style = `verticalLabelPosition=bottom;verticalAlign=top;labelHandleSize=10;`;
  cell = new mxCell('Text Here', new mxGeometry(0, 0, 100, 100), style); // last two values are height and width respectively
  cell.geometry.setTerminalPoint(new mxPoint(0, 100), true); // source point
  cell.geometry.setTerminalPoint(new mxPoint(100, 0), false); // target point
  cell.geometry.relative = true;
  cell.edge = false;
  return cell;
}

function addToolbarButton(toolbar, image, click_function)
{
  var button = document.createElement('button');

  var img = document.createElement('img');
  img.setAttribute('src', image);
  img.style.width = '20px';
  img.style.height = '20px';
  img.style.verticalAlign = 'middle';
  img.style.marginRight = '2px';
  button.appendChild(img);

  // click_function is a custom object passed through as a param in addToolbarButton
  button.addEventListener("click", click_function)
  toolbar.appendChild(button)
}

function startVirtualMachines()
{
  console.log('Starting VMs')
}

function stopVirtualMachines()
{
  console.log('Stopping VMs')
}
