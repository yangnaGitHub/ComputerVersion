import glob
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

from kmeans import kmeans, avg_iou

def load_dataset(path):
    dataset = []
    files = glob.iglob('{}/*xml'.format(path))
    for xml_file in files:
        tree = ET.parse(xml_file)
        height = float(tree.findtext('./size/height'))
        width = float(tree.findtext('./size/width'))
        for obj in tree.iter('object'):
            xmin = float(obj.findtext('bndbox/xmin')) / width
            ymin = float(obj.findtext('bndbox/ymin')) / height
            xmax = float(obj.findtext('bndbox/xmax')) / width
            ymax = float(obj.findtext('bndbox/ymax')) / height
            if (0 == xmax - xmin) or (0 == ymax - ymin):
                print(xml_file, obj.findtext('bndbox/xmin'), obj.findtext('bndbox/xmax'), obj.findtext('bndbox/ymin'), obj.findtext('bndbox/ymax'))
            dataset.append([xmax - xmin, ymax - ymin])
    return np.array(dataset)

def plot_data(out, data, CLUSTERS):
    for i in range(CLUSTERS):
        color = ['orange','green','blue','gray','yellow','purple','pink','black','brown']
        mark= ['o','s','^','*','d','+','x','p','|']
        lab = 'claster' + str(i+1)
        plt.scatter(data[index == i, 0], data[index == i, 1], s=10, c=color[i], marker=mark[i], label=lab)
    plt.legend()
    plt.grid()
    plt.show()

if __name__=='__main__':
    ANNOTATIONS_PATH = '/home/yangna/yangna/code/object_detection/darknet_origin/scripts/VOCdevkit/VOC2013/Annotations'
    CLUSTERS = 9
    IMG_SIZE = 608
    iteration = 10#iterate multiple times,take take the best 'avg_iou' result

    print('loading data...')
    data = load_dataset(ANNOTATIONS_PATH)
    print('calculating anchor clusters...')
    for index in range(iteration):
        out, iter_times = kmeans(data, k=CLUSTERS)
        print('\n\niter %d'%(index+1))
        print('kmeans iterate %d times'%iter_times)
        print('Accuracy avg_iou: {:.2f}%'.format(avg_iou(data, out) * 100))
        #print('Boxes w, h:\n {}-{}'.format(out[:, 0]*IMG_SIZE, out[:, 1]*IMG_SIZE))
        print('Boxes w, h:\n {}'.format(out*IMG_SIZE))
        ratios = np.around(out[:, 0] / out[:, 1], decimals=2).tolist()
        print('Ratios w/h:\n {}'.format(sorted(ratios)))
        #plot_data(out, data, CLUSTERS)