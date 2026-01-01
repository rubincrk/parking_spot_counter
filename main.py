import cv2
from utils import get_parking_spots_bboxes, empty_or_not
import numpy as np
from datetime import datetime


def calc_diff(im1, im2):
    return np.abs(np.mean(im1) - np.mean(im2))


mask = "data/mask_1920_1080.png"

video_path = "data/parking_1920_1080.mp4"

mask = cv2.imread(mask, 0)
connected_components = cv2.connectedComponentsWithStats(mask, cv2.CV_32S)

spots = get_parking_spots_bboxes(connected_components)

cap = cv2.VideoCapture(video_path)
window_name = 'frame'
spots_status = [None for j in spots]
frame_num = 0
window_closed = False  # Flag to track if the window was closed manually
step = 30
diffs = [None for j in spots]
prev_frame = None


while cap.isOpened():
    ret, frame = cap.read()
    
    if frame_num % step == 0 and prev_frame is not None:
        for spot_index, spot in enumerate(spots):
            x1, y1, w, h = spot
            spot_crop = frame[y1:y1+h, x1:x1+w, :] 
            
            diffs[spot_index] = calc_diff(spot_crop, prev_frame[y1:y1+h, x1:x1+w, :])
    
    #Once every 30 frames
    if frame_num % step == 0:
        if prev_frame is None:
            arr_ = range(len(spots))
        else:
            arr_ = [j for j in np.argsort(diffs) if diffs[j] / np.amax(diffs) > 0.4]
        
        for spot_index in arr_:
            spot = spots[spot_index]
            x1, y1, w, h = spot
            spot_crop = frame[y1:y1+h, x1:x1+w, :] 
        
            spot_status = empty_or_not(spot_crop)
            spots_status[spot_index] = spot_status
            
    if frame_num % step == 0:
        prev_frame = frame.copy()
        
        
    for spot_index, spot in enumerate(spots):
        spot_status = spots_status[spot_index]
        x1, y1, w, h = spots[spot_index]
        
            
        if spot_status:
            frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1+h ), (0,255,0), 2)
        else:
            frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1+h ), (0,0,255), 2)
    
    cv2.rectangle(frame, (80,20), (550,80), (0,0,0), -1) 
    cv2.putText(frame, 'Available Spots: {} / {}'.format(str(sum(spots_status)), str(len(spots_status))), (100,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    available_count = sum(spots_status)
    occupied_count = len(spots_status) - available_count
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)    
    cv2.imshow(window_name, frame)
    
    if not ret:
        print("End of video or can't retrieve frame.")
        break

    # Check if 'q' is pressed or window is closed
    if cv2.waitKey(1) == ord('q'):
        print("Exiting on 'q' press.")
        break
    
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1: 
        print("Window was closed manually.")
        window_closed = True
        break
    
    frame_num += 1

# Release resources
cap.release()
cv2.destroyAllWindows()

if window_closed:
    print("Window closed properly and video capture terminated.")
