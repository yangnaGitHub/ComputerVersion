#include <iostream>
#include <opencv/cv.hpp>
using namespace std;
using namespace cv;

int main()
{
    Mat img = imread("1.PNG");
    imshow("first windows", img);
    waitKey(0);
    cout << "done" << endl;
    return 0;
}
