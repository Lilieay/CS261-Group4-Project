const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const page = fs.readFileSync(path.join(__dirname, '../public/index.html'));

http.createServer((req, res) => {
  if (req.url !== '/') {
    res.writeHead(404);
    return res.end();
  }

  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(page);
}).listen(3000, '127.0.0.1', () => {
  console.log('Frontend: http://127.0.0.1:3000');
});
