import requests, json
from pymongo import MongoClient

client = MongoClient()
database = client['cf_project']
users = database['users']
userRepos = database['userRepos']

response = None
globalCounter = 0

for document in users.find():
	count = 0
	print(document['repos_url'])
	response = requests.get(document['repos_url'] + "?page=1&per_page=100&client_id=84690af0552c9ed4357b&client_secret=288d95782c060102e5f251cd880a386feef1d835")
	lastPage = 0
	if( globalCounter % 100 == 0 ):
		print("Ratelimit Left : {0}").format(response.headers.get("x-ratelimit-remaining", None))
	while(response.ok):
		link = response.headers.get('link', None)
		if( link is not None ):
			values = link.split(",")
			if( 'rel="last"' in values[1] ):
				lastPage = int(values[1].split("?")[1].split("&")[0][5:])
		item = json.loads(response.text or response.content)
		for repo in item:
			repo['user_id'] = document['id']
			userRepos.update(repo, repo, upsert = True)
		if( link is not None and count < lastPage ):
			count += 1
			link = link.split(">")[0][1:]
			linkVal = link.split("?")
			newLink = linkVal[0] + "?" + linkVal[1].split("&")[0][:5] + str(count) + "&" + linkVal[1].split("&")[1] + "&" + linkVal[1].split("&")[2] + "&" + linkVal[1].split("&")[3]
			response = requests.get(newLink)
		else:
			break
	print(globalCounter)
	globalCounter += 1