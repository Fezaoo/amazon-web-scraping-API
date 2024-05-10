from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})  # Habilita o CORS para todas as rotas locais

@app.route('/api/dados')
def dados():
    # Parâmetros
    query = request.args.get('query')
    query = query.replace(' ', '+')
    limit = int(request.args.get('limit', 4))
    try:
        # URLS e Headers utilizados
        base_url = 'https://www.amazon.com'
        url = f'{base_url}/s?k={query}'
        headers = ({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0", 'Accept-Language': 'en-US, en;q=0.5'})
        # Requisição à página da amazon com a query passada
        page = requests.get(url, headers=headers)

    except requests.exceptions.RequestException as e: # Tratamento de Erro
        print(f'Ocorreu um erro: {e}')
        return None
    else:
        # Obtem os conteúdos do site requisitado
        soup1 = BeautifulSoup(page.content, 'html.parser')
        soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')
        # Obtém as tags <a> (link) dos produtos
        links = soup2.find_all('a', attrs={'class':'a-link-normal s-no-outline'})
        link_list = list()
        c = 1
        # Obtem os links das tags recebidas e define um limite de produtos
        for link in links:
            link_list.append(link.get('href'))
            if c >= limit: break
            c+=1

        data_response = []
        # Obtem o conteúdo e informação de cada produto mostrado na página de pesquisa
        for link in link_list:
            new_page = requests.get(f'{base_url}{link}', headers=headers)
            soup1 = BeautifulSoup(new_page.content, 'html.parser')
            soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')
            title = soup2.find('span', attrs= {'id':"productTitle"}) # Obtém a tag do título do produto
            price = soup2.find('span', attrs={'class':"aok-offscreen"}) # Obtém a tag do preço do produto
            if not price: # Caso o preço do produto seja exibido em tabela
                price = soup2.find('span', {'class':"a-price"})
            rating = soup2.find(id="acrPopover") # Obtém a tag da avaliaçãos do produto
            image = soup2.find('div', attrs={'id':"imgTagWrapperId"}) # Obtém a tag da imagem do produto
            if not image:
                image = soup2.find('div', attrs={'class':"image-wrapper"}) # Caso a imagem seja de audiobook
            if title:
                title = title.get_text().strip() # Formata o título do produto
            if price:
                price = price.get_text().strip() # Formata o preço do produto
                price = price.split()[0]
            if rating:
                rating = rating.get_text().strip() # Formata a avaliação do produto
                rating = rating.split()[0]
            if image:
                image = image.find('img').get('src') # Recebe o link source da imagem do produto
            # Resposta da API
            data_response.append(            
                {'title': title,
                    'price': price,
                    'rating': rating,
                    'link': base_url + link,
                    'image':image
            })
        return jsonify(data_response)

if __name__ == '__main__':
    app.run(debug=True)
