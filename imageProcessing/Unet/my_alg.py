
import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
import skimage.transform as skt



#build U shape network for 32 x 32 image
# build U shape network for 32 x 32 image
def build_model_32_32():
    acf = keras.activations.relu

    img_input = keras.Input(shape=(32, 32, 1))
    # out 32 x 32 @

    block_0_in = keras.layers.Conv2D(32, 3, padding='same')(img_input)
    block_0 = keras.layers.BatchNormalization()(block_0_in)

    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0_in)
    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0)
    block_0 = keras.layers.BatchNormalization()(block_0)
    block_0 = keras.layers.add([block_0, block_0_in])

    # out 32 x 32 @ 16

    # down sample
    block_1_in = keras.layers.Conv2D(64, 2, 2, activation=acf)(block_0)
    block_1_in = keras.layers.BatchNormalization()(block_1_in)

    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1_in)
    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1)
    block_1 = keras.layers.BatchNormalization()(block_1)
    block_1 = keras.layers.add([block_1, block_1_in])

    # out 16 x 16 @ 32

    block_2_in = keras.layers.Conv2D(128, 2, 2, activation=acf)(block_1)
    block_2_in = keras.layers.BatchNormalization()(block_2_in)

    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2_in)
    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2)
    block_2 = keras.layers.BatchNormalization()(block_2)
    block_2 = keras.layers.add([block_2, block_2_in])

    # out 8 x 8 @ 64, end block 2

    block_3_in = keras.layers.Conv2D(256, 2, 2, activation=acf)(block_2)
    block_3_in = keras.layers.BatchNormalization()(block_3_in)
    # out 4 x 4 @128

    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3_in)
    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3)
    block_3 = keras.layers.BatchNormalization()(block_3)
    block_3 = keras.layers.add([block_3, block_3_in])
    # out 4 x 4 @128

    up_block_0 = keras.layers.Conv2DTranspose(128, 2, 2, activation=acf)(block_3)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    # out  8x8 @ 64

    # skip connestion
    up_block_0 = keras.layers.concatenate([block_2, up_block_0])

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0_in = keras.layers.BatchNormalization()(up_block_0)

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0_in)
    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    up_block_0 = keras.layers.add([up_block_0, up_block_0_in])
    # out 8 x 8 @ 128

    up_block_1 = keras.layers.Conv2DTranspose(64, 2, 2, activation=acf)(up_block_0)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    # out 16 x 16 @ 32

    # skip connection
    up_block_1 = keras.layers.concatenate([up_block_1, block_1])
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1_in = keras.layers.BatchNormalization()(up_block_1)

    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1_in)
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    up_block_1 = keras.layers.add([up_block_1, up_block_1_in])
    # out 16 x 16 @ 32

    up_block_2 = keras.layers.Conv2DTranspose(32, 2, 2, activation=acf)(up_block_1)
    up_block_2 = keras.layers.concatenate([up_block_2, block_0])
    # out 32 x 32 @ 32
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2_in = keras.layers.BatchNormalization()(up_block_2)

    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2_in)
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2 = keras.layers.BatchNormalization()(up_block_2)
    up_block_2 = keras.layers.add([up_block_2, up_block_2_in])
    # out = 32 x 32 @ 64

    # 1 x 1 conv
    out_img = keras.layers.Conv2D(64, 5, padding='same', activation=acf)(up_block_2)
    out_img = keras.layers.BatchNormalization()(out_img)
    out_img = keras.layers.Conv2D(1, 1, activation= keras.activations.sigmoid)(out_img)

    model = keras.Model(img_input, out_img)

    return model

