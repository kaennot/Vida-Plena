"""Vida Plena: servidor local con formulario real y almacenamiento SQLite.

Ejecutar: python3 servidor.py
Abrir: http://127.0.0.1:8000

Este servidor es para un prototipo local. Para publicarlo, usar HTTPS,
protección contra spam y alojamiento seguro con políticas de privacidad.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from email.utils import parseaddr
from datetime import datetime, timezone
import sqlite3
import re
import os

HERE = Path(__file__).resolve().parent
DB = HERE / 'private' / 'mensajes.db'
DB.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(DB) as con:
    con.execute('''CREATE TABLE IF NOT EXISTS mensajes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fecha TEXT NOT NULL,
      nombre TEXT NOT NULL,
      correo TEXT NOT NULL,
      telefono TEXT,
      tema TEXT NOT NULL,
      mensaje TEXT NOT NULL
    )''')

ALLOWED_PAGES = {p.name for p in HERE.glob('*.html')}
ALLOWED_ASSETS = {p.name for p in (HERE / 'assets').glob('*.svg')}
ALLOWED_PUBLIC_FILES = {'styles.css','app.js'}
TEMAS={'Salud','Alimentación','Movimiento','Bienestar emocional','Acompañamiento','Sugerencia','Otro'}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(HERE),**kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/': self.path = '/index.html'
        elif path.startswith('/assets/') and path.removeprefix('/assets/') in ALLOWED_ASSETS: pass
        elif path.startswith('/') and path[1:] in ALLOWED_PAGES | ALLOWED_PUBLIC_FILES: pass
        else:
            self.send_error(404,'Página no encontrada')
            return
        return super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != '/enviar':
            self.send_error(404,'Ruta no encontrada'); return
        try:
            size=int(self.headers.get('Content-Length','0'))
        except ValueError:
            self.send_error(400,'Solicitud inválida'); return
        if size < 1 or size > 16_000:
            self.send_error(413,'Mensaje demasiado largo'); return
        if self.headers.get('Content-Type','').split(';')[0].strip().lower() != 'application/x-www-form-urlencoded':
            self.send_error(415,'Formato no permitido'); return
        # Control básico contra envíos realizados desde otros dominios.
        origin=self.headers.get('Origin','')
        port=self.server.server_address[1]
        if origin and origin not in {f'http://127.0.0.1:{port}',f'http://localhost:{port}'}:
            self.send_error(403,'Origen no permitido'); return
        try:
            fields = parse_qs(self.rfile.read(size).decode('utf-8'),keep_blank_values=True,max_num_fields=12)
            val=lambda key: fields.get(key,[''])[0].strip()
            nombre,correo,telefono,tema,mensaje = [val(k) for k in ('nombre','correo','telefono','tema','mensaje')]
            valid=(2<=len(nombre)<=100 and 5<=len(correo)<=160 and
                 re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',correo) and
                 len(telefono)<=30 and tema in TEMAS and
                 10<=len(mensaje)<=2500 and val('consentimiento')=='si')
            if val('sitio'): # Campo-trampa para bots.
                self.send_response(303);self.send_header('Location','/gracias.html');self.end_headers();return
            if not valid:
                self.send_error(400,'Revisa los campos del formulario e inténtalo de nuevo');return
            with sqlite3.connect(DB) as con:
                con.execute('INSERT INTO mensajes(fecha,nombre,correo,telefono,tema,mensaje) VALUES(?,?,?,?,?,?)',
                    (datetime.now(timezone.utc).isoformat(),nombre,correo,telefono,tema,mensaje))
        except (UnicodeDecodeError, ValueError, sqlite3.DatabaseError):
            self.send_error(400,'No se pudo procesar el mensaje');return
        self.send_response(303)
        self.send_header('Location','/gracias.html')
        self.send_header('Cache-Control','no-store')
        self.end_headers()

    def list_directory(self,path):
        self.send_error(403,'No permitido')
        return None

if __name__ == '__main__':
    port=int(os.environ.get('PORT',8000))
    print(f'Vida Plena en http://127.0.0.1:{port}')
    print(f'Los mensajes quedarán guardados en {DB} (no se envían por email).')
    try: ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
    except KeyboardInterrupt: print('\nServidor detenido.')
