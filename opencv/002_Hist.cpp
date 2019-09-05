#include <iostream>
#include <opencv/cv.h>

using namespace std;
using namespace cv;

int main(){
	Mat Picture = imread("002_1.jpg", cv::IMREAD_GRAYSCALE);
	imshow("Picture", Picture);

	int imagecount = 1;
	int channels[1] = {0};
	Mat outputHist;
	int dims = 1;
	int histSize[1] = {256};
	float hranges[2] = {0, 255};
	const float* ranges[1] = {hranges};
	bool uni = true;
	bool accum = false;
	calcHist(&Picture, imagecount, channels, Mat(), outputHist, dims, histSize, ranges, uni, accum);
	for(int index = 0; index < 256; index++)
		cout << "bin/value" << index << "=" << outputHist.at<float>(index) << endl;

	int scale = 1;
	Mat histPic(histSize[0] * scale, histSize[0], CV_8U, Scalar(255));
	double maxValue = 0, minValue = 0;
	minMaxloc(outputHist, &minValue, &maxValue, NULL, NULL);
	cout << minValue << " + " << maxValue << endl;

	double rate = (histSize[0] / maxValue) * 0.9;
	for(int index = 0; index < histSize[0]; index++){
		float value = outputHist.at<float>(index);
		line(histPic, Point(index*scale, histSize[0]), Point(i*scale, histSize[0] - value*rate), Scalar(0));
	}
	imshow("OprateAfter", histPic);
	waitKey(0);
	return 0;
}