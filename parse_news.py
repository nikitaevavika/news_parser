import requests
from bs4 import BeautifulSoup
import json

def parse_news():
    url = "https://web.archive.org/web/20230903112115/https://iz.ru/news"
    
    try:
        print("Загружаем страницу...")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_dict = {}
        
        news_blocks = soup.find_all('div', class_='news_block')
        
        if not news_blocks:
            news_blocks = soup.find_all('section', class_='news-section')
        if not news_blocks:
            news_blocks = soup.find_all('div', class_='news-item')
        
        print(f"Найдено новостных блоков: {len(news_blocks)}")
        
        for block in news_blocks:
            section_title = "Общие новости"
            
            section_elem = block.find(['h2', 'h3', 'div'], class_=True)
            if section_elem:
                section_title = section_elem.get_text(strip=True)
                section_title = section_title.replace('\n', ' ').replace('\t', ' ')
            
            news_list = []
            news_links = block.find_all('a', href=True)
            
            for link in news_links:
                title = link.get_text(strip=True)
                news_url = link['href']
                
                if title and len(title) > 10 and '/news/' in news_url:
                    if news_url.startswith('/'):
                        news_url = 'https://iz.ru' + news_url
                    
                    news_list.append({
                        'title': title,
                        'link': news_url
                    })
            
            if news_list:
                news_dict[section_title] = news_list
                print(f"Раздел '{section_title}': {len(news_list)} новостей")
        
        if not news_dict:
            print("Пробуем альтернативный метод поиска...")
            news_dict = alternative_parsing(soup)
        
        return news_dict
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}

def alternative_parsing(soup):
    news_dict = {}
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link['href']
        title = link.get_text(strip=True)
        
        if ('/news/' in href or '/article/' in href) and title and len(title) > 10:
            parent = link.find_parent(['div', 'section'])
            section_name = "Новости"
            
            if parent and parent.get('class'):
                class_name = ' '.join(parent.get('class'))
                if 'policy' in class_name.lower():
                    section_name = "Политика"
                elif 'sport' in class_name.lower():
                    section_name = "Спорт"
                elif 'society' in class_name.lower():
                    section_name = "Общество"
                elif 'health' in class_name.lower():
                    section_name = "Здоровье"
            
            if href.startswith('/'):
                href = 'https://iz.ru' + href
            
            if section_name not in news_dict:
                news_dict[section_name] = []
            
            news_dict[section_name].append({
                'title': title,
                'link': href
            })
    
    return news_dict

def save_results(news_data):
    if news_data:
        with open('news_results.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        print("Результаты сохранены в файл 'news_results.json'")
    else:
        print("Нет данных для сохранения")

def main():
    print("=== Парсер новостей с сайта Известия ===")
    print("Начинаем парсинг...")
    
    news_data = parse_news()
    
    if news_data:
        print("\n=== РЕЗУЛЬТАТЫ ПАРСИНГА ===")
        print(f"Найдено разделов: {len(news_data)}")
        
        for section, news in news_data.items():
            print(f"\n--- {section} ---")
            for item in news:
                print(f"  • {item['title']}")
                print(f"    Ссылка: {item['link']}")
        
        save_results(news_data)
        
        total_news = sum(len(news) for news in news_data.values())
        print(f"\n=== СТАТИСТИКА ===")
        print(f"Всего разделов: {len(news_data)}")
        print(f"Всего новостей: {total_news}")
        
    else:
        print("Не удалось получить новости. Проверьте подключение к интернету.")

if __name__ == "__main__":
    main()