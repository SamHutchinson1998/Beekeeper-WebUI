// Program starts here. Creates a sample graph in the
// DOM node with the specified ID. This function is invoked
// from the onLoad event handler of the document (see below).
function main(container, sidebar)
{
  // Checks if the browser is supported
  if (!mxClient.isBrowserSupported())
  {
    // Displays an error message if the browser is not supported.
    mxUtils.error('Browser is not supported!', 200, false);
  }
  else
  {
    mxConstants.MIN_HOTSPOT_SIZE = 16;
    mxConstants.DEFAULT_HOTSPOT = 1;
    mxGraphHandler.prototype.guidesEnabled = true;

    // Disables the built-in context menu
    mxEvent.disableContextMenu(container);

    // Creates the graph inside the given container
    var graph = new mxGraph(container);
    var images_list = getDevices();
    var i;
    for(i = 0; i < images_list.length; i++){
      var image = images_list[i].fields;
      var id = images_list[i].pk;
      addSidebarIcon(sidebar, graph, image, id);
    }
    // Populates toolbar
    populateToolbar(graph);
    // Enables rubberband selection
    new mxRubberband(graph);
    // Disable highlight of cells when dragging from toolbar
    graph.setDropEnabled(false);
    graph.isCellSelectable = function(cell)
    {
      return !this.isCellLocked(cell);
    };

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();
    var string = getXml();
    //console.log(string);
    var xml_string = mxUtils.parseXml(string);
    var codec = new mxCodec(xml_string);
    codec.decode(xml_string.documentElement, graph.getModel());
    keyBindings(graph)
    graphListener(graph)
  }
};

function getVector(device)
{
  switch(device.devicetype)
  {
    case "pc":
      return '../static/devices/computer.svg';
    case "switch":
      return '../static/devices/switch.svg';
    case "router":
      return '../static/devices/router.svg';
    case 'server':
      return '../static/devices/server.svg';
    case "mlswitch":
    default:
      return '../static/devices/computer.svg';
  }
}

function graphListener(graph)
{
  // Updates the display
  graph.getModel().addListener('change', function(){
    var encoder = new mxCodec();
    var result = encoder.encode(graph.getModel());
    var xml = mxUtils.getXml(result);
    //console.log('xml', xml);
    //console.log('raw_data', result)
    sendRequest(xml);
  });
}

function addSidebarIcon(sidebar, graph, disk_image, image_id)
{
  var image = getVector(disk_image);
  var funct = function(graph, evt, cell, x, y)
  {
    var parent = graph.getDefaultParent();
    var model = graph.getModel();
    
    var device = null;
    var stylesheet = `shape=image;image=${image};` +
    `verticalLabelPosition=bottom;verticalAlign=top;`;
    model.beginUpdate();
    try
    {
      device = graph.insertVertex(parent, null, disk_image.name, x, y, 100, 100, stylesheet);
      device.setConnectable(true);
    }
    finally
    {
      model.endUpdate();
    }
    graph.setSelectionCell(device);
    cell_id = graph.getSelectionCell().getId();
    console.log(cell_id);
    getDeviceModal(image_id, cell_id, graph);
  }
  var wrapper = document.createElement('div');
  wrapper.setAttribute('data-image-tags',`${disk_image.name},${disk_image.devicetype}`);


  var icon = document.createElement('img');
  icon.setAttribute('src', image);
  icon.setAttribute('data-image-name', disk_image.name);
  icon.setAttribute('data-image-id', image_id);
  icon.setAttribute('id', 'sidebarItem');
  icon.title = 'Drag this onto the canvas to create a new device';
  wrapper.appendChild(icon);

  var description = document.createElement('div');
  description.innerHTML = disk_image.name;
  description.setAttribute('align','center');
  wrapper.appendChild(description); 

  sidebar.appendChild(wrapper);

  var dragElement = document.createElement('div');
  dragElement.style.border = 'dashed black 1px';
  dragElement.style.width = '150px';
  dragElement.style.height = '150px';

  var ds = mxUtils.makeDraggable(icon,graph,funct,dragElement,0,0,true,true);
  ds.setGuidesEnabled(true);
}

function populateToolbar(graph)
{
  var toolbar = document.getElementById('toolbarContainer');
  addToolbarIcon(toolbar, graph, '../static/devices/ethernet_cable.svg', 'draggable');
}

function addToolbarIcon(toolbar, graph, tool, tooltype)
{
  var funct = function(graph, evt, cell, x, y)
  {
    var parent = graph.getDefaultParent();
    var model = graph.getModel();
    var cable = null;
    var style = `strokeColor=red;`;
    model.beginUpdate();
    try
    {
      cable = graph.insertEdge(parent, null, '', new mxPoint(x,y), new mxPoint(x, y+50));
    }
    finally
    {
      model.endUpdate();
    }
    graph.setSelectionCell(cable);
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


function keyBindings(graph)
{
  var keyHandler = new mxKeyHandler(graph);
  keyHandler.bindKey(46, function(evt)
  {
    if (graph.isEnabled())
    {
      var i;
      var selected_cells = graph.getSelectionCells();
      for(i = 0; i < selected_cells.length; i++){
        cell_id = selected_cells[i].getId();
        removeDevice(cell_id);
      }
      graph.removeCells();
    }
  });
}

function getDeviceModal(image_id, cell_id, graph)
{
  $('#device_modal').modal('show');
  $(document).ready(function(){
    $('#device_modal').on("hide.bs.modal", function () {
      if (graph.isEnabled())
      {
        graph.removeCells();
      }
    });
    $('#device_modal').on("shown.bs.modal", function(event){
      var id_string = image_id.toString();
      var cell_id_string = cell_id.toString();
      document.getElementById('disk_image_id').value = id_string;
      document.getElementById('cell_id').value = cell_id_string;
    });
  });
}

function getDevices()
{
  var output = null;
  $.ajax({
    url: "get_devices",
    async: false,
    success: function(result){
      output = result['disk_images'];
    }
  });
  return output;
}

function removeDevice(cell_id)
{
  $.ajax({
    url: 'remove_device',
    data: {'cell_id':cell_id},
    async: false,
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

function sendRequest(xml)
{
  $.ajax({
    url: "home",
    data: {'XML': xml},
    success: function(result){
    }
  });
}

function getXml()
{
  var output = "";
  $.ajax({
    url: "retrieveXml",
    async: false,
    contentType: "text/xml",
    success: function(result){
      output = result["response"];
    }
  })
  return output;
}
