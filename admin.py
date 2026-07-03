#!/usr/bin/env python3
"""
Dashboard Server — Detalles Aleydy 🎀
Servidor local que usa el service account de Firebase para gestionar productos y pedidos.
Ejecutar: python3 admin.py
Acceder: http://localhost:5050
"""

import json
import os
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import firebase_admin
from firebase_admin import credentials, firestore

# === CONFIGURACION ===
PORT = 5050
AUTH_TOKEN = 'aleydy-admin-2026'  # Token simple para el dashboard
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

# === INICIALIZAR FIREBASE ===
import firebase_admin as fb_admin
try:
    app = fb_admin.get_app()
    fb_admin.delete_app(app)
except ValueError:
    pass
cred = credentials.Certificate('/home/will/.hermes/keys/detalles-aleydy-firebase-sa.json')
fb_admin.initialize_app(cred)
db = firestore.client()

# === SERVIDOR ===
class DashboardHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api_get(path)
            return
        
        # Servir archivos estaticos
        if path == '/' or path == '':
            path = '/dashboard.html'
        
        file_path = os.path.join(STATIC_DIR, path.lstrip('/'))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type = 'text/html'
            if path.endswith('.css'): content_type = 'text/css'
            elif path.endswith('.js'): content_type = 'application/javascript'
            elif path.endswith('.json'): content_type = 'application/json'
            elif path.endswith('.svg'): content_type = 'image/svg+xml'
            elif path.endswith('.png'): content_type = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'): content_type = 'image/jpeg'
            elif path.endswith('.webp'): content_type = 'image/webp'
            
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if not path.startswith('/api/'):
            self.send_error(404)
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        try:
            data = json.loads(body)
        except:
            data = {}
        
        self.handle_api_post(path, data)
    
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if not path.startswith('/api/'):
            self.send_error(404)
            return
        
        self.handle_api_delete(path)
    
    def check_auth(self):
        """Verificar token de autorizacion en header o cookie."""
        auth_header = self.headers.get('Authorization', '')
        if auth_header == 'Bearer ' + AUTH_TOKEN:
            return True
        
        # Cookie
        cookie = self.headers.get('Cookie', '')
        if 'auth_token=' + AUTH_TOKEN in cookie:
            return True
        
        return False
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    # === API GET ===
    def handle_api_get(self, path):
        # Auth
        if path == '/api/auth/check':
            self.send_json({'ok': self.check_auth()})
            return
        
        # Login simple
        if path == '/api/auth/login':
            qs = parse_qs(urlparse(self.path).query)
            token = qs.get('token', [''])[0]
            if token == AUTH_TOKEN:
                self.send_json({'ok': True, 'cookie': 'auth_token=' + AUTH_TOKEN})
            else:
                self.send_json({'ok': False, 'error': 'Token invalido'}, 401)
            return
        
        # Productos
        if path == '/api/productos':
            if not self.check_auth():
                self.send_json({'error': 'No autorizado'}, 401)
                return
            productos = [{'id': doc.id, **doc.to_dict()} for doc in db.collection('productos').order_by('categoria').get()]
            self.send_json(productos)
            return
        
        # Categorias
        if path == '/api/categorias':
            if not self.check_auth():
                self.send_json({'error': 'No autorizado'}, 401)
                return
            categorias = [{'id': doc.id, **doc.to_dict()} for doc in db.collection('categorias').order_by('orden').get()]
            self.send_json(categorias)
            return
        
        # Pedidos
        if path == '/api/pedidos':
            if not self.check_auth():
                self.send_json({'error': 'No autorizado'}, 401)
                return
            pedidos = [{'id': doc.id, **doc.to_dict()} for doc in db.collection('pedidos').order_by('fecha', direction=firestore.Query.DESCENDING).limit(50).get()]
            self.send_json(pedidos)
            return
        
        self.send_error(404)
    
    # === API POST ===
    def handle_api_post(self, path, data):
        if path == '/api/auth/login':
            token = data.get('token', '')
            if token == AUTH_TOKEN:
                self.send_json({'ok': True, 'token': AUTH_TOKEN})
            else:
                self.send_json({'ok': False, 'error': 'Token invalido'}, 401)
            return
        
        if not self.check_auth():
            self.send_json({'error': 'No autorizado'}, 401)
            return
        
        # Guardar producto
        if path == '/api/productos':
            prod_id = data.get('id') or data.get('nombre', '').lower().replace(' ', '-')
            doc_data = {
                'nombre': data.get('nombre', ''),
                'categoria': data.get('categoria', ''),
                'descripcion': data.get('descripcion', ''),
                'precio': float(data.get('precio', 0)),
                'foto': data.get('foto', ''),
                'badge': data.get('badge', ''),
                'destacado': data.get('destacado', False),
                'activo': data.get('activo', True),
                'fechaActualizacion': firestore.SERVER_TIMESTAMP
            }
            db.collection('productos').document(prod_id).set(doc_data, merge=True)
            self.send_json({'ok': True, 'id': prod_id})
            return
        
        # Guardar categoria
        if path == '/api/categorias':
            cat_id = data.get('id') or data.get('nombre', '').lower().replace(' ', '-')
            doc_data = {
                'nombre': data.get('nombre', ''),
                'orden': int(data.get('orden', 0))
            }
            db.collection('categorias').document(cat_id).set(doc_data, merge=True)
            self.send_json({'ok': True, 'id': cat_id})
            return
        
        # Actualizar estado de pedido
        if path == '/api/pedidos/estado':
            pedido_id = data.get('id')
            estado = data.get('estado')
            if pedido_id and estado:
                db.collection('pedidos').document(pedido_id).update({
                    'estado': estado,
                    'fechaActualizacion': firestore.SERVER_TIMESTAMP
                })
                self.send_json({'ok': True})
            else:
                self.send_json({'error': 'Faltan parametros'}, 400)
            return
        
        self.send_error(404)
    
    # === API DELETE ===
    def handle_api_delete(self, path):
        if not self.check_auth():
            self.send_json({'error': 'No autorizado'}, 401)
            return
        
        # Eliminar producto
        if path.startswith('/api/productos/'):
            prod_id = path.split('/api/productos/')[1]
            db.collection('productos').document(prod_id).delete()
            self.send_json({'ok': True})
            return
        
        # Eliminar categoria
        if path.startswith('/api/categorias/'):
            cat_id = path.split('/api/categorias/')[1]
            db.collection('categorias').document(cat_id).delete()
            self.send_json({'ok': True})
            return
        
        self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════╗
║   🎀 DETALLES ALEYDY - DASHBOARD   ║
╠══════════════════════════════════════╣
║  Servidor local en puerto """ + str(PORT) + """       ║
║  Abri: http://localhost:""" + str(PORT) + """        ║
║                                    ║
║  CTRL+C para detener               ║
╚══════════════════════════════════════╝
""")
    server = HTTPServer(('0.0.0.0', PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard detenido.")
        server.server_close()
