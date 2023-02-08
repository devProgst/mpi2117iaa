import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
print("Ожидание инициализации tensorflow...")
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
from nodeLogger import *
import tensorflow as tf
import numpy as np
import time

class Model:
	def __init__(self, dsSplit = 6, modelName="default_model.log", init_lr=1e-4):
		self.name = modelName
		cleanLog(self.name)
		self.init_lr = init_lr
		self.load_model()
		self.prepare_dataset(dsSplit)
		self.last_gradient = None
		
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
		self.opt = Adam(learning_rate=self.init_lr, decay=self.init_lr)

	def save_model(self, model_name):
		self.model.save(model_name)

	def load_model(self, model_name='sharedModel.h5'):
		self.model = tf.keras.models.load_model(model_name)
		self.opt = Adam(learning_rate=self.init_lr, decay=self.init_lr)

	def prepare_dataset(self, split):
		print("Подготовка датасета...", end="\r")
		((self._trainX, self._trainY), (self.testX, self.testY)) = mnist.load_data()
		self.dsS = split

		# Набор для обучения
		self._trainX = np.expand_dims(self._trainX, axis=-1)
		self._trainX = self._trainX.astype("float32") / 255.0
		self._trainCategories = {c:[] for c in range(10)}
		for i,v in enumerate(self._trainY):
			self._trainCategories[v].append(i)			
		self._trainY = to_categorical(self._trainY, 10)

		# Тестовый набор
		self.testX = np.expand_dims(self.testX, axis=-1)
		self.testX = self.testX.astype("float32") / 255.0
		self.testY = to_categorical(self.testY, 10)

		self.random_dataset()

	def random_dataset(self):
		print("Формирование случайной сбалансированной части датасета...")
		dsCountSplitted = len(self._trainX) // self.dsS # к-во эл-тов в части датасета
		dsCountInCat = dsCountSplitted // 10 # к-во эл-тов в каждой категории
		dsPickIndexes = []
		# Формирование сбалансированного упорядоченного датасета:
		for i in self._trainCategories.keys():
			np.random.shuffle( self._trainCategories[i] )
			dsPickIndexes += self._trainCategories[i][:dsCountInCat]
		np.random.shuffle(dsPickIndexes)
		self.trainX = self._trainX[ dsPickIndexes ]
		self.trainY = self._trainY[ dsPickIndexes ]

	def step(self, X, y):
		with tf.GradientTape() as tape:
			pred = self.model(X)
			loss = categorical_crossentropy(y, pred)
		grad = tape.gradient(loss, self.model.trainable_variables)
		self.opt.apply_gradients(zip(grad, self.model.trainable_variables))

	def train(self, cancelTrain=True, epochs=12, batchSize=64):
		W0 = self.model.get_weights()
		updCount = len(self.trainX) // batchSize
		for epoch in range(0, epochs):
			print("[train]\tЭпоха: {}/{}...".format(epoch + 1, epochs),end="\r\t\t\t")
			epochStart = time.time()
			for i in range(updCount):
				start = i*batchSize
				end = start+batchSize
				self.step(self.trainX[start:end], self.trainY[start:end])
				print("Пройдено батчей:", i, "из", updCount, end="\r\t\t\t")
			epochEnd = time.time()
			elapsed = (epochEnd - epochStart)
			print("Эпоха завершена полностью. ->", ( (str(round(elapsed,2)) + "сек.") if elapsed < 60 else (str(round(elapsed/60,2)) + "мин.")), end="\r\t\t\t\n")
			self.checkAccuracy() # проверить точность и внести в лог обучения
		W = self.model.get_weights()
		if cancelTrain: self.model.set_weights(W0)
		return list(W[i]-W0[i] for i,_ in enumerate(W0))

	def checkAccuracy(self, tag='main', comment=None):
		self.model.compile(optimizer=self.opt, loss=categorical_crossentropy,	metrics=["acc"])
		(loss, acc) = self.model.evaluate(self.testX, self.testY, verbose=0)
		print("[train] Точность обучения модели: {:.2f}%".format(acc*100))
		writeLog(self.name, tag, loss, acc, comment)

	def applyAggGrads(self, grads, balance=None):
		balance = [1.0]*len(grads) if balance is None else balance[:len(grads)]
		if len(grads) != len(balance): raise Exception("Количество градиентов и коэффициентов не совпадает!")
		elif len(grads) <= 0 or grads == None: return None
		# aggregate gradients & mult self balance
		for i,grad in enumerate(grads):
			for l,_ in enumerate(grad):
				if i == 0: grads[i][l] *= balance[i]
				else: grads[0][l] += grads[i][l] * balance[i]
		w0 = self.model.get_weights()
		# normalize & apply gradients
		for i,layer in enumerate(grads[0]):
			w0[i] += layer / sum(balance)
		self.model.set_weights(w0)

if __name__ == "__main__":
	m = Model(20, "test_model.log")
	g1 = m.train(epochs = 3)
	g2 = m.train(epochs = 3)
	m.applyAggGrads([ g1, g2 ], [ 1, 0.25 ])
	m.checkAccuracy()