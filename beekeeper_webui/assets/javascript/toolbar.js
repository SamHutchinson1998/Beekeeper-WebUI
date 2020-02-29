function populateToolbar(editor, graph)
{
  var toolbar = document.getElementById('toolbarContainer');
  addToolbarItem(toolbar, graph, '../static/devices/ethernet_cable.svg', 'cable');
  addToolbarItem(toolbar, graph, '../static/devices/Label.svg', 'textbox');
  addToolbarButton(toolbar, '../static/devices/refresh.svg', 'refresh')
  addToolbarButton(toolbar, '../static/devices/start_button.svg', 'start', graph, editor);
  addToolbarButton(toolbar, '../static/devices/stop_button.svg', 'stop', graph, editor);
  addToolbarButton(toolbar, '../static/devices/zoom_in.svg', 'Zoom In', graph, editor);
  addToolbarButton(toolbar, '../static/devices/zoom_out.svg', 'Zoom Out', graph, editor);

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
          cell = graph.insertVertex(parent, null, node, x, y, 120, 30, style);
          cell.setConnectable(false);
        break;
        case 'cable':
          style = `strokeWidth=6;strokeColor=black;endArrow=none;html=1;`;
          cell = new mxCell('Test Cable', new mxGeometry(0, 0, 150, 150), style); // last two values are height and width respectively
          cell.geometry.setTerminalPoint(new mxPoint(0, 170), true); // source point
          cell.geometry.setTerminalPoint(new mxPoint(180, 0), false); // target point
          cell.geometry.relative = true;
          cell.edge = true;
          cell.setAttribute('type', 'cable'); // Not working!
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

function addToolbarButton(toolbar, image, type, graph, editor)
{
  var button = document.createElement('button');
  button.style.background = 'transparent';
  button.style.color = '#FFFFFF';
  button.style.border = 'none';
  button.style.height = '25px';
  button.style.width = '25px';
  button.setAttribute('id', 'toolbarItem');
  var img = document.createElement('img');
  img.setAttribute('src', image);
  img.style.width = '18px';
  img.style.height = '18px';
  img.style.Align = 'center';
  button.appendChild(img);

  switch(type)
  {
    case 'start':
      startVirtualMachines(button, graph);
      button.title = `${type} selected/all devices`;
    break;
    case 'stop':
      stopVirtualMachines(button, graph);
      button.title = `${type} selected/all devices`;
    break;
    case 'Zoom Out':
      zoomButtons(button, 'zoomOut', editor);
      button.title = `${type}`;
    case 'Zoom In':
      zoomButtons(button, 'zoomIn', editor);
      button.title = `${type}`;
    case 'refresh':
      //$('#graphBody').load(" #graphBody > *");
    break;
  }
  toolbar.appendChild(button);
}

function zoomButtons(button, action, editor)
{
  mxEvent.addListener(button, 'click', function(evt){
    editor.execute(action);
  });
}

function startVirtualMachines(button, graph)
{
  button.addEventListener("click", function(){
    var cells = graph.getSelectionCells();
    var cellArry = [];
    var i;
    for(i = 0; i < cells.length; i++){
      id = cells[i].getId();
      cellArry.push(id);
    }
    $.ajax({
      url: 'change_vm_state',
      async: false,
      data: {
        'state': 'start',
        'cells': JSON.stringify(cellArry)
      },
      success: function(result){
        alert('Devices successfully switched on');
      }
    });
  })
}

function stopVirtualMachines(button, graph)
{
  button.addEventListener("click", function(){
    var cells = graph.getSelectionCells();
    var cellArry = [];
    var i;
    for(i = 0; i < cells.length; i++){
      id = cells[i].getId();
      cellArry.push(id);
    }
    $.ajax({
      url: 'change_vm_state',
      async: false,
      data: {
        'state': 'stop',
        'cells': JSON.stringify(cellArry)
      },
      success: function(result){
        alert('Devices successfully switched off');
      }
    });
  });
}
