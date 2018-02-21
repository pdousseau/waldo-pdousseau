"""Script that verifies if one image is a cropped part of the other one."""
import sys
import cv2
from pathlib import Path
from collections import namedtuple
import imghdr

VALID_FORMATS = ['png', 'jpg', 'jpeg', 'bmp']
BestMatch = namedtuple('BestMatch', ['accuracy', 'top_left', 'template_dimension'])

# accuracy, the limit of confidence that one image is really crop of the other one
THRESHOLD = 0.8


def sort_images(img1, img2):
    """Method that tries to define which one of the pictures is the main image and which one is the template.

    It checks if it is possible to fit one image inside the other. In this case it doesn't consider that one of the
    images might be scaled, and because of this they wouldn't fit inside each other.

    :param img1: <str> the path for the first image
    :param img2: <str> the path for the second image
    :return: (<numpy.ndarray>, <numpy.ndarray>) return a tuple where the first element is the image and the second is
    the template. Return a tuple of None in case it is not possible to fit one image inside the other.
    """
    image1 = cv2.imread(img1)
    image2 = cv2.imread(img2)

    if image1.shape[0] <= image2.shape[0] and image1.shape[1] <= image2.shape[1]:
        return image2, image1
    elif image1.shape[0] > image2.shape[0] and image1.shape[1] > image2.shape[1]:
        return image1, image2

    return None, None


def subimage(img1, img2):
    """Method that tries to match the template inside the image.

    Currently it scales the image from 0.25% its size till 1.25% and returns the best match. Ideally it should use a
    bigger range to also match templates that are bigger or smaller than this interval.
    It should also consider that the template could be rotated or distorted (in perspective).
    Also to improve performance, it could generate a new image and template where only the edges are detected.

    :param img1: <str> the path for the first image
    :param img2: <str> the path for the second image
    :return: in case it is possible to find the template in the image, return the original image with the template
    highlighted. None otherwise.
    """
    method = cv2.TM_CCOEFF_NORMED  # statistical method used

    # define which one is the template and which one is the image
    image, template = sort_images(img1, img2)

    # in case it is not possible to fit one image inside the other
    if image is None and template is None:
        return None

    best_scale = BestMatch(0, 0.5, 0)

    image2 = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)

    h, w = image2.shape[:2]
    imageGray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # resize the template from 0.25% of its size then 1.25% its size
    for scale in range(25,130,5):

        template_scaled = cv2.resize(template, (0, 0), fx=scale/100, fy=scale/100)

        # convert to grayscale to search it faster
        templateGray = cv2.cvtColor(template_scaled, cv2.COLOR_BGR2GRAY)

        # if the template gets bigger than the image, break it
        if templateGray.shape[0] > h or templateGray.shape[1] > w:
            break

        # find template
        result = cv2.matchTemplate(imageGray, templateGray, method)

        # finds the min and max local value and their position
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # if it found a scale with a better accuracy, update the values found
        if max_val > best_scale.accuracy:
            best_scale = BestMatch(max_val, max_loc, templateGray.shape)  # get template dimension)

    # if the accuracy is below the threshold, it means that it was not possible to find a good match
    if best_scale.accuracy < THRESHOLD:
        return None

    top_left = best_scale.top_left   # top left position of the image that matches
    h, w = best_scale.template_dimension
    bottom_right = (top_left[0] + w, top_left[1] + h)  # calculate bottom right position
    cv2.rectangle(image2, top_left, bottom_right, (0, 0, 255), 4)  # draw a red rectangle around the image

    return image2

if __name__ == "__main__":

    if len(sys.argv) != 3 or not Path(sys.argv[1]).is_file() or not Path(sys.argv[2]).is_file():
        print('Please, insert the correct number of arguments: image1 and image2.')
        sys.exit()
    elif imghdr.what(sys.argv[1]) not in VALID_FORMATS or imghdr.what(sys.argv[2]) not in VALID_FORMATS:
        print('Both parameters must be an image.')
        sys.exit()

    image = subimage(sys.argv[1], sys.argv[2])

    # Show result
    if image is not None:
        cv2.imshow("Result", image)
        cv2.waitKey(10000)
