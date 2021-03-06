from VGG16 import VGG16
from VGG16SEBlock import VGG16SEBlock
from ResNet20 import ResNet20
from ResNet20SEBlock import ResNet20SEBlock
import tensorflow as tf
from util import Cifar10Dataset
import numpy as np
from prune import vgg_prune,tensor_shape_to_int,seblock_channel_select,seblock_prune

flags = tf.app.flags
flags.DEFINE_integer("epoch", 100, "Epoch to train [25]")
flags.DEFINE_float("learning_rate", 0.1, "Learning rate of for adam [0.0002]")
flags.DEFINE_integer("batch_size", 128, "The size of batch images [64]")
flags.DEFINE_string("dataset", "data/cifar-10-batches-py", "The name of dataset [celebA, mnist, lsun]")
flags.DEFINE_string("checkpoint_dir", "checkpoint", "Directory name to save the checkpoints [checkpoint]")
flags.DEFINE_integer("testset_size", 1000, "testset size [32]")
flags.DEFINE_float("l2_lambda", 0.0001, "l2 term lambda")
flags.DEFINE_float("l1_lambda", 0, "l1 term lambda")
flags.DEFINE_string("model_name", "VGG16Cifar10", "model to train")
FLAGS = flags.FLAGS

def train(batch_size, epoch_num, data_set, learning_rate, testset_size, checkpoint_dir, model, ues_regularizer=False):
    train_step = model.get_train_step(learning_rate, ues_regularizer)
    var_dict = model.get_needrestore_variable()
    saver = tf.train.Saver(var_dict, max_to_keep=1)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        load_result = model.load_weight(sess, saver, checkpoint_dir)
        if load_result == True:
            print("Checkpoint load success!")
        else:
            print("No checkpoint file,weight inited!")

        # se, loss, acc = sess.run([model.seblock_output[0], model.loss, model.accaury],
        #                      feed_dict={model.x: data_set.test_x, model.y_: data_set.test_label, model.isTrain: False})
        # print("Model init stat: loss is {},accuary is {}".format(loss, acc))
        # print("seblock output is {}".format(se[0]))
        # max_acc = max(acc, 0.84)
        # train_data_size = len(data_set.train_label)
        # batch_num = train_data_size // batch_size
        # for epoch in range(10):
        #     # 每个epoch都打乱数据顺序
        #     random_order = np.random.permutation(train_data_size)
        #     for i in range(batch_num):
        #         batch_index = random_order[i * batch_size: min(i * batch_size + batch_size, train_data_size)]
        #         batch_x = data_set.train_x[batch_index]
        #         batch_label = data_set.train_label[batch_index]
        #         # 数据增强
        #         batch_x = data_set.data_argument(batch_x)
        #         batch_x = data_set.normalize(batch_x)
        #         sess.run(train_step, feed_dict={model.x: batch_x, model.y_: batch_label, model.isTrain: True})
        #         if i % 100 == 0:
        #             train_loss, train_acc = sess.run([model.loss, model.accaury],
        #                                              feed_dict={model.x: batch_x,
        #                                                         model.y_: batch_label,
        #                                                         model.isTrain: False})
        #             print("{}/{} batch: train loss is {:.3f},acc is {:.2f}.".format(i, batch_num,train_loss, train_acc))
        #     se, loss, acc = sess.run([model.seblock_output[0], model.loss, model.accaury],
        #                          feed_dict={model.x: data_set.test_x, model.y_: data_set.test_label, model.isTrain: False})
        #     print("seblock output is {}".format(se[0]))
        #     print("{} epoch: loss is {},accuary is {}".format(epoch, loss, acc))
        #     # if acc > max_acc:
        #     #     saver.save(sess, "{}_{:.2f}".format(checkpoint_dir, acc))
        #     #     max_acc = acc
        #     #     print("{} epoch weight save success!".format(epoch))
        # print("Training end!")
        # saver2 = tf.train.Saver(max_to_keep=1)
        # saver2.save(sess, "{}_after_setrain".format(checkpoint_dir))
        # print("Checkpoint saved, acc is {.4f}".format(acc))
        vgg_prune(sess,data_set,model,"block_1/conv_layer_1", "block_1/conv_layer_2",0.3,0)
        saver.save(sess, "{}_after_pruning".format(checkpoint_dir))

def main(_):
    batch_size = FLAGS.batch_size
    epoch_num = FLAGS.epoch
    dataset_path =  FLAGS.dataset
    learning_rate = FLAGS.learning_rate
    testset_size = FLAGS.testset_size
    l2_lambda = FLAGS.l2_lambda
    checkpoint_dir = FLAGS.checkpoint_dir
    model_name = FLAGS.model_name
    ues_regularizer = False
    l1_lambda = FLAGS.l1_lambda

    cifar10 = Cifar10Dataset(dataset_path)
    cifar10.load_train_data()
    print("Train data load success,train set shape:{}".format(cifar10.train_x.shape))
    cifar10.load_test_data()
    print("Test data load success,test set shape:{}".format(cifar10.test_x.shape))
    cifar10.load_prune_data()
    print("Prune data load success,prune set shape:{}".format(cifar10.prune_x.shape))

    model = None
    if model_name == "VGG16SEBlock":
        model = VGG16SEBlock(l2_lambda)
        ues_regularizer = True
    elif model_name == "VGG16":
        model = VGG16(l2_lambda)
        ues_regularizer = True
    elif model_name == "ResNet20":
        model = ResNet20(l2_lambda,l1_lambda)
        ues_regularizer = True
    elif model_name == "ResNet20SEBlock":
        model = ResNet20SEBlock(l2_lambda)
        ues_regularizer = True
    model.build_model()
    print("Model build success!")
    train(batch_size, epoch_num, cifar10, learning_rate, testset_size, checkpoint_dir, model, ues_regularizer)

if __name__ == '__main__':
  tf.app.run()