from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_products():
    url = "https://www.jumbo.cl/pescaderia"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        product_cards = soup.find_all('div', class_='product-card')
        products = []

        for card in product_cards:
            try:
                name = card.find('a', class_='product-card-name').text.strip()
                price = card.find('span', class_='prices-main-price').text.strip()
                brand = card.find('a', class_='product-card-brand').text.strip()
                img_tag = card.find('img', class_='lazy-image')
                image_url = img_tag['src'] if img_tag else ''
                
                products.append({
                    'name': name,
                    'price': price,
                    'brand': brand,
                    'image_url': image_url
                })
            except Exception as e:
                logger.error(f"Error al extraer información del producto: {str(e)}")
                continue
        
        return products
        
    except requests.RequestException as e:
        logger.error(f"Error al realizar la solicitud: {str(e)}")
        return []

@app.route('/')
def index():
    products = get_products()
    return render_template('index.html', products=products)

@app.route('/api/products')
def api_products():
    products = get_products()
    simplified_products = [{
        'name': product['name'],
        'brand': product['brand'],
        'price': product['price']
    } for product in products]
    return jsonify(simplified_products)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True) 