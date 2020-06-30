#!/usr/bin/env python2
#-*- coding: utf-8 -*-
'''
Created on Wed Jul 17 14:39:06 2019

@author: yangna
'''

#tensorflow distribute train by synchronously update 

import tensorflow as tf
import numpy as np

tf.app.flags.DEFINE_string('train_dir', './models', 'Directory where to write event logs and checkpoint.')
tf.app.flags.DEFINE_string('ps_hosts', '192.168.41.162:2222', 'Comma-separated list of hostname:port pairs')
#两个worker节点
tf.app.flags.DEFINE_string('worker_hosts', '192.168.41.25:2222,192.168.41.221:2222', 'Comma-separated list of hostname:port pairs')
tf.app.flags.DEFINE_string('job_name', '', 'one of ps or worker')
tf.app.flags.DEFINE_integer('task_index', 0, '0, 1, 2...')
FLAGS = tf.app.flags.FLAGS

def train():
    ps_hosts = FLAGS.ps_hosts.split(',')
    worker_hosts = FLAGS.worker_hosts.split(',')
    n_works = len(worker_hosts)
    #Create a cluster from the parameter server and worker server
    cluster = tf.train.ClusterSpec({'ps':ps_hosts, 'worker':worker_hosts})

    #Create and start a server for the local task
    server = tf.train.Server(cluster, job_name = FLAGS.job_name, task_index=FLAGS.task_index)

    if FLAGS.job_name == 'ps':
        server.join()
    elif FLAGS.job_name == 'worker':
        #Assigns ops to the local worker by default
        with tf.device(tf.train.replica_device_setter(worker_device='/job:worker/task:%d' % FLAGS.task_index, cluster=cluster)):
            train_X = np.linspace(-1.0, 1.0, 100)
            train_Y = 2.0 * train_X + np.random.randn(*train_X.shape) * 0.33 + 10.0
            X = tf.placeholder('float')
            Y = tf.placeholder('float')

            w = tf.Variable(0.0, name='weight')
            b = tf.Variable(0.0, name='bias')
            loss = tf.square(Y - tf.multiply(X, w) - b)

            global_step = tf.Variable(0)

            #for Syncmously updata
            #同步更新模式下,需要等待所有计算图计算出梯度,然后梯度求平均,tf.train.SyncReplicasOptimizer实现了这种封装
            opt = tf.train.SyncReplicasOptimizer(tf.train.AdagradOptimizer(0.01),
                                                 replicas_to_aggregate=n_works,
                                                 total_num_replicas=n_works)
            train_op = opt.minimize(loss, global_step=global_step)
            saver = tf.train.Saver()
            summary_op = tf.summary.merge_all()

            init_op = tf.global_variables_initializer()

            #for Syncmously updata
            #同步模式下,主计算服务器需要协调不同计算服务器计算得到的梯度,并更新参数。
            if FLAGS.task_index==0:
                #定义协调不同计算服务器的队列,并定义初始化操作
                chief_queue_runner = opt.get_chief_queue_runner()
                init_tokens_op = opt.get_init_tokens_op(0)

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

            #for Syncmously updata. 
            #prepare_or_wait_for_session used by sync. It will wait until main node ok and parameter init over!
            #for Syncmously updata. 
            #这里用的是prepare_or_wait_for_session。
            #相比于异步更新的managed_session:只要某个计算服务器参数初始化完毕就可以开始,
            #prepare_or_wait_for_session:等待所有计算服务器参数初始化完毕(参数只有一份,后续的计算服务器应该不需要初始化了?只需要和参数服务器建立一个关系),主节点协调工作完毕后,开始
            with sv.prepare_or_wait_for_session(server.target) as sess:
                #for Syncmously updata
                if FLAGS.task_index==0:
                    #开始训练之前,主计算服务器需要启动协调同步更新的队列,并执行初始化操作
                    sv.start_queue_runners(sess, [chief_queue_runner])
                    sess.run(init_tokens_op)

                step = 0
                while step < 100000:
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
