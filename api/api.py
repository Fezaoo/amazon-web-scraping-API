# serverless_function.py

from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/dados', methods=['GET'])
def dados():
    query = request.args.get('query')
    query = query.replace(' ', '+')
    limit = int(request.args.get('limit', 4))
    
    try:
        base_url = 'https://www.amazon.com'
        url = f'{base_url}/s?k={query}'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0", 'Accept-Language': 'en-US, en;q=0.5'}
        
        page = requests.get(url, headers=headers)

    except requests.exceptions.RequestException as e:
        print(f'Ocorreu um erro: {e}')
        return jsonify({'error': 'Erro ao fazer a requisição'}), 500
    
    else:
        soup1 = BeautifulSoup(page.content, 'html.parser')
        soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')
        links = soup2.find_all('a', attrs={'class':'a-link-normal s-no-outline'})
        link_list = list()
        c = 1
        
        for link in links:
            link_list.append(link.get('href'))
            if c >= limit: break
            c += 1

        data_response = []

        for link in link_list:
            new_page = requests.get(f'{base_url}{link}', headers=headers)
            soup1 = BeautifulSoup(new_page.content, 'html.parser')
            soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')
            title = soup2.find('span', attrs= {'id':"productTitle"})
            price = soup2.find('span', attrs={'class':"aok-offscreen"})
            if not price:
                price = soup2.find('span', {'class':"a-price"})
            rating = soup2.find(id="acrPopover")
            image = soup2.find('div', attrs={'id':"imgTagWrapperId"})
            if not image:
                image = soup2.find('div', attrs={'class':"image-wrapper"})
            if title:
                title = title.get_text().strip()
            if price:
                price = price.get_text().strip()
                price = price.split()[0]
            if rating:
                rating = rating.get_text().strip()
                rating = rating.split()[0]
            if image:
                image = image.find('img').get('src')
            
            data_response.append({            
                'title': title,
                'price': price,
                'rating': rating,
                'link': base_url + link,
                'image':image
            })
        
        return jsonify(data_response)

if __name__ == '__main__':
    app.run(debug=True)