def build_model_128_3layer():
    acf = tf.nn.relu
    img_input = keras.Input(shape=(128, 128, 1))
    # out 128 x 128 @

    block_0_in = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(img_input)
    block_0 = keras.layers.BatchNormalization()(block_0_in)

    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0_in)
    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0)
    block_0 = keras.layers.BatchNormalization( )(block_0)
    block_0 = keras.layers.add([block_0, block_0_in])

    # out 128 x 128 @ 32

    # down sample
    block_1_in = keras.layers.Conv2D(64, 2, 2, activation=acf)(block_0)
    block_1_in = keras.layers.BatchNormalization()(block_1_in)
    # 64 x 64 @ 64

    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1_in)
    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1)
    block_1 = keras.layers.BatchNormalization()(block_1)
    block_1 = keras.layers.add([block_1, block_1_in])
    # out 64 x 64 @ 64

    block_2_in = keras.layers.Conv2D(128, 2, 2, activation=acf)(block_1)
    block_2_in = keras.layers.BatchNormalization()(block_2_in)
    # 32 x 32 @ 128

    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2_in)
    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2)
    block_2 = keras.layers.BatchNormalization()(block_2)
    block_2 = keras.layers.add([block_2, block_2_in])

    # out 32 x 32 @ 128, end block 2

    block_3_in = keras.layers.Conv2D(256, 2, 2, activation=acf)(block_2)
    block_3_in = keras.layers.BatchNormalization()(block_3_in)
    # out 16 x 16 @128

    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3_in)
    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3)
    block_3 = keras.layers.BatchNormalization()(block_3)
    block_3 = keras.layers.add([block_3, block_3_in])
    # out 16 x 16 @256

    up_block_0 = keras.layers.Conv2DTranspose(128, 2, 2, activation=acf)(block_3)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    # out  32x32 @ 128

    # skip connestion
    up_block_0 = keras.layers.concatenate([block_2, up_block_0])

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0_in = keras.layers.BatchNormalization()(up_block_0)

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0_in)
    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    up_block_0 = keras.layers.add([up_block_0, up_block_0_in])
    # out 32 x 32 @ 64

    up_block_1 = keras.layers.Conv2DTranspose(64, 2, 2, activation=acf)(up_block_0)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    # out 64 x 64 @ 32

    # skip connection
    up_block_1 = keras.layers.concatenate([up_block_1, block_1])
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1_in = keras.layers.BatchNormalization()(up_block_1)

    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1_in)
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    up_block_1 = keras.layers.add([up_block_1, up_block_1_in])
    # out 64 x 64 @ 32

    up_block_2 = keras.layers.Conv2DTranspose(32, 2, 2, activation=acf)(up_block_1)
    up_block_2 = keras.layers.concatenate([up_block_2, block_0])
    # out 128 x 128 @ 32
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2_in = keras.layers.BatchNormalization()(up_block_2)

    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2_in)
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2 = keras.layers.BatchNormalization()(up_block_2)
    up_block_2 = keras.layers.add([up_block_2, up_block_2_in])
    # out = 128 x 128 @ 64

    # 1 x 1 conv
    out_img = keras.layers.Conv2D(3, 3, padding='same', activation=keras.activations.sigmoid)(up_block_2)
    model = keras.Model(img_input, out_img)

    return model


