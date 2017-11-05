import requests, json
from pymongo import MongoClient

client = MongoClient()
database = client['cf_project']
userRepos = database['userRepos']
userLangs = database['userLangs']

response = None
count = 0
cursor = userRepos.find(timeout = False)

for document in cursor:
	response = requests.get(document['languages_url'] + "?client_id=84690af0552c9ed4357b&client_secret=288d95782c060102e5f251cd880a386feef1d835")
	# response can be empty which signifies that the repository may be forked and user has not contributed anything to the repositories
	if( response.ok ):
		item = json.loads(response.text or response.content)
		if( len(item) != 0 ):
			item['user_id'] = document['user_id']
			item['repo_id'] = document['id']
			userLangs.update(item, item, upsert = True)
	if( count % 100 == 0 ):
		print("Ratelimit Left : {0}").format(response.headers.get("x-ratelimit-remaining", None))
		if( response.headers.get("x-ratelimit-remaining", None) == '0' ):
			print("Ratelimit reached!!!!")
			break
	print(count)
	count += 1

cursor.close()
