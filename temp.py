import h5py
import numpy as np

rating_matrix_save = h5py.File("rating_matrix", 'r')
rating_matrix = rating_matrix_save['rating_matrix'][:]
rating_matrix_save.close()


counter = 0
for user in range(1000):
	for item in range(1000):
		if( rating_matrix[user][item] != 0 ):
			print("-----------")
			print(rating_matrix[user][item])
			print("User" + str(user), "Repo" + str(item))
			counter += 1

print(counter)