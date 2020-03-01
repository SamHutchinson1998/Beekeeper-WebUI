// nodeJS libraries
var express = require('express');
var redis = require('redis');

var client = redis.createClient();
var app = express();

app.get('/get', function(req, res){
  var xml_string = client.get('beekeeper_xml')
  res.json({xml:xml_string})
});

app.listen(3000);
