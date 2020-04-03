// Program starts here. Creates a sample graph in the
// DOM node with the specified ID. This function is invoked
// from the onLoad event handler of the document (see below).

function main(container, sidebar)
{
  // Toastr options for displaying the toast
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
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
    var editor = new mxEditor();
    var graph = editor.graph;
    editor.setGraphContainer(container);

    var images_list = getImages();
    var i;
    for(i = 0; i < images_list.length; i++){
      var image = images_list[i].fields;
      var id = images_list[i].pk;
      addSidebarIcon(sidebar, graph, image, id);
    }
    // Populates toolbar
    populateToolbar(editor, graph);
    // Enables rubberband selection
    new mxRubberband(graph);
    // Disable highlight of cells when dragging from toolbar

    graph.setDropEnabled(false);
    graph.vertexLabelsMovable = true;
    graph.isCellSelectable = function(cable)
    {
      return !this.isCellLocked(cable);
    };

    var string = getXml();
    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();
    var xml_string = mxUtils.parseXml(string);
    var codec = new mxCodec(xml_string);
    codec.decode(xml_string.documentElement, graph.getModel());
    keyBindings(graph);
    //addMouseWheelZoom(graph) // re-enable this sometime soon
    getDeviceMenu(graph);
    getLegend();
    insertStatusLights(graph);
    graphListener(graph);
    handleDeviceFormSubmit(graph);
    handleEthernetFormSubmit(graph);
    //window.setInterval(function(){ displayGraph(graph); }, 2000); // update the graph every second
  }
};
// displayGraph gets called when the user clicks the refresh button
function displayGraph(graph)
{
  insertStatusLights(graph);
}

function getLegend()
{
  var legend = document.createElement('div');
  legend.style.position = 'absolute';
  legend.style.overflow = 'hidden';
  legend.style.width = '230px';
  legend.style.bottom = '56px';
  legend.style.height = '130px';
  legend.style.right = '20px';
  
  legend.style.background = 'black';
  legend.style.color = 'white';
  legend.style.fontSize = '10px';
  legend.style.padding = '4px';

  mxUtils.setOpacity(legend, 50);
  
  mxUtils.writeln(legend, '- Drag an image from the sidebar to the canvas to create a device');
  mxUtils.writeln(legend, '- Drag an ethernet cable/textbox from the toolbar to the canvas');
  mxUtils.writeln(legend, '- Rightclick and drag on canvas for panning');
  mxUtils.writeln(legend, '- Rightclick on selected device for device-specific options');
  mxUtils.writeln(legend, '- Click and drag a device to move and connect');
  document.body.appendChild(legend);
}

function addMouseWheelZoom(graph)
{
  mxEvent.addMouseWheelListener(function(evt, up)
  {
    if (up)
    {
      graph.zoomIn();
    }
    else
    {
      graph.zoomOut();
    }

    mxEvent.consume(evt);
  });
}

function graphListener(graph)
{
  // Updates the display
  graph.getModel().addListener('change', function(sender, evt){
    var changes = evt.getProperty('edit').changes;
    console.log(changes);
    connectEthernetCable(changes);
    // add code here to update labels of edges too?
    var encoder = new mxCodec();
    var result = encoder.encode(graph.getModel());

    // Experimented with Redis requests for a short period of time

    /*
    $.ajax({
      url: 'redis',
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      async: false,
      method: 'GET',
      success: function(response){
        console.log(response);
      },
      error: function(xhr, status, error) {
        var err = eval("(" + xhr.responseText + ")");
      }
    });
    */
    var xml = mxUtils.getXml(result);
    sendRequest(xml);
  });
}

function connectEthernetCable(changes)
{
  for(var i = 0; i < changes.length; i++){
    if(changes[i].constructor.name === "mxTerminalChange"){ // if the program detects a cable being (dis)connected to a device
      var cable_id = changes[i].cell.id;
      var terminal_cell = changes[i].terminal;
      var previous_cell = changes[i].previous;
      var endpoint = '';
      if(cell.source){
        endpoint = 'source';
      }
      else{
        endpoint = 'target';
      }
      if(compareDevices(terminal_cell, previous_cell) == false){ // if there are any changes in the device the cable is connected to
        connectCable(cable_id, terminal_cell, endpoint);
      }
    }
  }
}

function compareDevices(previous, terminal)
{
  // previous = any previous cells the cable might've been attached to
  // terminal = the current device, if any, which the cable might be attached to.

  if(previous){
    if(terminal){
      if(previous.id == terminal.id){ return true; } // no need to create another port for the same cable for the same device
      else{ return false;}
    }
    return false; // because there is no terminal but a previous cell, implying change
  }
  else{ // if there is no previous
    if(terminal){ return false; } // because there is no previous but a terminal cell, implying change
    return true; // both devices are null at this line but true returned as the program should not connect a cable to nothing
  }
}
/*
function getCableEndpoints(cell)
{
  if(cell != null){
    return cell.id;
  }
  return false;
}
*/

function connectCable(cell_id, device, endpoint)
{
  // device at this point could still be null, which implies it has been disconnected as it's already been verified there's a change in device
  if(device){
    $.ajax({
      url: 'connect_cable',
      data: {
        'cell_id': cell_id,
        'device': device.id,
        'endpoint': endpoint
      },
      async: false, 
      success: function(result){
        // Do nothing for now.
      }
    });
  }
  else{
    // 'disconnect' the cable as it's no longer attached on one end
    disconnectCable(cell_id, endpoint)
    // remove the endpoint here using the cable
  }
}

