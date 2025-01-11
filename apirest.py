import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

TC_SCRIPT_PATH = '/home/vnx/script_tc.py'

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/modificar_tc':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                command = data.get('command')
                args_value = data.get('args', '')
                interface_value = data.get('interface', '')

                if not command or not interface_value:
                    self._send_response(400, {
                        'status': 'error',
                        'mensaje': 'Faltan parametros requeridos (command o interface).'
                    })
                    return

                comando = 'python3 {} --command {} --args "{}" --interface {}'.format(
                    TC_SCRIPT_PATH, command, args_value, interface_value
                )
                proceso = subprocess.Popen(
                    comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                salida, errores = proceso.communicate()

                if proceso.returncode != 0:
                    self._send_response(500, {
                        'status': 'error',
                        'mensaje': errores.decode().strip()
                    })
                else:
                    self._send_response(200, {
                        'status': 'success',
                        'mensaje': salida.decode().strip()
                    })

            except Exception as e:
                self._send_response(500, {
                    'status': 'error',
                    'mensaje': str(e)
                })
        else:
            self._send_response(404, {
                'status': 'error',
                'mensaje': 'Ruta no encontrada'
            })

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Servidor iniciado en el puerto {}'.format(port))
    httpd.serve_forever()

if __name__ == '__main__':
    run()

