import urllib.parse
from bs4 import BeautifulSoup
import urllib
import csv
import sqlite3

def get_offer_pages():
  base_url = 'https://buchung.hsz.rwth-aachen.de/angebote/aktueller_zeitraum/'
  page = urllib.request.urlopen(urllib.parse.urljoin(base_url, 'index.html'))
  soup = BeautifulSoup(page)
  menu = soup.find('dl', { 'class': 'bs_menu'})
  exercise_types = menu.find_all('dd')
  types = []
  for exercise_type in exercise_types:
    url = urllib.parse.urljoin(base_url, exercise_type.a['href'])
    text = exercise_type.text
    types.append((text, url))
  
  csv.writer(open('exercise_types.csv', 'w')).writerows(types)

def get_offers():
  reader = csv.reader(open('exercise_types.csv'), delimiter=',')
  conn = sqlite3.connect('data.sqlite3')
  for row in reader:
    print(row)
    _, url = row
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page)
    tables = soup.find_all('table', { 'class': 'bs_kurse'})
    for table in tables:
      tbody = table.tbody
      trows = tbody.find_all('tr')
      for trow in trows:
        row = []
        tds = trow.find_all('td', class_=lambda x: x != 'bs_sbuch')
        for td in tds:
          row.append(td.text)
        conn.execute('''
          INSERT INTO exercise_types (kursnr, details, tag, zeit, ort, zeitraum, leitung, preis, url)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], url))
  conn.commit()
  conn.close()
      
def create_data_table():
  conn = sqlite3.connect('data.sqlite3')

  c = conn.cursor()
  c.execute('''
    CREATE TABLE IF NOT EXISTS exercise_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kursnr TEXT,
            details TEXT,
            tag TEXT,
            zeit TEXT,
            ort TEXT,
            zeitraum TEXT,
            leitung TEXT,
            preis TEXT,
            url TEXT
    );
  ''')
  conn.commit()
  conn.close()


def create_avail_table():
  conn = sqlite3.connect('data.sqlite3')
  c = conn.cursor()
  c.execute('''
    CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER,
            available BOOLEAN,
            timestamp TEXT
    );
  ''')
  conn.commit()
  conn.close()
    
    
  