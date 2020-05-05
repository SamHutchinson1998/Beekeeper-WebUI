function getDeviceMenu(graph)
{
  graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
  {
    if(cell){ // A user could right-click on a blank area
      if(isCellDevice(cell)){
        if(cell.children[1]){
          menu.addItem('Disconnect from the internet', null, function(){
            disconnectFromTheInternet(evt, graph, cell);
          });
        } else {
          menu.addItem('Connect to the internet', null, function(){
            connectToTheInternet(graph, cell);
          });
        }
        menu.addItem('Telnet', null, function(){
          getTelnet(cell);
        });
        menu.addItem('VNC', null, function(){
          getVNC(cell);
        });
        menu.addItem('Delete', null, function(){
          removeDevices(graph);
        });
      }
    }
  }
}

function connectToTheInternet(graph, cell)
{
  image = getVector('nat');
  var cell_id = cell.getId();
  var style = `port;shape=image;image=${image};spacingLeft=12;`;

  $.ajax({
    url: 'connect_device_to_internet',
    data: {'cell_id': cell_id},
    async: false,
    success: function(result){
      if(result['result'] == 'success'){
        var nat_logo = graph.insertVertex(cell, null, '', 1, 0.35, 16, 16, style, true);
        nat_logo.geometry.offset = new mxPoint(-8, -8);
        toastr.success('Device connected to the internet');
      }
      else{
        toastr.error('Unable to connect device to the internet');
      }
    }
  });
}

function disconnectFromTheInternet(evt, graph, cell)
{
  var cell_id = cell.getId();
  var nat_cell = cell.children[1]; // The cell which is the nat icon
  //cell.remove(1) // Index of the nat icon, as a child of the device vertex
  $.ajax({
    url: 'disconnect_device_from_internet',
    data: {'cell_id': cell_id},
    async: false,
    success: function(result){
      if(result['result'] == 'success'){
        graph.removeCells([nat_cell]);
        mxEvent.consume(evt);
        toastr.success('Device disconnected from the internet');
      }
      else{
        toastr.error('Unable to disconnect device from the internet');
      }
    }
  });
}

function getTelnet(cell)
{
  $.ajax({
    url: 'lookup_device',
    data: {'cell_id': cell.getId()},
    async: false,
    success: function(result){
      if(result['response'] != 'Not Found'){
        var console_port = result['console_port'];
        window.open(`telnet://${window.location.host}:${console_port}`)
      }
    }
  });
  window.open
}

function getVNC(cell)
{
  var id = cell.getId();
  //window.location = '/get_device_vnc?cell_id='+id
  window.open( '/get_device_vnc?cell_id='+id, '_blank');
}

