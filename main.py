from VGG16Imagenet import VGG16Imagenet
from VGG16Cifar10 import VGG16Cifar10
import tensorflow as tf
import numpy as np
import os
from glob import glob
import util
import sys

flags = tf.app.flags
flags.DEFINE_integer("epoch", 25, "Epoch to train [25]")
flags.DEFINE_float("learning_rate", 0.0002, "Learning rate of for adam [0.0002]")
flags.DEFINE_float("train_size", np.inf, "The size of train images [np.inf]")
flags.DEFINE_integer("batch_size", 64, "The size of batch images [64]")
flags.DEFINE_string("dataset", None, "The name of dataset [celebA, mnist, lsun]")
flags.DEFINE_string("checkpoint_dir", "checkpoint", "Directory name to save the checkpoints [checkpoint]")
flags.DEFINE_boolean("train", False, "True for training, False for testing [False]")
flags.DEFINE_integer("testset_size", 32, "testset size [32]")
FLAGS = flags.FLAGS

# def run():
#     batch_size = 64
#     train_data_size = None
#     epoch_num = FLAGS.epoch
#
#     test_x, test_label = None
#
#     vgg = VGG16Imagenet()
#     vgg.build_model()
#     train_step = vgg.get_train_step(0.02)
#
#     print("Training starts!")
#     batch_num = batch_size/train_data_size
#     with tf.Session() as sess:
#         for epoch in range(epoch_num):
#             for i in range(batch_num):
#                 batch_x ,batch_label= None #batch_x和batch_label需要在这里进行赋值
#                 sess.run(train_step,feed_dict={vgg.x:batch_x,vgg.y_:batch_label})
#                 if i%100==0:
#                     loss = sess.run(vgg.cross_entropy, feed_dict={vgg.x: test_x, vgg.y_: test_label})
#                     print(str(i) + "/" + str(batch_num) + " batch: loss is " + str(loss))
#             loss,acc = sess.run([vgg.cross_entropy,vgg.accaury], feed_dict={vgg.x: test_x, vgg.y_: test_label})
#             print(str(epoch) + " epoch: loss is " + str(loss) + ",accuary is " + str(acc))
#     print("Training end!")

def run_vgg_cifar10(batch_size, epoch_num, dataset_path, learning_rate, testset_size):
    train_file = glob(os.path.join(dataset_path, 'data*1'))
    train_x,train_label = util.data_read(train_file)
    train_x = np.reshape(train_x,(-1, 32, 32, 3))
    print(train_x.shape)

    test_file = glob(os.path.join(dataset_path, 'test*'))
    test_x,test_label = util.data_read(test_file)
    test_x = np.reshape(test_x, (-1, 32, 32, 3))
    print(test_x.shape)
    train_data_size = len(train_label)
    print('Total train sample number is ' + str(train_data_size))

    vgg = VGG16Cifar10()
    vgg.build_model()
    train_step = vgg.get_train_step(learning_rate)

    print("Model build success!")
    batch_num = train_data_size//batch_size
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        print("Training starts...")
        for epoch in range(epoch_num):
            for i in range(batch_num):
                batch_x = train_x[i*batch_size : min(i*batch_size+batch_size,train_data_size)]
                batch_label = train_label[i*batch_size : min(i*batch_size+batch_size,train_data_size)]
                # y = sess.run(vgg.y, feed_dict={vgg.x: batch_x, vgg.y_: batch_label})
                sess.run(train_step, feed_dict={vgg.x: batch_x, vgg.y_: batch_label})
                # print(str(i)+":y is "+str(y))
                if i % 5 == 0:
                    loss,acc = sess.run([vgg.cross_entropy,vgg.accaury], feed_dict={vgg.x: test_x[0:testset_size], vgg.y_: test_label[0:testset_size]})
                    print(str(i) + "/" + str(batch_num) + " batch: loss is " + str(loss) + ",acc is "+str(acc))
            loss, acc = sess.run([vgg.cross_entropy, vgg.accaury], feed_dict={vgg.x: test_x[0:testset_size], vgg.y_: test_label[0:testset_size]})
            print(str(epoch) + " epoch: loss is " + str(loss) + ",accuary is " + str(acc))
    print("Training end!")

def main(_):
    # if FLAGS.input_width is None:
    #     FLAGS.input_width = FLAGS.input_height
    # if FLAGS.output_width is None:
    #     FLAGS.output_width = FLAGS.output_height
    batch_size = FLAGS.batch_size
    epoch_num = FLAGS.epoch
    dataset_path = os.path.join(sys.path[0],'data', FLAGS.dataset)
    learning_rate = FLAGS.learning_rate
    testset_size = FLAGS.testset_size

    run_vgg_cifar10(batch_size, epoch_num, dataset_path, learning_rate, testset_size)

if __name__ == '__main__':
  tf.app.run()