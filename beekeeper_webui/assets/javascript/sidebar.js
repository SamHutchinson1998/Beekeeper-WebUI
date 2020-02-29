function searchDevices()
{
  var value = document.getElementById('searchBar').value.toLowerCase();
  var sidebar = document.getElementById('sidebarContainer');
  //console.log('searching sidebar...')
  var children = sidebar.childNodes;
  console.log(children);
  hideSidebarChildNodes(children, value);
}

function hideSidebarChildNodes(children, value)
{
  var i;
  for(i = 0; i < children.length; i++){
    var child = children[i];
    var id = child.id;
    if (id == 'deviceItem'){
      var tags = $(child).attr('data-image-tags');
      if (!(tags.includes(value) && value.length >= 0)){
        child.style.display = 'none';
      }
      else{
        child.style.display = 'inline';
      }
    }
  }
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
    `verticalLabelPosition=bottom;verticalAlign=top;labelHandleSize=8;`;
    model.beginUpdate();
    try
    {
      device = graph.insertVertex(parent, null, disk_image.name, x, y, 100, 100, stylesheet);
      device.setConnectable(true);
      device.setAttribute('type', 'vertex'); // Not working!

      var status_light = graph.insertVertex(device, null, '', 1, 0.15, 16, 16,
        'port;shape=image;image=../static/devices/status_unknown.svg;spacingLeft=18', true);
      status_light.geometry.offset = new mxPoint(-8, -8);
    }
    finally
    {
      model.endUpdate();
    }
    graph.setSelectionCell(device);
    cell_id = graph.getSelectionCell().getId();
    getDeviceModal(image_id, cell_id, graph);
  }
  var wrapper = document.createElement('div');
  wrapper.setAttribute('data-image-tags',`${disk_image.name.toLowerCase()},${disk_image.devicetype.toLowerCase()}`);
  wrapper.setAttribute('id', 'deviceItem')
  wrapper.style.display = 'inline';

  var icon = document.createElement('img');
  icon.setAttribute('src', image);
  icon.setAttribute('data-image-name', disk_image.name);
  icon.setAttribute('data-image-id', image_id);
  icon.setAttribute('id', 'sidebarItem');
  icon.setAttribute('align', 'center');
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


function getVector(device)
{
  var filepath = '../static/devices/';
  switch(device.devicetype)
  {
    case "pc":
      return `${filepath}computer.svg`;
    case "switch":
      return `${filepath}switch.svg`;
    case "router":
      return `${filepath}router.svg`;
    case 'server':
      return `${filepath}server.svg`;
    case 'status_unknown':
      return `${filepath}status_unknown.svg`;
    case 'status_offline':
      return `${filepath}status_offline`;
    case 'status_suspended':
      return `${filepath}status_suspended`;
    case 'status_online':
      return `${filepath}status_online`;
    case "mlswitch":
    default:
      return `${filepath}computer.svg`;
  }
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
