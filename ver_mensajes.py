"""Ver mensajes recibidos. Ejecutar en la terminal: python3 ver_mensajes.py"""
from pathlib import Path
import sqlite3
path=Path(__file__).resolve().parent/'private'/'mensajes.db'
if not path.exists():
    print('Todavía no hay mensajes guardados.')
else:
    with sqlite3.connect(path) as c:
        rows=c.execute('SELECT id,fecha,nombre,correo,telefono,tema,mensaje FROM mensajes ORDER BY id DESC').fetchall()
    print(f'\nMensajes recibidos: {len(rows)}')
    for r in rows:
        print('\n'+'='*56)
        for k,v in zip(['ID','Fecha','Nombre','Correo','Teléfono','Tema','Mensaje'],r):
            print(f'{k}: {v}')
