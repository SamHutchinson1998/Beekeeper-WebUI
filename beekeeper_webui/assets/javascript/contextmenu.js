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
        menu.addItem('Get SSH Link', null, function(){
          getSSH(cell);
        });
        menu.addItem('VNC', null, function(){
          getVNC(cell);
        });
        menu.addItem('Download', null, function(){
          deployDevice(cell);
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

function getSSH(cell)
{
  var label = cell.getValue();
  $.ajax({
    url: 'lookup_device',
    data: {'cell_id': cell.getId()},
    success: function(result){
      if(result['response'] != "Not Found"){
        alert(`Open up a terminal and input the following:\nssh -t [user]@${window.location.host} sudo virsh console ${label}\n\n where [user] is your account on the server`);
      }
      else{
        toastr.error('Unable to offer SSH at this time');
      }
    }
  });
}

function getVNC(cell)
{
  var id = cell.getId();
  //window.location = '/get_device_vnc?cell_id='+id
  window.open( '/get_device_vnc?cell_id='+id, '_blank');
}

function deployDevice(cell)
{
  var id = cell.getId();
  $.ajax({
    url: 'download_device',
    data: {'cell_id': id},
    success: function(result){
      toastr.warning('Download in progress');
    }
  });
}

