import http.server
import socketserver
import psutil
import csv
import io
import datetime


class ServiceListHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            services = []
            for service in psutil.win_service_iter():
                service_data = {
                    'Name': service.name(),
                    'Display Name': service.display_name(),
                    'Status': service.status(),
                    'Hostname': socket.gethostname(),
                    'Timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                services.append(service_data)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Create a CSV file in memory
            output = io.StringIO()
            csv_writer = csv.writer(output)
            csv_writer.writerow(['Name', 'Display Name', 'Status', 'Hostname', 'Timestamp'])
            for service in services:
                csv_writer.writerow([service['Name'], service['Display Name'], service['Status'], service['Hostname'],
                                     service['Timestamp']])

            csv_content = output.getvalue().encode()

            # Add a link to download the CSV
            self.wfile.write(b'<html><body><h1>Windows Services</h1>')
            self.wfile.write(b'<a href="/services.csv" download>Download CSV</a>')
            self.wfile.write(b'<pre>')
            self.wfile.write(csv_content)
            self.wfile.write(b'</pre></body></html>')

        elif self.path == '/services.csv':
            # Serve the CSV file for download
            self.send_response(200)
            self.send_header('Content-type', 'text/csv')
            self.send_header('Content-Disposition', 'attachment; filename="services.csv"')
            self.end_headers()
            with open('services.csv', 'rb') as csv_file:
                self.wfile.write(csv_file.read())
        else:
            super().do_GET()


if __name__ == '__main__':
    import socket

    port = 8080
    with socketserver.TCPServer(("", port), ServiceListHandler) as httpd:
        print(f"Serving at http://127.0.0.1:{port}")
        httpd.serve_forever()
