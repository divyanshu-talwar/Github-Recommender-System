import pickle
import numpy as np
from pymongo import MongoClient

client = MongoClient()
database = client['cf_project']
users = database['users']
repos = database['userRepos']
langs = database['userLangsSmall']
forks = database['repoForksSmall']
stars = database['repoStarsSmall']
watchers = database['repoWatchersSmall']
followers = database['userFollowerSmall']
followings = database['userFollowingSmall']

user_cursor = users.find(timeout = False).limit(1000)

user_id_mapping = dict()
repo_id_mapping = dict()

for  idx, user_doc in enumerate(user_cursor):
	print(idx)
	user_id_mapping[user_doc['id']] = idx
	repo = repos.find({'user_id' : user_doc['id']}).limit(1)
	if( repo.count() == 0 ):
		continue
	repo = repo[0]
	repo_id_mapping[repo['id']] = idx

print(max(user_id_mapping.values()))
print(max(repo_id_mapping.values()))

with open("user_mappings.pkl", "wb") as handle:
	pickle.dump(user_id_mapping, handle, protocol = pickle.HIGHEST_PROTOCOL)

with open("repo_mappings.pkl", "wb") as handle:
	pickle.dump(repo_id_mapping, handle, protocol = pickle.HIGHEST_PROTOCOL)