const https = require('https');

exports.handler = async (event) => {
  const path = event.queryStringParameters?.path || '/fixtures';
  const params = new URLSearchParams(event.queryStringParameters || {});
  params.delete('path');
  const url = `https://v3.football.api-sports.io${path}?${params.toString()}`;

  return new Promise((resolve) => {
    const req = https.get(url, {
      headers: {
        'x-apisports-key': '09ee8ca7bbb9485ca2200028df5f958c',
        'x-rapidapi-key': '09ee8ca7bbb9485ca2200028df5f958c',
        'x-rapidapi-host': 'v3.football.api-sports.io'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
          },
          body: data
        });
      });
    });
    req.on('error', (e) => {
      resolve({ statusCode: 500, body: JSON.stringify({ error: e.message }) });
    });
    req.setTimeout(10000, () => { req.destroy(); resolve({ statusCode: 504, body: JSON.stringify({ error: 'Timeout' }) }); });
  });
};
