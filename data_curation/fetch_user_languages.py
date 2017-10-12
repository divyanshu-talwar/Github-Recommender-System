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
	# if( count >= 247638 ):
	response = requests.get(document['languages_url'] + "?client_id=X&client_secret=X")
	# response can be empty which signifies that the repository may be forked and user has not contributed anything to the repositories
	if( response.ok ):
		item = json.loads(response.text or response.content)
		if( len(item) != 0 ):
			item['user_id'] = document['user_id']
			item['repo_id'] = document['id']
			userLangs.update(item, item, upsert = True)
	if( count % 100 == 0 ):
		print("Ratelimit Left : {0}").format(response.headers.get("x-ratelimit-remaining", None))
	print(count)
	count += 1

cursor.close()
