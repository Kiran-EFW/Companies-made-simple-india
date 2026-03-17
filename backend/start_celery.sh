#!/bin/sh
# Start a minimal HTTP health-check server on $PORT alongside the Celery process.
# Cloud Run requires all services to respond on PORT; Celery doesn't serve HTTP.

python3 -c "
import http.server, os
port = int(os.environ.get('PORT', 8080))
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a): pass
http.server.HTTPServer(('0.0.0.0', port), H).serve_forever()
" &

# Run the celery command passed as arguments
exec "$@"
