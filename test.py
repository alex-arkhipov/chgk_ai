import requests
from bs4 import BeautifulSoup
import json


url = 'https://gotquestions.online/pack/10000'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

with open('gotquestions/1/1.html', 'r') as f:
    text = f.read()

#Скачиваем HTML страницы при помощи requests
#response = requests.get(url, headers=headers)
#print(response.status_code)
# Проверяем валидность полученного ответа
#if response.status_code == 200:

# Парсим HTML при помощи Beautiful Soup
soup = BeautifulSoup(markup=text, features='html.parser')

# CSS-селектор для основных таблиц
script = soup.find(name='script', attrs={'id': '__NEXT_DATA__'})
#print (script.text)
data = json.loads(script.text)
data2 = data['props']['pageProps']['pack']['tours']
for tour in data2:
    print(f'Tour: {tour["id"]}')
    for question in tour['questions']:
        raz = ''
        if question.get('razdatkaPic'):
            raz = ' with razdatka'
        print(f'Question: {question["id"]}{raz}')
#print(data2)