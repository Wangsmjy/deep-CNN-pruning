from VGG16 import VGG16
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
flags.DEFINE_float("l2_lambda", 0.01, "l2 term lambda")
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
#                 batch_x ,batch_label= None
#                 sess.run(train_step,feed_dict={vgg.x:batch_x,vgg.y_:batch_label})
#                 if i%100==0:
#                     loss = sess.run(vgg.cross_entropy, feed_dict={vgg.x: test_x, vgg.y_: test_label})
#                     print(str(i) + "/" + str(batch_num) + " batch: loss is " + str(loss))
#             loss,acc = sess.run([vgg.cross_entropy,vgg.accaury], feed_dict={vgg.x: test_x, vgg.y_: test_label})
#             print(str(epoch) + " epoch: loss is " + str(loss) + ",accuary is " + str(acc))
#     print("Training end!")

def run_vgg_cifar10(batch_size, epoch_num, dataset_path, learning_rate, testset_size, l2_lambda, checkpoint_dir):
    WEIGHT_SAVER_DIR = os.path.join(checkpoint_dir,'vgg16_cifar_epoch')
    train_file = glob(os.path.join(dataset_path, 'data*'))
    train_x,train_label = util.data_read(train_file)
    print("Train data load success,Train set shape:{}".format(train_x.shape))

    test_file = glob(os.path.join(dataset_path, 'test*'))
    test_x,test_label = util.data_read(test_file)
    print("Test data load success,Test set shape:{}".format(test_x.shape))

    vgg = VGG16Cifar10(l2_lambda)
    vgg.build_model()
    train_step = vgg.get_train_step(learning_rate,ues_regularizer=True)

    print("Model build success!")
    train_data_size = len(train_label)
    batch_num = train_data_size//batch_size
    saver = tf.train.Saver(max_to_keep=1)
    max_acc = 0.8
    with tf.Session() as sess:
        try:
            saver.restore(sess, WEIGHT_SAVER_DIR)
            print("Checkpoint load success!")
        except ValueError:
            sess.run(tf.global_variables_initializer())
            print("No checkpoint file,weight inited!")
        print("Training starts...")
        for epoch in range(epoch_num):
            for i in range(batch_num):
                batch_x = train_x[i*batch_size : min(i*batch_size+batch_size,train_data_size)]
                batch_label = train_label[i*batch_size : min(i*batch_size+batch_size,train_data_size)]
                sess.run(train_step, feed_dict={vgg.x: batch_x, vgg.y_: batch_label, vgg.isTrain:True})
                if i % 100 == 0:
                    loss,acc = sess.run([vgg.loss,vgg.accaury], feed_dict={vgg.x: test_x[0:testset_size], vgg.y_: test_label[0:testset_size], vgg.isTrain:False})
                    train_loss, train_acc = sess.run([vgg.loss,vgg.accaury], feed_dict={vgg.x: batch_x, vgg.y_: batch_label, vgg.isTrain:False})
                    print("{}/{} batch: loss is {},acc is {}. on train set:{},{}".format(i,batch_num,loss,acc,train_loss,train_acc))
            loss, acc = sess.run([vgg.loss, vgg.accaury], feed_dict={vgg.x: test_x, vgg.y_: test_label, vgg.isTrain:False})
            print("{} epoch: loss is {},accuary is {}".format(epoch,loss,acc))
            if acc>max_acc:
                saver.save(sess, WEIGHT_SAVER_DIR)
                max_acc = acc
                print("{} epoch weight save success!".format(epoch))
        print("Training end!")




def main(_):
    batch_size = FLAGS.batch_size
    epoch_num = FLAGS.epoch
    dataset_path = os.path.join(sys.path[0],'data', FLAGS.dataset)
    learning_rate = FLAGS.learning_rate
    testset_size = FLAGS.testset_size
    l2_lambda = FLAGS.l2_lambda
    checkpoint_dir = FLAGS.checkpoint_dir

    run_vgg_cifar10(batch_size, epoch_num, dataset_path, learning_rate, testset_size, l2_lambda, checkpoint_dir)

if __name__ == '__main__':
  tf.app.run()