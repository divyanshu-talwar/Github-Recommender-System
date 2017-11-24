from __future__ import division, print_function, absolute_import
import os
import h5py
import argparse
import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

parser = argparse.ArgumentParser(description = 'Collborative Filtering Assignment 2.')
parser.add_argument('--debug', type = str, nargs = '+', help = "Want debug statements.", choices = ['yes', 'no'])

args = parser.parse_args()

initTime1 = datetime.datetime.now()

rating_matrix_save = h5py.File("rating_matrix", 'r')
rating_matrix = rating_matrix_save['rating_matrix'][:]
rating_matrix_save.close()
	
non_zeros_users = []
non_zeros_repos = []
non_zeros_ratings = []

for user in xrange(rating_matrix.shape[0]):
	for repo in xrange(rating_matrix.shape[1]):
		if( rating_matrix[user][repo] != 0 ):
			non_zeros_users.append(user)
			non_zeros_repos.append(repo)
			non_zeros_ratings.append(rating_matrix[user][repo])

non_zeros_values = zip(non_zeros_users, non_zeros_repos)

# train_x, test_x, train_y, test_y = train_test_split(non_zeros_values, non_zeros_ratings, test_size = 0.20, random_state = 42)
# np.savetxt("Train_X_2.txt", train_x)
# np.savetxt("Test_X_2.txt", test_x)
# np.savetxt("Train_Y_2.txt", train_y)
# np.savetxt("Test_Y_2.txt", test_y)

train_x = np.loadtxt("Train_X_2.txt")
train_y = np.loadtxt("Train_Y_2.txt")
test_x = np.loadtxt("Test_X_2.txt")
test_y = np.loadtxt("Test_Y_2.txt")


training_matrix = np.zeros(rating_matrix.shape)
p_matrix = np.zeros(rating_matrix.shape)
test_y_p = [1] * len(test_y)

for (x, y), rating in zip(train_x, train_y):
	p_matrix[int(x)][int(y)] = 1.0
	training_matrix[int(x)][int(y)] = rating

X = tf.placeholder("float32", [None, training_matrix.shape[1]])
X_prob = tf.placeholder("float32", [None, training_matrix.shape[1]])
mask = tf.placeholder("float32", [None, training_matrix.shape[1]])

matrix_mask = training_matrix.copy()
matrix_mask[matrix_mask.nonzero()] = 1 

learning_rate = 0.001
num_hidden_1 = [50]
lambda_list = [0.001]
mae = []
for hidden_layer_1 in num_hidden_1:
	minMae = 1000
	weights = {
		'encoder_h1': tf.Variable(tf.random_normal([training_matrix.shape[1], hidden_layer_1])),
		'decoder_h1': tf.Variable(tf.random_normal([hidden_layer_1, training_matrix.shape[1]])),
		}
	biases = {
		'encoder_b1': tf.Variable(tf.random_normal([hidden_layer_1])),
		'decoder_b1': tf.Variable(tf.random_normal([training_matrix.shape[1]])),
	}
	
	def encoder(x):
		layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['encoder_h1']), biases['encoder_b1']))
		return layer_1

	def decoder(x):
		layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['decoder_h1']), biases['decoder_b1']))
		return layer_1
	
	encoder_op = encoder(X)
	decoder_op = decoder(encoder_op)

	y_pred = decoder_op
	y_prob = X_prob
	y_true = X

	for lambda_val in lambda_list:

		temp_loss_1 = tf.pow(tf.norm(y_prob - tf.multiply(mask, y_pred), axis = 1), 2)
		temp_loss_2 = tf.norm(1.0 + tf.multiply(tf.constant(learning_rate, dtype="float32"), y_true))
		rmse_loss = tf.multiply(temp_loss_1, temp_loss_2)
		regularization = tf.multiply(tf.constant(lambda_val/2.0, dtype="float32"), tf.add(tf.pow(tf.norm(weights['decoder_h1']), 2), tf.pow(tf.norm(weights['encoder_h1']), 2)))
		loss = tf.add(tf.reduce_mean(rmse_loss), regularization)
		optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(loss)

		display_step = 100
		print("Stating!!!")
		init = tf.global_variables_initializer()
		with tf.Session() as sess:
			sess.run(init)
			num_steps = 5
			for k in range(1, num_steps+1):
				for i in range(0, training_matrix.shape[0]):
					vector_mask = training_matrix[i].copy()		
					vector_mask[vector_mask.nonzero()] = 1
					if( len(vector_mask.nonzero()[0]) == 0 ):
						continue
					_, l, l1, l_1, l_2 = sess.run([optimizer, loss, rmse_loss, temp_loss_1, temp_loss_2], feed_dict={X_prob: p_matrix[i].reshape(1, p_matrix.shape[1]), X: training_matrix[i].reshape( (1, training_matrix.shape[1]) ), mask: vector_mask.reshape( (1, training_matrix.shape[1]) )})
					# print(l_1, l_2)
					# if( i >= 10 ):
					# 	exit()
					if( args.debug[0] == 'yes' ):
						if i % display_step == 0 or i == 1:
							print('Step %i: Loss: %f' % (i, l))

			trained_data = sess.run(y_pred, feed_dict={X_prob: p_matrix, X: training_matrix, mask: matrix_mask})
			print("Ended!!")
			errorArray = []
			prediction = []
			true_pos = 0.0
			false_pos = 0.0
			for (x, y), rating in zip(test_x, test_y_p):
				if( trained_data[int(x)][int(y)] >= 0.45 ):
					true_pos += 1
					errorArray.append(0)
					prediction.append(1)
				else:
					false_pos += 1
					errorArray.append(1)
					prediction.append(0)
				# errorArray.append(abs(int(np.round(trained_data[x][y])) - rating))
			errorArray = np.array(errorArray)
			print("MAE = {0}, hidden_layer_1 = {1}, lambda_val = {2}".format(np.mean(errorArray), hidden_layer_1, lambda_val))
			if( minMae >= np.mean(errorArray) ):
				minMae = np.mean(errorArray)
			# print(precision_recall_fscore_support(test_y_p, prediction, average = "macro"))
			print("Precision = {}".format(true_pos/(true_pos + false_pos)))


		mae.append(minMae)

initTime2 = datetime.datetime.now()
print("Total time taken = {0}".format(initTime2 - initTime1))
