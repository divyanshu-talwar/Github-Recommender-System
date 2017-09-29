import requests, json
from pymongo import MongoClient

client = MongoClient()
database = client['cf_project']
users = database['users']

response = requests.get('https://api.github.com/users?since=0&page=1&per_page=100&client_id=84690af0552c9ed4357b&client_secret=288d95782c060102e5f251cd880a386feef1d835')
count = 0

while(response.ok):
	link = response.headers.get('link',None)
	item = json.loads(response.text or response.content)
	for user in item:
		users.update(user, user, upsert = True)
	print(count)
	if(count % 100 == 0): 
		print("Ratelimit Left : {0}").format(response.headers.get("x-ratelimit-remaining", None))
		break
	if(link is not None):
		count += 1
		link = link.split(">")[0][1:]
		response = requests.get(link)