def build_model_128():
    acf = tf.nn.relu
    img_input = keras.Input(shape=(128, 128, 1))
    # out 32 x 32 @

    block_0_in = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(img_input)
    block_0 = keras.layers.BatchNormalization()(block_0_in)

    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0_in)
    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0)
    block_0 = keras.layers.BatchNormalization( )(block_0)
    block_0 = keras.layers.add([block_0, block_0_in])

    # out 128 x 128 @ 32

    # down sample
    block_1_in = keras.layers.Conv2D(64, 2, 2, activation=acf)(block_0)
    block_1_in = keras.layers.BatchNormalization()(block_1_in)
    # 64 x 64 @ 64

    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1_in)
    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1)
    block_1 = keras.layers.BatchNormalization()(block_1)
    block_1 = keras.layers.add([block_1, block_1_in])
    # out 64 x 64 @ 64

    block_2_in = keras.layers.Conv2D(128, 2, 2, activation=acf)(block_1)
    block_2_in = keras.layers.BatchNormalization()(block_2_in)
    # 32 x 32 @ 128

    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2_in)
    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2)
    block_2 = keras.layers.BatchNormalization()(block_2)
    block_2 = keras.layers.add([block_2, block_2_in])

    # out 32 x 32 @ 128, end block 2

    block_3_in = keras.layers.Conv2D(256, 2, 2, activation=acf)(block_2)
    block_3_in = keras.layers.BatchNormalization()(block_3_in)
    # out 16 x 16 @128

    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3_in)
    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3)
    block_3 = keras.layers.BatchNormalization()(block_3)
    block_3 = keras.layers.add([block_3, block_3_in])
    # out 16 x 16 @256

    up_block_0 = keras.layers.Conv2DTranspose(128, 2, 2, activation=acf)(block_3)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    # out  32x32 @ 128

    # skip connestion
    up_block_0 = keras.layers.concatenate([block_2, up_block_0])

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0_in = keras.layers.BatchNormalization()(up_block_0)

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0_in)
    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    up_block_0 = keras.layers.add([up_block_0, up_block_0_in])
    # out 8 x 8 @ 128

    up_block_1 = keras.layers.Conv2DTranspose(64, 2, 2, activation=acf)(up_block_0)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    # out 16 x 16 @ 32

    # skip connection
    up_block_1 = keras.layers.concatenate([up_block_1, block_1])
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1_in = keras.layers.BatchNormalization()(up_block_1)

    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1_in)
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    up_block_1 = keras.layers.add([up_block_1, up_block_1_in])
    # out 16 x 16 @ 32

    up_block_2 = keras.layers.Conv2DTranspose(32, 2, 2, activation=acf)(up_block_1)
    up_block_2 = keras.layers.concatenate([up_block_2, block_0])
    # out 32 x 32 @ 32
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2_in = keras.layers.BatchNormalization()(up_block_2)

    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2_in)
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2 = keras.layers.BatchNormalization()(up_block_2)
    up_block_2 = keras.layers.add([up_block_2, up_block_2_in])
    # out = 32 x 32 @ 64

    # 1 x 1 conv
    out_img = keras.layers.Conv2D(1, 3, padding='same', activation=keras.activations.sigmoid)(up_block_2)
    model = keras.Model(img_input, out_img)

    return model

def build_model_128_color():
    acf = tf.nn.relu
    img_input = keras.Input(shape=(128, 128, 3))
    # out 32 x 32 @

    block_0_in = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(img_input)
    block_0 = keras.layers.BatchNormalization()(block_0_in)

    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0_in)
    block_0 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(block_0)
    block_0 = keras.layers.BatchNormalization( )(block_0)
    block_0 = keras.layers.add([block_0, block_0_in])

    # out 128 x 128 @ 32

    # down sample
    block_1_in = keras.layers.Conv2D(64, 2, 2, activation=acf)(block_0)
    block_1_in = keras.layers.BatchNormalization()(block_1_in)
    # 64 x 64 @ 64

    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1_in)
    block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(block_1)
    block_1 = keras.layers.BatchNormalization()(block_1)
    block_1 = keras.layers.add([block_1, block_1_in])
    # out 64 x 64 @ 64

    block_2_in = keras.layers.Conv2D(128, 2, 2, activation=acf)(block_1)
    block_2_in = keras.layers.BatchNormalization()(block_2_in)
    # 32 x 32 @ 128

    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2_in)
    block_2 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(block_2)
    block_2 = keras.layers.BatchNormalization()(block_2)
    block_2 = keras.layers.add([block_2, block_2_in])

    # out 32 x 32 @ 128, end block 2

    block_3_in = keras.layers.Conv2D(256, 2, 2, activation=acf)(block_2)
    block_3_in = keras.layers.BatchNormalization()(block_3_in)
    # out 16 x 16 @128

    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3_in)
    block_3 = keras.layers.Conv2D(256, 3, padding='same', activation=acf)(block_3)
    block_3 = keras.layers.BatchNormalization()(block_3)
    block_3 = keras.layers.add([block_3, block_3_in])
    # out 16 x 16 @256

    up_block_0 = keras.layers.Conv2DTranspose(128, 2, 2, activation=acf)(block_3)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    # out  32x32 @ 128

    # skip connestion
    up_block_0 = keras.layers.concatenate([block_2, up_block_0])

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0_in = keras.layers.BatchNormalization()(up_block_0)

    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0_in)
    up_block_0 = keras.layers.Conv2D(128, 3, padding='same', activation=acf)(up_block_0)
    up_block_0 = keras.layers.BatchNormalization()(up_block_0)
    up_block_0 = keras.layers.add([up_block_0, up_block_0_in])
    # out 8 x 8 @ 128

    up_block_1 = keras.layers.Conv2DTranspose(64, 2, 2, activation=acf)(up_block_0)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    # out 16 x 16 @ 32

    # skip connection
    up_block_1 = keras.layers.concatenate([up_block_1, block_1])
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1_in = keras.layers.BatchNormalization()(up_block_1)

    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1_in)
    up_block_1 = keras.layers.Conv2D(64, 3, padding='same', activation=acf)(up_block_1)
    up_block_1 = keras.layers.BatchNormalization()(up_block_1)
    up_block_1 = keras.layers.add([up_block_1, up_block_1_in])
    # out 16 x 16 @ 32

    up_block_2 = keras.layers.Conv2DTranspose(32, 2, 2, activation=acf)(up_block_1)
    up_block_2 = keras.layers.BatchNormalization()(up_block_2)
    up_block_2 = keras.layers.concatenate([up_block_2, block_0])

    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2_in = keras.layers.BatchNormalization()(up_block_2)

    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2_in)
    up_block_2 = keras.layers.Conv2D(32, 3, padding='same', activation=acf)(up_block_2)
    up_block_2 = keras.layers.BatchNormalization()(up_block_2)
    up_block_2 = keras.layers.add([up_block_2, up_block_2_in])
    # out = 32 x 32 @ 64

    # 1 x 1 conv
    out_img = keras.layers.Conv2D(3, 3, padding='same', activation=keras.activations.sigmoid)(up_block_2)
    model = keras.Model(img_input, out_img)

    return model

