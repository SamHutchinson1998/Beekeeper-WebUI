// nodeJS libraries
var express = require('express');
var http = require('http');
var redis = require('redis');

var client = redis.createClient();
var app = express();

/*
app.options("/*", function(req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With');
    res.sendStatus(200);
});

app.all('*', function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    next();
});
*/

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.get('/get', function (req, res) {
  res.type('json');
  //res.setHeader('Content-Type', 'application/json');
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

