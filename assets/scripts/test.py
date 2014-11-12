import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pprint import pprint


api_key = sys.argv[1]
file = sys.argv[2]
url = sys.argv[3]
limit = 0
batch_size = 1000
started = datetime.now()

try:
    limit = int(sys.argv[4])
except Exception:
    pass

classifications = []

with open(file, 'r') as obj:
    reader = csv.reader(obj)
    x = 0
    headers = None
    for row in reader:
        x += 1
        if x == 1:
            headers = [r for r in row]
            continue
        if limit > 0 and x > limit + 1:
            break
        obj = {}
        for y in range(len(headers)):
            obj[headers[y]] = row[y]
        classifications.append(obj)
        if len(classifications) == batch_size:
            post_data = urllib.parse.urlencode({'api_key': api_key, 'data': json.dumps(classifications)}).encode('utf8')
            request = urllib.request.Request(url, post_data)
            response = urllib.request.urlopen(request)
            print('%s processed:  %s: %s' % ((x - 1), datetime.now(), response.read()))
            classifications = []
td = datetime.now() - started
hours, remainder = divmod(td.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
print('finished in %s days, %s hours, %s minutes and %s seconds' % (td.days, hours, minutes, seconds))
