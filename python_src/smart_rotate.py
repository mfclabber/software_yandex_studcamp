import cv2
import numpy as np
import time
from test_move import RobotDirection
from control.follow2object import PIDController


def detect_perspective_x(image,ret):
    h = image.shape[0]
    w = image.shape[1]

    image = image[:][round(h*0.3):h]
    image = cv2.resize(image,None,fx=1,fy=1.7)
    h1 = image.shape[0]
    
    HORIZONT = -0.3*h*1.7/2

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    cv2.circle(gray,(round(w*0.5)-20,h1+10),200,0,-1)
    thr = cv2.inRange(gray,100,255)
    thr = cv2.medianBlur(thr,3)
    thr = cv2.inRange(gray,120,255)

    edges = cv2.Canny(thr,50,150,apertureSize=3)

    lines_list =[]
    lines = cv2.HoughLinesP(
                edges, # Input edge image
                1, # Distance resolution in pixels
                np.pi/180, # Angle resolution in radians
                threshold= 80, # Min number of votes for valid line
                minLineLength=50, # Min allowed length of line
                maxLineGap=50 # Max allowed gap between line for joining them
                )

    # Iterate over points
    x_persp_arr = []

    to_draw = []

    if lines is not None:
      for points in lines:
            # Extracted points nested in the list
          x1,y1,x2,y2=points[0]
          # Draw the lines joing the points
          # On the original image
          if abs(x2-x1)>0.1*w:
            a = (y2-y1)/(x2-x1)
            if abs(a)>0.5:
                b = y1-a*x1
                x_persp = (b-HORIZONT)/(-a)
                x_persp_arr.append(x_persp)
              

                ### draw line to horizont
                cv2.line(image,(x1,y1),(x2,y2),(255,0,0),4)
                if (x_persp>0) and (x_persp<w):
                    cv2.line(image,(round(x_persp),h1),(round(x_persp),round(h1*0.7)),(0,255,0),4)

                # Maintain a simples lookup list for points

                lines_list.append([(x1,y1),(x2,y2)])
                [x,y] = [x1,y1] if y1>y2 else [x2,y2]
                if (x_persp>-w) and (x_persp<w*2):
                   to_draw.append((x,y,round(x_persp),round(HORIZONT),True))
                else:
                   to_draw.append((x,y,-w,round(b),False))
    
    x_mean = sum(x_persp_arr)/(len(x_persp_arr)+0.00001)

    image_wide = np.concatenate( (np.zeros_like(image), image, np.zeros_like(image)), 1 )
    image_wide = np.concatenate( (np.zeros_like(image_wide),image_wide.copy()), 0 )

    cv2.line(image_wide,(0,round(HORIZONT+h1)),(w*3,round(HORIZONT+h1)),(0,255,0))

    for i in to_draw:
        if i[4]:
          cv2.circle(image_wide,(i[2]+w,i[3]+h1),10,(255,0,0),-1)
        cv2.line(image_wide,(i[0]+w,i[1]+h1),(i[2]+w,i[3]+h1),(255,0,0))
    

    ### draw line to horizont
    if (x_mean>-w) and (x_mean<2*w) and x_mean!=0:
      cv2.circle(image_wide,(round(x_mean)+w, round(HORIZONT)+h1),20,(0,0,255),-1)
      cv2.line(image_wide,(round(x_mean)+w,2*h1),(round(x_mean)+w, round(HORIZONT)+h1),(0,0,255),5)
    image_wide = cv2.resize(image_wide,(640*2,460*2))
    image_wide = cv2.putText(image_wide,str(round(x_mean)),(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),thickness=5)
    ret.write(image_wide)
    return x_mean

def finish_rotate(go,cap):
    pid = PIDController(0.25,0.2,0,320)
    lim = 30
    result = cv2.VideoWriter('it worked1.avi',
                         cv2.VideoWriter_fourcc(*'XVID'), 
                         10, (640*2,460*2),True)

    # try:
    for i in range(50):
        ret, frame = cap.read()

        if (ret) and i%10 == 0:
            lim = 60
            res = detect_perspective_x(frame,result)
            if res:
                angle = pid.update(res)
                angle = max(min(angle,lim),-lim)
                if abs(angle)>15:
                    go.forward_with_angle(0,angle)
                print(f"angle:{angle}    res:{res-320}")
                time.sleep(0.3)
                go.stop()
            else:
               print('no wall found')
        elif i%10 == 0:
           print('no video for ya')
        
        #else:
        #    cap.release()
        #    result.release()
        #    print('no video')
        #    break
    result.release()

# go = RobotDirection()
# cap = cv2.VideoCapture(0)
# finish_rotate(go,cap)
# cap.release()