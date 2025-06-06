import imutils
from skimage.filters import threshold_local
import numpy as np
import cv2

def order_points(pts):
	rect = np.zeros((4, 2), dtype = "float32")
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped


def compute_channel_stats(image_channel):
    hist = cv2.calcHist([image_channel], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()  # Нормализация гистограммы
    mean = np.sum(hist * np.arange(256))  # Среднее значение
    variance = np.sum(hist * (np.arange(256) - mean) ** 2)  # Дисперсия
    return mean, variance

def get_four_corners(hull):
        points = hull.reshape(-1, 2)
        n = points.shape[0]
        if n < 4:
            return None

        max_dist = 0
        A, B = None, None
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(points[i] - points[j])
                if dist > max_dist:
                    max_dist, A, B = dist, points[i], points[j]

        if A is None or B is None:
            return None

        line_vec = B - A
        left, right = [], []
        for pt in points:
            if np.array_equal(pt, A) or np.array_equal(pt, B):
                continue
            cross = np.cross(line_vec, pt - A)
            if cross > 0:
                left.append(pt)
            else:
                right.append(pt)

        def distance(p):
            return np.abs(np.cross(line_vec, p - A)) / np.linalg.norm(line_vec)

        C = max(left, key=distance, default=None)
        D = max(right, key=distance, default=None)

        four_points = []
        if C is not None and D is not None:
            four_points = [A, C, B, D]
        else:
            remaining = [p for p in points if not (np.array_equal(p, A) or np.array_equal(p, B))]
            if len(remaining) >= 2:
                four_points = [A, remaining[0], B, remaining[1]]
            else:
                return None

        sum_coords = np.sum(four_points, axis=1)
        ordered = [
            four_points[np.argmin(sum_coords)],
            four_points[np.argmax([pt[0] - pt[1] for pt in four_points])],
            four_points[np.argmax(sum_coords)],
            four_points[np.argmin([pt[0] - pt[1] for pt in four_points])]
        ]

        return np.array(ordered).reshape(-1, 1, 2).astype(np.int32)

def calculate_polygon_area(pts):
    """Вычисление площади многоугольника по его вершинам"""
    pts = pts.reshape(-1, 2)
    x = pts[:, 0]
    y = pts[:, 1]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def raw_photo_to_scan(mask, image):
    image_copy = image.copy()

    # Предобработка маски
    if len(mask.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Поиск контуров
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in cnts:
        # Аппроксимация контура до четырех точек
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # Если контур похож на прямоугольник
        if len(approx) >= 4:
            screenCnt = approx
            break

    if screenCnt is None:
        # Если не найдено — ищем через HoughLines
        edges = cv2.Canny(mask, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=100, maxLineGap=30)

        if lines is not None:
            intersections = find_line_intersections(lines)
            if len(intersections) >= 4:
                screenCnt = order_points(intersections[:4])

    if screenCnt is None:
        return "No contour"

    # Применение преобразования
    warped = four_point_transform(image, screenCnt.reshape(4, 2))

    return warped, cv2.drawContours(image_copy, [screenCnt], -1, (0, 255, 0), 4)


def find_line_intersections(lines):
    intersections = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            line1 = lines[i][0]
            line2 = lines[j][0]
            x1, y1, x2, y2 = line1
            x3, y3, x4, y4 = line2
            intersection = line_intersection((x1, y1, x2, y2), (x3, y3, x4, y4))
            if intersection is not None:
                intersections.append(intersection)
    return intersections


def line_intersection(line1, line2):
    # Функция для нахождения пересечения двух линий
    # Реализация через линейную алгебру
    xdiff = (line1[0] - line1[2], line2[0] - line2[2])
    ydiff = (line1[1] - line1[3], line2[1] - line2[3])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None  # Линии параллельны

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (int(x), int(y))

def raw_to_binarized(image):
    warped = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method='gaussian')
    best_warped = (warped > T).astype('uint8') * 255

    return best_warped
