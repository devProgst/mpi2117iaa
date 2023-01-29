from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers.legacy import Adam # оптимизатор
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import clone_model
from nodeLogger import *
import tensorflow as tf
import numpy as np
import time
import pickle

class Model:
	def __init__(self, dsPart = 6, modelName="default"):
		self.name = modelName
		cleanLog(self.name)

		self.epochs    = 10
		self.batchSize = 32
		self.init_LR   = 1e-3
		self.load_model()

		# Dataset
		((self.dsX, self.dsY), (self.testX, self.testY)) = mnist.load_data()
		self.dsP = dsPart
		self.dsX = np.expand_dims(self.dsX, axis=-1)
		self.dsX = self.dsX.astype("float32") / 255.0
		self.dsY = to_categorical(self.dsY, 10)
		self.setRandomDS()

		self.testX = np.expand_dims(self.testX, axis=-1)
		self.testX = self.testX.astype("float32") / 255.0
		self.testY = to_categorical(self.testY, 10)
	def rebuild_model(self, width, height, depth, classes):
		inputShape = (height, width, depth)
		chanDim = -1
		model = Sequential([
			# CONV => RELU => BN => POOL layer set
			Conv2D(16, (3, 3), padding="same", input_shape=inputShape),
			Activation("relu"),
			BatchNormalization(axis=chanDim),
			MaxPooling2D(pool_size=(2, 2)),
			# (CONV => RELU => BN) * 2 => POOL layer set
			Conv2D(32, (3, 3), padding="same"),
			Activation("relu"),
			BatchNormalization(axis=chanDim),
			Conv2D(32, (3, 3), padding="same"),
			Activation("relu"),
			BatchNormalization(axis=chanDim),
			MaxPooling2D(pool_size=(2, 2)),
			# (CONV => RELU => BN) * 3 => POOL layer set
			Conv2D(64, (3, 3), padding="same"),
			Activation("relu"),
			BatchNormalization(axis=chanDim),
			Conv2D(64, (3, 3), padding="same"),
			Activation("relu"),
			BatchNormalization(axis=chanDim),
			Conv2D(64, (3, 3), padding="same"),
			Activation("relu"),
			BatchNormalization(axis=chanDim),
			MaxPooling2D(pool_size=(2, 2)),
			# first (and only) set of FC => RELU layers
			Flatten(),
			Dense(256),
			Activation("relu"),
			BatchNormalization(),
			Dropout(0.5),
			# softmax classifier
			Dense(classes),
			Activation("softmax")
		])
		self.model = model
		self.opt = Adam(learning_rate=self.init_LR, decay=self.init_LR / self.epochs)

	def save_model(self, model_name):
		self.model.save(model_name)

	def load_model(self, model_name='sharedModel.h5'):
		self.model = tf.keras.models.load_model(model_name)
		self.opt = Adam(learning_rate=self.init_LR, decay=self.init_LR / self.epochs)
		self.optTrain = Adam(learning_rate=self.init_LR, decay=self.init_LR / self.epochs)

	def setRandomDS(self):
		print("Get random dataset...")
		dsCount = len(self.dsX) // self.dsP
		indices = tf.range(start=0, limit=len(self.dsX), dtype=tf.int32)
		idx = tf.random.shuffle(indices)[:dsCount]
		self.trainX = tf.gather(self.dsX, idx)
		self.trainY = tf.gather(self.dsY, idx)

	def step(self, model, optimizer, X, y):
		with tf.GradientTape() as tape:
			pred = model(X)
			loss = categorical_crossentropy(y, pred)
		stepGradient = tape.gradient(loss, model.trainable_variables)
		optimizer.apply_gradients(zip(stepGradient, model.trainable_variables))
		return stepGradient

	def train(self):
		# temp
		trainModel = clone_model( self.model )

		# start train
		lastGradients = []
		for epoch in range(0, self.epochs):
			print("[train] Обучение. Эпоха: {}/{}...".format(epoch + 1, self.epochs), end="\r")
			epochStart = time.time()
			end = np.random.randint(self.batchSize, len(self.trainX) - self.batchSize)
			start = end - self.batchSize
			for i in range(0, 10):
				lastGradients.append( self.step( trainModel, self.optTrain, self.trainX[start:end], self.trainY[start:end] ) )
			epochEnd = time.time()
			elapsed = (epochEnd - epochStart) / 60.0
		trainModel.compile(optimizer=self.optTrain, loss=categorical_crossentropy,	metrics=["acc"])
		(loss, acc) = trainModel.evaluate(self.testX, self.testY, verbose=2)
		print("[train] Точность модели после обучения: {:.4f}".format(acc))
		writeLog(self.name, 'main', loss, acc)
		return lastGradients

	def aggAndApplyGrads(self, gradsList):
		ag = gradsList[0]
		for g in gradsList[1:]:
			for i in range( len(g) ):
				for t in range( len(g[i]) ):
					ag[i][t] += g[i][t]
		for i in range( len(ag) ):
			for t in range( len(ag[i]) ):
				ag[i][t] /= len(gradsList)
			self.opt.apply_gradients(zip(ag[i], self.model.trainable_variables))
		self.model.compile(optimizer=self.opt, loss=categorical_crossentropy,	metrics=["acc"])
		(loss, acc) = self.model.evaluate(self.testX, self.testY, verbose=2)
		writeLog(self.name, 'mix', loss, acc)