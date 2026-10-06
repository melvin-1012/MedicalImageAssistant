"""
MediSight AI - Development Local Web Server
Runs a lightweight HTTP server on port 8000 to preview the hospital landing page.
Usage:
    py serve.py
"""

import http.server
import socketserver
import os
import sys

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class HospitalStaticServer(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable caching-free development headers
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    try:
        with socketserver.TCPServer(("", PORT), HospitalStaticServer) as httpd:
            print("=" * 65)
            print("  MediSight AI - Multimodal Medical Image Intelligence")
            print(f"  Local Development Server running at: http://localhost:{PORT}")
            print(f"  Document Root: {DIRECTORY}")
            print("  Press Ctrl+C to terminate.")
            print("=" * 65)
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048 or "Address already in use" in str(e):
            alt_port = 8080
            with socketserver.TCPServer(("", alt_port), HospitalStaticServer) as httpd:
                print(f"Port 8000 busy, running on: http://localhost:{alt_port}")
                httpd.serve_forever()
        else:
            raise

if __name__ == '__main__':
    main()
