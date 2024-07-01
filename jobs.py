import datetime
from time import sleep
import sqlite3, urllib
from typing import Tuple

from bs4 import BeautifulSoup

def get_availability(offer_id):
  conn = sqlite3.connect('data.sqlite3')
  c = conn.cursor()
  c.execute('''
    SELECT kursnr, url
    FROM exercise_types
    WHERE id = ?
  ''', (offer_id,))
  object: Tuple[str] | None = c.fetchone()
  if object is None:
    return None
  kursnr = object[0]
  url = object[1]
  available = True
  attempts = 0
  while available and attempts < 60:
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    trows = soup.find_all('tr')
    for trow in trows:
      td_kursnr = trow.find('td', class_='bs_sknr')
      if td_kursnr is not None and td_kursnr.text == kursnr:
        attempts += 1
        input = trow.find('td', 'bs_sbuch').input
        if input is not None:
          c.execute('''
                    INSERT INTO availability (offer_id, available, timestamp)
                    VALUES (?, ?, ?)
          ''', (offer_id, input['value'] != 'Warteliste', datetime.datetime.now().isoformat()))
          conn.commit()
          available = input['value'] != 'Warteliste'
        break
    else:
      available = False
    sleep(58)
  conn.close()

  