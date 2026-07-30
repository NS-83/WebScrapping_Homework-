from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
from fake_headers import Headers

# KEYWORDS = ['дизайн', 'фото', 'web', 'python']
KEYWORDS = ['вещей', 'читальный']
URL = 'https://habr.com/ru/articles/'


escaped_keywords = [re.escape(kw) for kw in KEYWORDS]
pattern_str = '|'.join(escaped_keywords)
keyword_pattern = re.compile(
    r'\b(' + pattern_str + r')\b',
    re.IGNORECASE
)

headers = Headers(browser='chrome', os='linux').generate()
html_doc = requests.get(URL, headers=headers).text
soup = BeautifulSoup(html_doc, 'lxml')
articles_list = soup.select('div.article-snippet')

for article in articles_list:
    texts_list = []
    time_tag = article.select_one('time')
    if time_tag:
        datetime_string = time_tag.get('datetime')
        if datetime_string:
            datetime_string = datetime_string.split('.')[0]
            dt_utc = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
            dt_msk = dt_utc + timedelta(hours=3)
            article_time = dt_msk.strftime('%d.%m.%Y %H:%M')
        else:
            article_time = 'Время не указано'
    else:
        article_time = 'Время не указано'
    article_header_tag = article.select_one('h2.tm-title.tm-title_h2')
    if article_header_tag:
        article_header_content = article_header_tag.select_one('a.tm-title__link')
        if article_header_content:
            article_link = article_header_content.get('href')
            article_link = f'https://habr.com{article_link}'
            article_header_tag = article_header_content.select_one('span')
            if article_header_tag:
                article_header = article_header_tag.text
            else:
                article_header = ''
        else:
            article_header = ''
            article_link = ''
    else:
        article_header = ''
        article_link = ''
    if article_header:
        texts_list.append(article_header)

    article_keywords_tags_container = article.select_one('div.tm-publication-hubs__container')
    if article_keywords_tags_container:
        article_keywords_tags = article_keywords_tags_container.select('span.tm-publication-hub__link-container')
        if article_keywords_tags:
            keywords_list = [keywords_tag.select_one('span').text.strip() for keywords_tag in article_keywords_tags]
            texts_list.extend(keywords_list)

    lead_tag = article.select_one('div.lead')
    if lead_tag:
        preview_tags = lead_tag.select('p')
        if preview_tags:
            preview_texts = [preview_tag.text.strip() for preview_tag in preview_tags]
            texts_list.extend(preview_texts)

    article_preview_text = ' '.join(texts_list)
    if keyword_pattern.search(article_preview_text):
         found_article_string = f'{article_time} - {article_header} - {article_link}'
         print(found_article_string)



