// This library isn't actually used by beekeeper anymore but is being kept here for research purposes

// nodeJS libraries
var express = require('express');
var http = require('http');
var redis = require('redis');

var client = redis.createClient();
var app = express();

app.all('*', function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    next();
});

app.get('/getredis', function (req, res) {
  res.type('json');
  getRedisXml(client, res);
});

function getRedisXml(client, res)
{
  var response = client.get('beekeeper_xml', function (error, result) {
    if (error) {
        console.log(error);
        throw error;
    }
    console.log(result);
    res.json({xml:result});
  });
}

app.listen(3000, function(){
  console.log("server listening at localhost:3000");
});

