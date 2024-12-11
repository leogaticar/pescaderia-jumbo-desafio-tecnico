from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import logging
import os

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_products():
    url = "https://www.jumbo.cl/pescaderia"
    
    try:
        # Configurar headers para simular un navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info("Realizando solicitud a %s", url)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        logger.info("Solicitud exitosa. Código de estado: %d", response.status_code)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar todos los productos usando el nuevo selector
        product_cards = soup.find_all('div', class_='product-card')
        
        logger.info("Encontrados %d productos", len(product_cards))
        
        products = []
        for card in product_cards:
            try:
                # Extraer información usando los nuevos selectores
                name = card.find('a', class_='product-card-name').text.strip()
                price = card.find('span', class_='prices-main-price').text.strip()
                brand = card.find('a', class_='product-card-brand').text.strip()
                
                # Buscar la imagen
                img_tag = card.find('img', class_='lazy-image')
                image_url = img_tag['src'] if img_tag else ''
                
                products.append({
                    'name': name,
                    'price': price,
                    'brand': brand,
                    'image_url': image_url
                })
                
                logger.info("Producto extraído: %s", name)
                
            except Exception as e:
                logger.error("Error al extraer información del producto: %s", str(e))
                continue
        
        return products
        
    except requests.RequestException as e:
        logger.error("Error al realizar la solicitud: %s", str(e))
        return []

@app.route('/')
def index():
    products = get_products()
    return render_template('index.html', products=products)

@app.route('/api/products')
def api_products():
    products = get_products()
    # Solo devolver nombre, marca y precio
    simplified_products = [{
        'name': product['name'],
        'brand': product['brand'],
        'price': product['price']
    } for product in products]
    return jsonify(simplified_products)

if __name__ == '__main__':
    # Usar puerto 5002 por defecto
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True) 