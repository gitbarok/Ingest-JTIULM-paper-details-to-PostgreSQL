import pandas as pd
import psycopg2
import requests

from bs4 import BeautifulSoup

def create_db():
    con = psycopg2.connect(
        database="jtiulm",
        user="user",
        password="root",
        host="0.0.0.0")
    
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS paper_details")
    cur.execute("""CREATE TABLE IF NOT EXISTS paper_details(
    title VARCHAR,
    author VARCHAR,
    link VARCHAR
    )""")
    con.commit()

    return con, cur

def scrape_jtiulm():
    # declare url target
    url = 'https://jtiulm.ti.ft.ulm.ac.id/index.php/jtiulm/issue/archive'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # get all link from the archive and stored in links as a list
    links = []
    for link in soup.find_all('a', class_='cover'):
        links.append(link.get('href'))

    paper = {
        'title': [],
        'author': [],
        'link': [],
    }

    for link in links:
        page_a = requests.get(link)
        results_a = BeautifulSoup(page_a.content, 'html.parser')
        for content in results_a.find_all('div', class_='obj_article_summary'):
            paper_title = content.find('div', class_='title').text.strip()
            paper_author = content.find('div', class_='authors').text
            paper_link = content.find('a').get('href')
            paper['title'].append(paper_title)
            paper['author'].append(paper_author.replace('\t', '').replace('\n', ''))
            paper['link'].append(paper_link)


    df = pd.DataFrame.from_dict(paper)
    return df


def main():
    conn, cur = create_db()
    print("SCRAPING STARTED")
    df = scrape_jtiulm()
    print("SCRAPING FINISHED")
    sql_script = ("""INSERT INTO paper_details(
    title,
    author,
    link)
    VALUES (%s, %s, %s)
    """)
    for i, data in df.iterrows():
        print(f'insert {i+1} row from {df.shape[0]} total row')
        cur.execute(sql_script, list(data))
    conn.commit()


if __name__ == '__main__':
    main()