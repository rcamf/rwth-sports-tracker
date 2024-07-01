import sqlite3
import apscheduler.schedulers.blocking
from jobs import get_availability

# Booking starts a day earlier
tag_to_int = {
  'Mo': 6,
  'Di': 0,
  'Mi': 1,
  'Do': 2,
  'Fr': 3,
  'Sa': 4,
  'So': 5
}

def main():
  conn = sqlite3.connect('data.sqlite3')
  c = conn.cursor()
  
  scheduler = apscheduler.schedulers.blocking.BlockingScheduler()

  c.execute('''
    SELECT id, tag, zeit
    FROM exercise_types
  ''')

  for row in c.fetchall():
    offer_id, tag, zeit = row
    print(tag, zeit)
    scheduler.add_job(get_availability, trigger='cron', args=[offer_id], day_of_week=tag_to_int[tag[0:2]], hour=zeit.split(':')[0], minute=zeit.split(':')[1].split('-')[0])
  
  try:
    scheduler.start()
  except (KeyboardInterrupt, SystemExit):
    pass

if __name__ == '__main__':
  main()