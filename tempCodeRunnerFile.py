import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pickle
from tensorflow import keras
from keras.layers import Input, Conv2D
INPUT_DIR = "D:/Deep learning/galaxy-image-classification-main/pca_dataset"
IMAGE_SIDE_SIZE = 128

CLASS_NAMES = ["elliptical", "spiral", "irregular", "invalid"]

X = np.load(os.path.join(INPUT_DIR, "images.npy"))
y = np.load(os.path.join(INPUT_DIR, "labels.npy"))

print(X.shape)
print(y.shape)

from sklearn.model_selection import train_test_split
from keras.utils import  to_categorical

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 11)

y_test = to_categorical(y_test, num_classes=4)
y_train = to_categorical(y_train, num_classes=4)

from keras.models import  Model
from keras.layers import Input, Dropout, Flatten, Dense, AveragePooling2D
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping

dropout_rate = 0.25

ip = Input(shape = (IMAGE_SIDE_SIZE, IMAGE_SIDE_SIZE, 3))

temp = Conv2D(filters = 3, kernel_size= (3,3), strides=(4,4), padding = "same", activation="relu")(ip)
temp = AveragePooling2D(pool_size=(4,4), padding = "same")(ip)# resizing with GPU

temp = Flatten()(temp)
temp = Dropout(dropout_rate)(temp)
temp = Dense(units = 8, activation= "relu")(temp)
temp = Dropout(dropout_rate)(temp)
op = Dense(units = 4, activation="softmax")(temp)

model = Model(inputs = ip, outputs = op)

model.summary()

# Defining a function for plotting training and validation learning curves
def plot_history(history):
	  # plot loss
    plt.title('Loss')
    plt.plot(history.history['loss'], color='blue', label='train')
    plt.plot(history.history['val_loss'], color='red', label='test')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'])
    plt.show()
    
    # plot accuracy
    plt.title('Accuracy')
    plt.plot(history.history['accuracy'], color='blue', label='train')
    plt.plot(history.history['val_accuracy'], color='red', label='test')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'])
    plt.show()

epochs = 200
batch_size = 64

callbacks = [
    EarlyStopping(monitor="val_loss", patience=30, verbose=1, restore_best_weights=True),
    # keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=10, min_lr=0.00001, verbose=1)
]

model.compile(optimizer=Adam(), loss="categorical_crossentropy", metrics = ["accuracy"])

history = model.fit(
    X_train,
    y_train,
    batch_size=batch_size,
    epochs=epochs,
    callbacks=callbacks,
    validation_split = 0.2,
    verbose=1,
    shuffle = True
)

model.evaluate(X_train, y_train)
model.evaluate(X_test, y_test)

plot_history(history)

y_test_pred = model.predict(X_test)
y_test_pred_sparse = np.argmax(y_test_pred, axis = -1).reshape(-1)
y_test_sparse = np.argmax(y_test, axis = -1).reshape(-1)


from sklearn.metrics import  confusion_matrix, classification_report
print(confusion_matrix(y_test_sparse, y_test_pred_sparse))
print(classification_report(y_test_sparse, y_test_pred_sparse))

import random
# sample images
cols = 3
rows = 3
plt.figure(figsize=(cols*5, rows*5))

h_test = model.predict(X_test)
h_test_sparse = np.argmax(h_test, axis = -1)
y_test_sparse = np.argmax(y_test, axis = -1)

for i in range(rows):
  for j in range(cols):
    ax = plt.subplot(rows, cols, i*cols + j+1)
    indx = random.randint(0, y_test.shape[0]-1)

    gt = y_test_sparse[indx]
    pred = h_test_sparse[indx]
    title_string = "GT:" + str(CLASS_NAMES[gt]) + "\nPRED:" + str(CLASS_NAMES[pred])

    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.set_title(title_string, fontdict={"fontsize": 20})
    ax.imshow(X_test[indx])


model.save(os.path.join("D:/Deep learning/galaxy-image-classification-main/CNNmodel", "mlp_model.h5"))

