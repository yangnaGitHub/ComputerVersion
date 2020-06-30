#!/usr/bin/env python2
#-*- coding: utf-8 -*-
'''
Created on Wed Jul 17 14:23:23 2019

@author: yangna
'''

#tensorflow distribute train by asynchronously update 

import tensorflow as tf
import numpy as np

tf.app.flags.DEFINE_string('train_dir', './models', 'Directory where to write event logs and checkpoint.')
#一个ps节点
tf.app.flags.DEFINE_string('ps_hosts', '192.168.41.162:2222', 'Comma-separated list of hostname:port pairs')
#两个worker节点
tf.app.flags.DEFINE_string('worker_hosts', '192.168.41.25:2222,192.168.41.221:2222', 'Comma-separated list of hostname:port pairs')
#节点的名字
tf.app.flags.DEFINE_string('job_name', '', 'one of ps or worker')
#任务的id
tf.app.flags.DEFINE_integer('task_index', 0, '0, 1, 2...')

FLAGS = tf.app.flags.FLAGS

def train():
    ps_hosts = FLAGS.ps_hosts.split(',')
    worker_hosts = FLAGS.worker_hosts.split(',')

    #Create a cluster from the parameter server and worker server
    #创建集群
    cluster = tf.train.ClusterSpec({'ps':ps_hosts, 'worker':worker_hosts})
    #Create and start a server for the local task
    #每个任务都要创建本地的服务器
    server = tf.train.Server(cluster, job_name = FLAGS.job_name, task_index=FLAGS.task_index)
    #如果是参数服务器,则直接阻塞,等待计算服务器下达参数初始化,参数更新命令就可以了
    #不过"下达命令"这个是TF内部实现的,没有显式实现
    if FLAGS.job_name == 'ps':
        server.join() 
    elif FLAGS.job_name == 'worker':
        #Assigns ops to the local worker by default
        #每个worker设备要做的事情
        with tf.device(tf.train.replica_device_setter(worker_device='/job:worker/task:%d' % FLAGS.task_index, cluster=cluster)):
            #prepare data
            #准备数据
            train_X = np.linspace(-1.0, 1.0, 100)
            train_Y = 2.0 * train_X + np.random.randn(*train_X.shape) * 0.33 + 10.0
            #construct networks
            #构建网络
            X = tf.placeholder('float')
            Y = tf.placeholder('float')
            w = tf.Variable(0.0, name='weight')
            b = tf.Variable(0.0, name='bias')
            #define loss
            #定义loss和optimizer
            loss = tf.square(Y - tf.multiply(X, w) - b)
            global_step = tf.Variable(0)
            train_op = tf.train.AdagradOptimizer(0.01).minimize(loss, global_step=global_step)

            saver = tf.train.Saver()
            
            summary_op = tf.summary.merge_all()
            init_op = tf.global_variables_initializer()

            #Create a 'supervisor', which oversees the training process.
            sv = tf.train.Supervisor(is_chief=(FLAGS.task_index==0),
                                     logdir=FLAGS.train_dir,
                                     init_op=init_op,
                                     summary_op=summary_op,
                                     saver=saver,
                                     global_step=global_step,
                                     save_model_secs=100)

            #The supervisor takes care of session initialization, retoring from a
            #checkpoint, and closing when done or an error occurs.
            with sv.managed_session(server.target) as sess:
                step = 0
                while step < 1000000:#epoch
                    #Run a training step asynchronously
                    for (x, y) in zip(train_X, train_Y):
                        _, step =sess.run([train_op, global_step], feed_dict={X:x, Y:y})
                    loss_value = sess.run(loss, feed_dict={X:x, Y:y})
                    print('Step: {}, loss: {}'.format(step, loss_value))

            #Ask for all the services to stop
            sv.stop()

def main(argv=None):
    #FLAGS.train_dir = os.path.join(os.getcwd(), FLAGS.train_dir)
    if not tf.gfile.Exists(FLAGS.train_dir):
        tf.gfile.MakeDirs(FLAGS.train_dir)
    #else:
        #tf.gfile.DeleteRecursively(FLAGS.train_dir)
    train()

if __name__=='__main__':
    tf.app.run()
