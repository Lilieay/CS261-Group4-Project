const express = require('express');
const { error } = require('node:console');
const path = require('node:path');

const app = express();

app.use(express.static(path.join(__dirname, '../public')));

app.listen(5000, '127.0.0.1', () => {
 
  console.log('Frontend: http://127.0.0.1:5000');
});