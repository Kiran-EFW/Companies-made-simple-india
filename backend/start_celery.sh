#!/bin/sh
# Start a minimal HTTP health-check server on $PORT alongside the Celery process.
# Cloud Run requires all services to respond on PORT; Celery doesn't serve HTTP.

python3 -c "
import http.server, threading, os
port = int(os.environ.get('PORT', 8080))
handler = http.server.BaseHTTPRequestHandler
class H(handler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a): pass
threading.Thread(target=http.server.HTTPServer(('0.0.0.0', port), H).serve_forever, daemon=True).start()
" &

# Run the celery command passed as arguments
exec "$@"