function disconnectCable(cell_id, endpoint)
{
  $.ajax({
    url: 'disconnect_cable',
    data: {
      'cell_id': cell_id,
      'endpoint': endpoint
    }
  });
}

function keyBindings(graph)
{
  var keyHandler = new mxKeyHandler(graph);
  keyHandler.bindKey(46, function(evt)
  {
    removeDevices(graph);
  });
}

function removeDevices(graph)
{
  if (graph.isEnabled())
  {
    var i;
    var selected_cells = graph.getSelectionCells();
    for(i = 0; i < selected_cells.length; i++){
      cell_id = selected_cells[i].getId();
      if(selected_cells[i].isVertex()){
        removeDevice(selected_cells[i]);
      }
      if(selected_cells[i].isEdge()){
        destroyNetworkBridge(selected_cells[i]);
      }
    }
    graph.removeCells();
    toastr.success('Devices removed');
  }
}

function destroyNetworkBridge(cell)
{
  var cell_id = cell.getId();
  $.ajax({
    url: 'destroy_network_bridge',
    data: {'cell_id': cell_id},
    async: false,
    success: function(result){
      if(result['response'] == 'success'){
        toastr.success('Ethernet Cable removed successfully');
        // deal with cell removal here
      }
      else{
        toastr.error(`Unable to remove ethernet cable: ${result['error']}`);
      }
    }
  });
}

function getImages()
{
  var output = null;
  $.ajax({
    url: "get_images",
    async: false,
    success: function(result){
      output = result['disk_images'];
    }
  });
  return output;
}

function removeDevice(cell)
{
  cell_id = cell.getId();
  $.ajax({
    url: 'remove_device',
    data: {'cell_id':cell_id},
    async: false,
    success: function(result){
      if(result['result'] == 'success'){ // if the task was successful
        toastr.success('Device removed successfully');
      }
      else{ // handle error code here
        toastr.error('Error removing Device');
      }
    }
  });
}

function removeCable(cell)
{
  
}

function sendRequest(xml)
{
  $.ajax({
    url: "home",
    async: false,
    data: {'XML': xml},
    success: function(result){
      console.log(result)
    }
  });
}

function getXml()
{
  var output = "";
  $.ajax({
    url: "retrieveXml",
    async: false,
    dataType: "json",
    contentType: "text/xml",
    success: function(result){
      output = result["response"];
    }
  });
  return output;
}

function insertStatusLights(graph)
{
  cells = graph.getChildVertices(graph.getDefaultParent());
  var i = 0;
  for(i = 0; i < cells.length; i++){
    var cell = cells[i];
    insertStatusLight(graph, cell);
  }
}

function insertStatusLight(graph, cell)
{
  children = cell.children;
  var id = cell.getId();
  var light = getStatusLight(id);
  var style = ''
  if(light != null){
    style = `port;shape=image;image=${light};spacingLeft=18;`;
  }
  if(children){ // If the cell is a textbox, cable or anything that doesn't have a status light
    graph.getModel().setStyle(children[0], style);
  }
}

function getStatusLight(cell_id)
{
  var output = null;
  $.ajax({
    url: 'get_device_status',
    data: {'cell_id': cell_id},
    async: false,
    dataType: "json",
    success: function(result){
      var device_status = result['device_status'];
      output = getVector(device_status); // getVector is in sidebar.js
    }
  });
  //console.log(output);
  return output
}

function handleDeviceFormSubmit(graph)
{
  $("#device_form").on('submit', function(e) {
    e.preventDefault();
    var name = document.getElementById('device_name_id').value;
    var ram = document.getElementById('ramSlider').value;
    var disk_size = document.getElementById('diskSizeSlider').value;
    var cpus = document.getElementById('cpusSlider').value;
    var disk_image = document.getElementById('disk_image_id').value;
    var cell_id = document.getElementById('cell_id').value;
    var csrf = $('input[name=csrfmiddlewaretoken]').val();
    //var ethernetports = document.getElementById('ethernetSlider').value;
    $.ajax({
      url: 'post_device_form',
      type: 'POST',
      data: {
        name: name,
        ram: ram,
        disk_size: disk_size,
        cpus: cpus,
        disk_image: disk_image,
        cell_id: cell_id,
        csrfmiddlewaretoken: csrf,
        //ethernetports: ethernetports
      },
      success: function(result){
        if(result['response'] == 'error'){
          // remove the cell if there is an error in database submission or VM creation
          if (graph.isEnabled()){ graph.removeCells(); }
          toastr.error(`Error adding device: ${result['message']}`);
        }
        if(result['response'] == 'success'){
          changeCellLabel(graph.getModel(),cell_id,name);
          toastr.success('Device added successfully');
        }
        $('#device_modal').modal('hide');
      },
    });
  });
}

function changeCellLabel(model, cell_id, name)
{
  var cell = model.getCell(cell_id);
  model.setValue(cell, name);
}

function handleEthernetFormSubmit(graph)
{
  $('#ethernet_form').on('submit', function(e){
    e.preventDefault();
    var name = document.getElementById('ethernet_name').value;
    var deviceoneethernet = document.getElementById('device_one_ethernet').value;
    var devicetwoethernet = document.getElementById('device_two_ethernet').value;
    console.log(deviceoneethernet);
    console.log(devicetwoethernet);
    addNetworkBridge(name, deviceoneethernet, devicetwoethernet);
    // add logic here for making the AJAX requests to create a network bridge
    $('#ethernet_modal').modal('hide');
  });
}
