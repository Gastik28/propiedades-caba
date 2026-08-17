# 🏠 Propiedades CABA — App local

Dashboard para visualizar y filtrar propiedades inmobiliarias con fotos en tiempo real.

## Instalación (una sola vez)

```bash
pip install flask flask-cors requests beautifulsoup4
```

## Correr la app

```bash
cd propiedades-app
python app.py
```

Luego abrí el browser en: **http://localhost:5050**

## Uso

1. **Cargá los CSVs** usando los botones del panel izquierdo (ML, Argenprop, Zonaprop)
2. **Las fotos** se cargan automáticamente desde los portales — necesitás internet
3. **Filtrá** por zona, precio, m², palabras clave
4. **Marcá** propiedades como ⭐ Favorito / 👁 Visitada / ✗ Descartada
5. **Exportá favoritos** con el botón arriba a la derecha
6. **Click en una card** abre la publicación original en el portal

## Notas

- Los estados (favoritos, visitadas, descartadas) se guardan en el browser automáticamente
- Las fotos se cachean en memoria — si cerrás y reabrís la app, se vuelven a cargar
- Funciona con cualquier CSV que tenga las columnas: zona, titulo, precio_usd, direccion, atributos, link
- No requiere conexión para los filtros y estados, solo para cargar las fotos
