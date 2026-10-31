import { defineConfig } from 'vite';
import { transferFifoMessage, getFifoStatus, getFifoHistory, getFifoDisplay, resetFifoState } from './server/fifo-backend.js';

export default defineConfig({
  server: {
    port: 5173,
    open: true,
    cors: true
  },
  plugins: [
    {
      name: 'linux-fifo-api',
      configureServer(server) {
        server.middlewares.use(async (req, res, next) => {
          const url = req.url || '';

          // CORS Headers for any origin (e.g. file:// or localhost)
          res.setHeader('Access-Control-Allow-Origin', '*');
          res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
          res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

          if (req.method === 'OPTIONS') {
            res.statusCode = 204;
            res.end();
            return;
          }

          if (url.startsWith('/api/fifo/status') && req.method === 'GET') {
            try {
              const status = await getFifoStatus();
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(status));
            } catch (err) {
              res.setHeader('Content-Type', 'application/json');
              res.statusCode = 500;
              res.end(JSON.stringify({ error: err.message }));
            }
            return;
          }

          if (url.startsWith('/api/fifo/display') && req.method === 'GET') {
            try {
              const display = await getFifoDisplay();
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(display));
            } catch (err) {
              res.setHeader('Content-Type', 'application/json');
              res.statusCode = 500;
              res.end(JSON.stringify({ error: err.message }));
            }
            return;
          }

          if (url.startsWith('/api/fifo/history') && req.method === 'GET') {
            try {
              const history = await getFifoHistory();
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(history));
            } catch (err) {
              res.setHeader('Content-Type', 'application/json');
              res.statusCode = 500;
              res.end(JSON.stringify({ error: err.message }));
            }
            return;
          }

          if (url.startsWith('/api/fifo/reset') && req.method === 'POST') {
            try {
              const resObj = await resetFifoState();
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(resObj));
            } catch (err) {
              res.setHeader('Content-Type', 'application/json');
              res.statusCode = 500;
              res.end(JSON.stringify({ error: err.message }));
            }
            return;
          }

          if (url.startsWith('/api/fifo/write') && req.method === 'POST') {
            let body = '';
            req.on('data', chunk => { body += chunk; });
            req.on('end', async () => {
              try {
                let parsed = {};
                if (body && body.trim().length > 0) {
                  parsed = JSON.parse(body);
                }
                const result = await transferFifoMessage(parsed.message);
                res.setHeader('Content-Type', 'application/json');
                if (!result.success) {
                  res.statusCode = (result.error && result.error.includes('currently being used')) ? 409 : 500;
                } else {
                  res.statusCode = 200;
                }
                res.end(JSON.stringify(result));
              } catch (err) {
                res.setHeader('Content-Type', 'application/json');
                res.statusCode = 500;
                res.end(JSON.stringify({ success: false, error: err.message }));
              }
            });
            return;
          }

          next();
        });
      }
    }
  ]
});
