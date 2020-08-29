import h5py
import pickle
import numpy as np
from pymongo import MongoClient

MAX_USERS = 1000
MAX_REPOS = 1000

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
repo_cursor = repos.find(timeout = False)

user_id_mapping = dict()
repo_id_mapping = dict()

with open("user_mappings.pkl", "r") as handle:
	user_id_mapping = pickle.load(handle)

with open("repo_mappings.pkl", "r") as handle:
	repo_id_mapping = pickle.load(handle)

MAX_USERS = max(user_id_mapping.values())
MAX_REPOS = max(repo_id_mapping.values())

print(MAX_USERS)
print(MAX_REPOS)

rating_matrix = np.zeros((MAX_USERS+1, MAX_REPOS+1))

print("Done mapping!!")

user_cursor.rewind()
repo_cursor.rewind()

# stars contribution
for user_doc in user_cursor:
	user_repo = stars.find({'user_id' : user_doc['id']}).limit(1)
	if( user_repo.count() == 0 ):
		continue
	if( user_repo[0]['repo_id'] in repo_id_mapping.keys() ):
		user_repo = user_repo[0]
		for user in user_repo['user_id']:
			if( user in user_id_mapping.keys() ):
				rating_matrix[user_id_mapping[user]][repo_id_mapping[user_repo['repo_id']]] += 1

print("Stars contribution done!!")

user_cursor.rewind()

# watchers contribution
for user_doc in user_cursor:
	user_repo = watchers.find({'user_id' : user_doc['id']}).limit(1)
	if( user_repo.count() == 0 ):
		continue
	if( user_repo[0]['repo_id'] in repo_id_mapping.keys() ):
		user_repo = user_repo[0]
		for user in user_repo['user_id']:
			if( user in user_id_mapping.keys() ):
				rating_matrix[user_id_mapping[user]][repo_id_mapping[user_repo['repo_id']]] += 1				

print("Watchers contribution done!!")

user_cursor.rewind()

# forks contribution
for user_doc in user_cursor:
	user_repo = forks.find({'user_id' : user_doc['id']}).limit(1)
	if( user_repo.count() == 0 ):
		continue
	if( user_repo[0]['repo_id'] in repo_id_mapping.keys() ):
		user_repo = user_repo[0]
		for user in user_repo['user_id']:
			if( user in user_id_mapping.keys() ):
				rating_matrix[user_id_mapping[user]][repo_id_mapping[user_repo['repo_id']]] += 1				

print("Forks contribution done!!")

user_cursor.rewind()

# followings contribution
for user_doc in user_cursor:
	user_following = followings.find({'id' : user_doc['id']}).limit(1)
	if( user_following.count() == 0 ):
		continue
	user_following = user_following[0]
	for user in user_following:
		if( user in user_id_mapping.keys() ):
			user_repo = repos.find({'user_id' : user}).limit(1)
			if( user_repo.count() == 0 ):
				continue
			user_repo = user_repo[0]
			if( user_repo['id'] in repo_id_mapping.keys() ):
				rating_matrix[user_id_mapping[user_doc['id']]][repo_id_mapping[user_repo['id']]] += 1

print("Followings contribution done!!")

user_cursor.rewind()
repo_cursor.rewind()

# languages contribution
for user_doc in user_cursor:
	if( user_doc['id'] in user_id_mapping.keys() ):
		user_lang = langs.find({'user_id' : user_doc['id']}).limit(1)
		if( user_lang.count() == 0 ):
			continue
		user_lang = user_lang[0]
		for repo_doc in repo_cursor:
			repo_lang = langs.find({'repo_id' : repo_doc['id']}).limit(1)
			if( repo_lang.count() == 0 ):
				continue
			repo_lang = repo_lang[0]
			score = 0.0
			for lang in user_lang:
				if( lang in repo_lang and lang not in ['_id' ,'user_id', 'repo_id'] ):
					score += user_lang[lang]*1.0/repo_lang[lang]
			rating_matrix[user_id_mapping[user_doc['id']]][repo_id_mapping[repo_doc['id']]] += score

print("Languages contribution done!!")


user_cursor.rewind()

# followers contribution
for idx, user_doc in enumerate(user_cursor):
	print(idx)
	user_follower = followers.find({'id' : user_doc['id']}).limit(1)
	user_repo = repos.find({'user_id' : user_doc['id']}).limit(1)
	if( user_follower.count() == 0 or user_repo.count() == 0 ):
		continue
	user_follower = user_follower[0]
	user_repo = user_repo[0]
	for user in user_follower:
		if( user in user_id_mapping.keys() ):
			rating_matrix[user_id_mapping[user]][repo_id_mapping[user_repo['id']]] += 1

print("Followers contribution done!!")


print(rating_matrix)

user_cursor.close()
repo_cursor.close()

rating_matrix_save = h5py.File("rating_matrix", 'w')
rating_matrix_save.create_dataset('rating_matrix', data = rating_matrix)
rating_matrix_save.close()

print("Done!!")