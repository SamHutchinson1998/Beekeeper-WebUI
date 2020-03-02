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
    var editor = new mxEditor();
    //var graph = new mxGraph(container);
    var graph = editor.graph;
    editor.setGraphContainer(container);

    var images_list = getDevices();
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
    addMouseWheelZoom(graph)
    getDeviceMenu(graph);
    getLegend();
    insertStatusLights(graph);
    graphListener(graph);
    window.setInterval(function(){ displayGraph(graph); }, 2000); // update the graph every second
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
  graph.getModel().addListener('change', function(){
    var encoder = new mxCodec();
    var result = encoder.encode(graph.getModel());
    // work on making Redis server requests here?
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
        removeDevice(cell_id);
      }
    }
    graph.removeCells();
  }
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
  })
  //console.log(output);
  return output
}