def norm_img(x):
    x = x - np.min(x)
    x = x / np.max(x)
    return x

def show_some_results(x, y, y_pred, num_rows, indexes = None, img_size=5, resize_shape=(128, 128)):


    x = np.squeeze(x)
    y = np.squeeze(y)
    y_pred = np.squeeze(y_pred)

    if indexes is None:

        indexes = np.random.permutation(range(len(x)))

    fig, axs = plt.subplots(num_rows, 4, figsize=(4 * img_size, num_rows * img_size))
    for row in range(num_rows):
        sid = indexes[row]
        ax = axs[row]
        ax[0].imshow(
            skt.resize(norm_img(x[sid]), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
        ax[0].axis('off')
        ax[1].imshow(
            skt.resize(norm_img(y[sid]), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
        ax[1].axis('off')
        ax[2].imshow(
            skt.resize(norm_img(y_pred[sid]), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
        ax[2].axis('off')
        ax[3].imshow(
            skt.resize(np.abs(norm_img(y_pred[sid]) - norm_img(y[sid])), output_shape=resize_shape, anti_aliasing=True,
                       mode='constant', cval=0))
        ax[3].axis('off')
    return fig

def show_some_results_3layer(x, y, y_pred, num_rows, indexes = None, img_size=5, resize_shape=(128, 128)):


    x = np.squeeze(x)
    y = np.squeeze(y)
    y_pred = np.squeeze(y_pred)

    if indexes is None:

        indexes = np.random.permutation(range(len(x)))

    fig, axs = plt.subplots(num_rows, 6, figsize=(6 * img_size, num_rows * img_size))
    for row in range(num_rows):
        sid = indexes[row]
        ax = axs[row]
        ax[0].imshow(
            skt.resize(norm_img(x[sid]), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
        ax[0].axis('off')
        ax[1].imshow(
            skt.resize(norm_img(y[sid]), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
        ax[1].axis('off')
        ax[2].imshow(
            skt.resize(norm_img(y_pred[sid][:,:,0]), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
        ax[2].axis('off')
        ax[3].imshow(
            skt.resize(np.abs(norm_img(y_pred[sid]) - norm_img(y[sid])), output_shape=resize_shape, anti_aliasing=True,
                       mode='constant', cval=0))
        ax[3].axis('off')
    return fig

def show_random_sampels( imgs, num_row, num_col, idx = None, img_size = 5, resize_shape = (128,128)):
    imgs = np.squeeze( imgs)

    N = len(imgs)
    if idx is None:
        idx  = np.random.choice( range(N), num_row * num_col, replace= False)
    img_to_show = imgs[idx]

    fig, axs = plt.subplots( num_row, num_col,squeeze= False,  figsize = ( num_col * img_size, num_row * img_size ))

    for r in range( num_row):
        for c in range( num_col):
            img = img_to_show[r * num_col + c]
            ax = axs[r,c]
            ax.axis('off')
            ax.imshow( skt.resize( norm_img( img), output_shape=resize_shape, anti_aliasing=True, mode='constant', cval=0))
    return fig



def apply_forward_model(A, x, im_size,  noise_sigma = 0):
    '''apply forward model to input x
    x should be the shape (N_batch, height, width,1)
    '''
    if A.shape[0] != im_size ** 2 or A.shape[1] != im_size ** 2:
        raise NameError("Size not match")

    if len(x.shape) < 3:
        raise NameError('Dimension error')

    x = np.squeeze(x)
    if x.shape[1] != im_size or x.shape[2] != im_size:
        raise NameError("size not match")

    N = len(x)
    x = x.reshape(len(x), -1)
    b = x @ A

    # normalise b
    b = b / np.max(b, axis=1).reshape(-1, 1)

    #adding noise
    noise = np.random.standard_normal(b.shape) * noise_sigma
    b += noise

    b = b.reshape(N, im_size, im_size, 1)

    return b


def resize_data_set( x, out_shape = (128,128), add_dim = True):
    x = np.squeeze(x)

    out = []
    for img in x:
        img = skt.resize( norm_img(img), output_shape=out_shape,anti_aliasing=True, mode='constant', cval = 0).astype( np.float32)
        out.append( img)

    out = np.array( out)

    if add_dim == True:
        out = np.expand_dims( out, -1)

    return out


def average_SSIM( y_true, y_pred):
    ssims = []
    y_true = np.squeeze( y_true)
    y_pred = np.squeeze( y_pred)

    if len( y_true) !=  len( y_pred):
        raise  NameError("length not match!")

    for i in range(len(y_pred)):
        x = y_pred[i]
        y = y_true[i]
        ssims.append(ssim(x, y))
    ssims = np.array(ssims)
    ave_ssim = np.average(ssims)

    return ssims

def average_MAE( y_true, y_pred):
    mae = []
    y_true = np.squeeze( y_true)
    y_pred = np.squeeze( y_pred)

    if len( y_true) !=  len( y_pred):
        raise  NameError("length not match!")
    a,b = size(y_true[1])
    for i in range(len(y_pred)):
        x = y_pred[i]
        y = y_true[i]
        d = abs(x-y)
        m = sum(sum(d))/(a*b)
        mae.append(ssim(x, y))
    mae = np.array(mae)
#    ave_ssim = np.average(ssims)

    return mae


#functions for prepare data set
def split_data_set(data, p_val=0.2, p_test=0.1, seed=None):
    '''Seperate data set to training, validation and test
    args:
        data: array like of shape [ batch, ...]
        p_val: portion of validation
        p_test: portion of test

    return (data_train, data_val, data_test), ( train_idx, val_idx, test_idx)
    '''

    num_elems = len(data)
    num_train = int(num_elems * (1 - p_val - p_test))
    num_val = int(num_elems * p_val)
    num_test = num_elems - num_train - num_val

    if num_test <= 0:
        raise NameError('num error')

    if seed:
        np.random.seed(seed=seed)

    random_idx = np.random.permutation(range(num_elems))

    train_idx = random_idx[:num_train]
    val_idx = random_idx[num_train: num_train + num_val]
    test_idx = random_idx[num_train + num_val:]

    data_train, data_val, data_test = data[train_idx], data[val_idx], data[test_idx]

    return (data_train, data_val, data_test), (train_idx, val_idx, test_idx)


def ave_cross_en( y_true, y_pred):
    loss = ( keras.losses.kullback_leibler_divergence( y_true, y_pred) +  keras.losses.kld( 1 - y_true, 1- y_pred))
    return loss


def test_tp_minst():
    mnist_x = np.load('tp_mnist_x.npy')
    mnist_b = np.load( 'tp_mnist_b.npy')

    model = build_model_128()
    model.compile(optimizer=keras.optimizers.Adam(3e-4), loss=ave_cross_en, metrics=['mae'])
    model.fit(mnist_b, mnist_x, batch_size=16, epochs=5, verbose=1, validation_split=0.1 )
    model.save('tp_mnist_128.model')



if __name__ == '__main__':
    test_tp_minst()