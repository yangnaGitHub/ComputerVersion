import glob
import xml.etree.ElementTree as ET
# import matplotlib.pyplot as plt
import numpy as np

# from kmeans import kmeans, avg_iou

def iou(box, clusters):
    """
    Calculates the Intersection over Union (IoU) between a box and k clusters.
    :param box: tuple or array, shifted to the origin (i. e. width and height)
    :param clusters: numpy array of shape (k, 2) where k is the number of clusters
    :return: numpy array of shape (k, 0) where k is the number of clusters
    """
    x = np.minimum(clusters[:, 0], box[0])
    y = np.minimum(clusters[:, 1], box[1])
    if np.count_nonzero(x == 0) > 0 or np.count_nonzero(y == 0) > 0:
        raise ValueError("Box has no area")

    intersection = x * y
    box_area = box[0] * box[1]
    cluster_area = clusters[:, 0] * clusters[:, 1]

    iou_ = intersection / (box_area + cluster_area - intersection)

    return iou_


def avg_iou(boxes, clusters):
    """
    Calculates the average Intersection over Union (IoU) between a numpy array of boxes and k clusters.
    :param boxes: numpy array of shape (r, 2), where r is the number of rows
    :param clusters: numpy array of shape (k, 2) where k is the number of clusters
    :return: average IoU as a single float
    """
    return np.mean([np.max(iou(boxes[i], clusters)) for i in range(boxes.shape[0])])


def translate_boxes(boxes):
    """
    Translates all the boxes to the origin.
    :param boxes: numpy array of shape (r, 4)
    :return: numpy array of shape (r, 2)
    """
    new_boxes = boxes.copy()
    for row in range(new_boxes.shape[0]):
        new_boxes[row][2] = np.abs(new_boxes[row][2] - new_boxes[row][0])
        new_boxes[row][3] = np.abs(new_boxes[row][3] - new_boxes[row][1])
    return np.delete(new_boxes, [0, 1], axis=1)


def kmeans(boxes, k, dist=np.median):
    """
    Calculates k-means clustering with the Intersection over Union (IoU) metric.
    :param boxes: numpy array of shape (r, 2), where r is the number of rows
    :param k: number of clusters
    :param dist: distance function
    :return: numpy array of shape (k, 2)
    """
    rows = boxes.shape[0]

    distances = np.empty((rows, k))
    last_clusters = np.zeros((rows,))

    np.random.seed()

    # the Forgy method will fail if the whole array contains the same rows
    clusters = boxes[np.random.choice(rows, k, replace=False)]
    i = 1
    while True:
        for row in range(rows):
            distances[row] = 1 - iou(boxes[row], clusters)

        nearest_clusters = np.argmin(distances, axis=1)

        if (last_clusters == nearest_clusters).all():
            break
        # stop condition: cluster no change any more
        for cluster in range(k):
            clusters[cluster] = dist(boxes[nearest_clusters == cluster], axis=0)

        last_clusters = nearest_clusters
        i += 1

    return clusters, i

def load_dataset(path):
	dataset = []
	for xml_file in glob.glob("{}/*xml".format(path)):
		tree = ET.parse(xml_file)

		height = int(tree.findtext("./size/height"))
		width = int(tree.findtext("./size/width"))

		for obj in tree.iter("object"):
			xmin = int(float(obj.findtext("bndbox/xmin"))) / width
			ymin = int(float(obj.findtext("bndbox/ymin"))) / height
			xmax = int(obj.findtext("bndbox/xmax")) / width
			ymax = int(float(obj.findtext("bndbox/ymax"))) / height

			dataset.append([xmax - xmin, ymax - ymin])

	return np.array(dataset)


def plot_data(out, data, CLUSTERS):
    for i in range(CLUSTERS):
        color = ['orange','green','blue','gray','yellow','purple','pink','black','brown']
        mark= ['o','s','^','*','d','+','x','p','|']
        lab = 'claster' + str(i+1)
        plt.scatter(data[index == i, 0], data[index == i, 1], s=10, c=color[i], marker=mark[i], label=lab)
       # draw the centers
    plt.scatter(out[:, 0], out[:, 1], s=250, marker="*", c="red", label="cluster center")
    plt.legend()
    plt.grid()
    plt.show()

if __name__=="__main__":
	ANNOTATIONS_PATH = "/home/noah/Documents/datasets/Vehicles(coco_voc)/train/Annotations"
	# ANNOTATIONS_PATH = "/home/noah/Documents/datasets/Person(coco_voc)/train/Annotations"
	CLUSTERS = 9
	IMG_SIZE = 416
	iteration = 5 #iterate multiple times，take take the best 'avg_iou' result

	print("loading data...")
	data = load_dataset(ANNOTATIONS_PATH)
	print("calculating anchor clusters...")
	for i in range(iteration):
		out, iter_times= kmeans(data, k=CLUSTERS)
		print("\n\niter %d"%(i+1))
		print("kmeans iterate %d times"%iter_times)
		print("Accuracy avg_iou: {:.2f}%".format(avg_iou(data, out) * 100))
		# print("Boxes w, h:\n {}-{}".format(out[:, 0]*IMG_SIZE, out[:, 1]*IMG_SIZE))
		print("Boxes w, h:\n {}".format(out*IMG_SIZE))

		ratios = np.around(out[:, 0] / out[:, 1], decimals=2).tolist()
		print("Ratios w/h:\n {}".format(sorted(ratios)))
		# plot_data(out, data, CLUSTERS)
