"""
Proxy API para el Dashboard de Detalles Aleydy.
Serverless function para Vercel. Usa el service account de Firebase.
"""

import json
import os
import base64
from http.server import BaseHTTPRequestHandler
import firebase_admin
from firebase_admin import credentials, firestore

# ═══ INICIALIZACION (cacheada entre invocaciones) ═══
if not firebase_admin._apps:
    # La service account viene como variable de entorno en base64
    sa_b64 = os.environ.get('FIREBASE_SA_B64', '')
    if sa_b64:
        sa_json = json.loads(base64.b64decode(sa_b64))
        cred = credentials.Certificate(sa_json)
    else:
        # Fallback para desarrollo local
        cred = credentials.Certificate('keys/detalles-aleydy-firebase-sa.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()
AUTH_TOKEN = os.environ.get('DASHBOARD_TOKEN', 'aleydy2024')


class handler(BaseHTTPRequestHandler):
    """Manejador HTTP para Vercel serverless."""

    @property
    def _actual_path(self):
        """Extraer el path sin query string."""
        from urllib.parse import urlparse
        return urlparse(self.path).path

    def do_GET(self):
        path = self._actual_path
        
        # Debug: mostrar headers en produccion
        if path == '/api/debug' or 'debug' in path:
            return self._json({
                'path': self.path,
                'actual_path': path,
                'headers': dict(self.headers)
            })

        # Auth
        if path == '/api/auth/check':
            return self._json({'ok': self._check_auth()})

        if path == '/api/auth/login':
            qs = self._parse_qs()
            token = qs.get('token', [''])[0]
            if token == AUTH_TOKEN:
                return self._json({'ok': True, 'token': token})
            return self._json({'ok': False, 'error': 'Token invalido'}, 401)

        # Productos
        if path == '/api/productos':
            if not self._check_auth():
                return self._json({'error': 'No autorizado'}, 401)
            prods = [{'id': d.id, **d.to_dict()} for d in db.collection('productos').order_by('categoria').get()]
            return self._json(prods)

        # Categorias
        if path == '/api/categorias':
            if not self._check_auth():
                return self._json({'error': 'No autorizado'}, 401)
            cats = [{'id': d.id, **d.to_dict()} for d in db.collection('categorias').order_by('orden').get()]
            return self._json(cats)

        # Pedidos
        if path == '/api/pedidos':
            if not self._check_auth():
                return self._json({'error': 'No autorizado'}, 401)
            peds = [{'id': d.id, **d.to_dict()} for d in db.collection('pedidos').order_by('fecha', direction=firestore.Query.DESCENDING).limit(50).get()]
            return self._json(peds)

        # Endpoints PUBLICOS (sin auth, para la landing page)
        if path == '/api/productos-public':
            prods = [{'id': d.id, **d.to_dict()} for d in db.collection('productos').get() if d.to_dict().get('activo', True)]
            return self._json(prods)

        if path == '/api/categorias-public':
            cats = [{'id': d.id, **d.to_dict()} for d in db.collection('categorias').get()]
            return self._json(cats)

        # Tracking de visitas (público)
        if path == '/api/visitas':
            # Últimos 14 días
            from datetime import datetime, timedelta
            visits = []
            for i in range(14):
                day = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                doc = db.collection('visitas').document(day).get()
                visits.append({
                    'fecha': day,
                    'total': doc.to_dict().get('total', 0) if doc.exists else 0
                })
            visits.reverse()
            total_all = sum(v['total'] for v in visits)
            return self._json({'dias': visits, 'total': total_all})

        self._json({'error': 'Not found'}, 404)

    def do_POST(self):
        path = self._actual_path
        body = self._read_body()

        # Tracking de visita (público, sin auth)
        if path == '/api/track-visit':
            from datetime import datetime
            today = datetime.utcnow().strftime('%Y-%m-%d')
            ref = db.collection('visitas').document(today)
            doc = ref.get()
            current = doc.to_dict().get('total', 0) if doc.exists else 0
            ref.set({
                'total': current + 1,
                'ultimaVisita': firestore.SERVER_TIMESTAMP
            }, merge=True)
            return self._json({'ok': True, 'totalHoy': current + 1})

        # Login
        if path == '/api/auth/login':
            token = body.get('token', '')
            if token == AUTH_TOKEN:
                return self._json({'ok': True, 'token': token})
            return self._json({'ok': False, 'error': 'Token invalido'}, 401)

        if not self._check_auth():
            return self._json({'error': 'No autorizado'}, 401)

        # Guardar producto
        if path == '/api/productos':
            pid = body.get('id') or body.get('nombre', '').lower().replace(' ', '-').replace('/', '-')
            data = {
                'nombre': body.get('nombre', ''),
                'categoria': body.get('categoria', ''),
                'descripcion': body.get('descripcion', ''),
                'precio': float(body.get('precio', 0)),
                'foto': body.get('foto', ''),
                'badge': body.get('badge', ''),
                'destacado': body.get('destacado', False),
                'activo': body.get('activo', True),
                'fechaActualizacion': firestore.SERVER_TIMESTAMP,
            }
            db.collection('productos').document(pid).set(data, merge=True)
            return self._json({'ok': True, 'id': pid})

        # Guardar categoria
        if path == '/api/categorias':
            cid = body.get('id') or body.get('nombre', '').lower().replace(' ', '-')
            data = {
                'nombre': body.get('nombre', ''),
                'orden': int(body.get('orden', 0)),
            }
            db.collection('categorias').document(cid).set(data, merge=True)
            return self._json({'ok': True, 'id': cid})

        # Estado de pedido
        if path == '/api/pedidos/estado':
            pid = body.get('id')
            estado = body.get('estado')
            if pid and estado:
                db.collection('pedidos').document(pid).update({
                    'estado': estado,
                    'fechaActualizacion': firestore.SERVER_TIMESTAMP,
                })
                return self._json({'ok': True})
            return self._json({'error': 'Faltan parametros'}, 400)

        self._json({'error': 'Not found'}, 404)

    def do_DELETE(self):
        path = self._actual_path

        if not self._check_auth():
            return self._json({'error': 'No autorizado'}, 401)

        if path.startswith('/api/productos/'):
            pid = path.split('/api/productos/')[1]
            db.collection('productos').document(pid).delete()
            return self._json({'ok': True})

        if path.startswith('/api/categorias/'):
            cid = path.split('/api/categorias/')[1]
            db.collection('categorias').document(cid).delete()
            return self._json({'ok': True})

        self._json({'error': 'Not found'}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()

    # ═══ HELPERS ═══
    def _check_auth(self):
        auth = self.headers.get('Authorization', '')
        return auth == 'Bearer ' + AUTH_TOKEN

    def _read_body(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length > 0:
                return json.loads(self.rfile.read(length))
        except Exception:
            pass
        return {}

    def _parse_qs(self):
        from urllib.parse import urlparse, parse_qs
        return parse_qs(urlparse(self.path).query)

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
