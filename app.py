import os
"""
Propiedades CABA — App local v2
Correr con: python app.py
Abrir en browser: http://localhost:5050
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re, csv, io, os, json

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-AR,es;q=0.9",
}

_foto_cache = {}

def extraer_foto_principal(url):
    """Extrae UNA sola foto principal (rápido)."""
    url_clean = url.split('#')[0].split('?')[0]
    if url_clean in _foto_cache:
        return _foto_cache[url_clean]

    foto = ''
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Intentar og:image primero (más rápido, funciona en todos los portales)
        og = soup.find('meta', property='og:image')
        if og and og.get('content','').startswith('http'):
            foto = og['content']
        
        # MercadoLibre fallback
        if not foto and 'mercadolibre' in url:
            img = soup.select_one('img.ui-pdp-image, figure img')
            if img:
                foto = img.get('data-zoom') or img.get('src','')

        # Zonaprop fallback
        if not foto and 'zonaprop' in url:
            for script in soup.find_all('script'):
                m = re.search(r'"image"\s*:\s*\["?(https://[^"\]]+)', script.string or '')
                if m:
                    foto = m.group(1)
                    break

    except Exception as e:
        pass

    if not foto or not foto.startswith('http'):
        foto = ''
    _foto_cache[url_clean] = foto
    return foto


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/foto')
def api_foto():
    """Devuelve UNA sola foto para una URL."""
    url = request.args.get('url', '')
    if not url:
        return jsonify({'foto': ''})
    foto = extraer_foto_principal(url)
    return jsonify({'foto': foto})


@app.route('/api/parse-csv', methods=['POST'])
def api_parse_csv():
    data = request.json
    texto = data.get('csv', '')
    portal = data.get('portal', 'desconocido')

    reader = csv.DictReader(io.StringIO(texto))
    propiedades = []
    for i, row in enumerate(reader):
        link = (row.get('link') or '').split('#')[0].strip()
        if not link or link == 'Sin link':
            continue

        # Detectar portal desde link o columna
        if portal == 'candidatos':
            p = row.get('portal', '')
            if not p:
                p = 'ml' if 'mercadolibre' in link else ('argenprop' if 'argenprop' in link else 'zonaprop')
        else:
            p = portal

        titulo = row.get('titulo_word') or row.get('titulo', '')
        direccion = row.get('direccion') or row.get('titulo_word', '')

        prop = {
            'id': f"{p}_{i}",
            'portal': p,
            'zona': row.get('zona', ''),
            'titulo': titulo[:120],
            'precio_usd': row.get('precio_usd', ''),
            'direccion': direccion,
            'atributos': row.get('atributos', ''),
            'link': link,
            'orden': int(row.get('orden', i)),
        }
        m = re.search(r'[\d\.]+', prop['precio_usd'].replace(',','.'))
        prop['precio_num'] = int(m.group().replace('.','')) if m else 0
        m2 = re.search(r'(\d{2,4})\s*m[²2]', prop['atributos'])
        prop['m2'] = int(m2.group(1)) if m2 else 0

        propiedades.append(prop)

    # Ordenar por campo orden si viene del Word
    propiedades.sort(key=lambda x: x.get('orden', 9999))

    return jsonify({'propiedades': propiedades, 'total': len(propiedades)})


if __name__ == '__main__':
    print("\n🏠 Propiedades CABA — App local v2")
    print("   Abrí tu browser en: http://localhost:5050\n")
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=False, host="0.0.0.0", port=port, threaded=True)
