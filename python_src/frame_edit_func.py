import numpy as np
import cv2 as cv

def edge_dilated(img, num = 0):
    # num номер варианта обработки изображеняи

    if num == 0:
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
        lower_black = np.array([0, 0, 100])
        upper_black = np.array([255, 255, 255])
    
        mask = cv.bitwise_not(cv.inRange(hsv, lower_black, upper_black))
        blurred = cv.GaussianBlur(mask, (5, 5), 0)
        
        ret,thresh = cv.threshold(blurred,10,255,cv.THRESH_BINARY)
        kernel = np.ones((6,6), np.uint8)
        
        opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
    
        kernel1 = np.ones((3,3), np.uint8)
        
        morph_close = cv.morphologyEx(opening, cv.MORPH_CLOSE, kernel1)
        dilated = cv.dilate(morph_close, kernel, iterations=1)
        
        kernel2 = np.ones((3,3), np.uint8)
        morph_close = cv.morphologyEx(dilated, cv.MORPH_CLOSE, kernel2)

    
        return dilated
    elif num == 3:
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
        lower_black = np.array([0, 0, 100])
        upper_black = np.array([255, 255, 255])
    
        mask = cv.bitwise_not(cv.inRange(hsv, lower_black, upper_black))
        blurred = cv.GaussianBlur(mask, (5, 5), 0)
        
        ret,thresh = cv.threshold(blurred,10,255,cv.THRESH_BINARY)
        kernel = np.ones((10,10), np.uint8)
        kernel3 = np.ones((3,3), np.uint8)
        erosion = cv.erode(thresh, kernel3, iterations = 2)

        dilated = cv.dilate(erosion, kernel, iterations=1)
        kernel1 = np.ones((8,8), np.uint8)
    
        return dilated
    
    elif num == 1:
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
        lower_black = np.array([0, 0, 100])
        upper_black = np.array([255, 255, 255])
    
        mask = cv.bitwise_not(cv.inRange(hsv, lower_black, upper_black))
        blurred = cv.GaussianBlur(mask, (5, 5), 0)
            
        ret,thresh = cv.threshold(blurred,14,255,cv.THRESH_BINARY)
        
        kernel = np.ones((5,5), np.uint8)
        
        opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
    
        kernel1 = np.ones((8,8), np.uint8)
        
        morph_close = cv.morphologyEx(opening, cv.MORPH_CLOSE, kernel1)
        return morph_close
    
    elif num == 2:
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 100])
        upper_black = np.array([255, 255, 255])
        mask = cv.inRange(hsv, lower_black, upper_black)
    
        blurred = cv.GaussianBlur(mask, (5, 5), 0)
        th3 = cv.adaptiveThreshold(blurred,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv.THRESH_BINARY,11,2)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        cleaned = cv.morphologyEx(th3, cv.MORPH_CLOSE, kernel, iterations=2)
        cleaned = cv.morphologyEx(cleaned, cv.MORPH_OPEN, kernel, iterations=2)
        
        return cv.bitwise_not(cleaned)
    

def rotate_frame(frame, angle):
    frame_height, frame_width = frame.shape[:2] 
    center = (frame_width // 2, frame_height // 2)
    
    rotation_matrix = cv.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    new_width = int((frame_height * sin) + (frame_width * cos))
    new_height = int((frame_height * cos) + (frame_width * sin))
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
    rotated_frame = cv.warpAffine(frame, rotation_matrix, (new_width, new_height), borderValue=(255, 255, 255))
    
    return rotated_frame


def undistort_frame(frame):
    camera_matrix = np.array([[1.20467414e+03, 0.00000000e+00, 9.07854974e+02], 
                        [0.00000000e+00, 1.20123843e+03, 5.52728845e+02], 
                        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coeffs = np.array([-0.41728863,  0.22615515, -0.00167113,  0.00549296, -0.03307888])
    h, w = frame.shape[:2]
    new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    mapx, mapy = cv.initUndistortRectifyMap(camera_matrix, dist_coeffs, None, new_camera_matrix, (w, h), 5)

    undistorted_frame = cv.remap(frame, mapx, mapy, cv.INTER_LINEAR)

    x, y, w, h = roi
    undistorted_frame = undistorted_frame[y:y+h, x:x+w]

    return undistorted_frame