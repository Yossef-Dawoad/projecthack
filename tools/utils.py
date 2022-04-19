import itertools
import numpy as np
import cv2
import time
import os


# def printe() -> None:
#     print(os.getcwd())


def decode_byte_frame(framebytes: bytes) -> np.ndarray:
    '''function that convert binary image(bytes) to numpy array'''
    arr =  np.frombuffer(framebytes, dtype=np.int8) # convert bytes into array of int8
    imgarr =  cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return imgarr


class TimeTracker:
    def __init__(self) -> None:
        self.startProgram = time.time()
        self.primetime = time.time()
        self.ptime2 = time.time()
        self.ptime3 = time.time()
    
    def current_time(self) -> float:
        return time.time()

    def fps_calculate(self) -> float:
        fps = 1 / (self.current_time() - self.primetime)
        self.primetime = self.current_time()
        return fps
    
    def format_time(self, format: str="%y_%m_%d_%H_%M_%S") -> str:
        return time.strftime(format, time.localtime(self.current_time()))

    def time_pass(self, time_pass_ms) -> bool:
        if (self.current_time() - self.ptime2)*1000.0 > time_pass_ms:
            self.ptime2 = self.current_time()
            return True

    def time_pass_s(self, time_pass: int) -> bool:
        if (self.current_time() - self.ptime3) > time_pass:
            self.ptime3 = self.current_time()
            return True



######################################### Deep Learning 
from pathlib import Path




class FaceDetector:
    def __init__(self, cuda=None):
        modelweights = "./dlmodels/res10_300x300_ssd_iter_140000_fp16.caffemodel" # model paramters
        modelconfig= './dlmodels/res10_structure_paramters.prototxt' # model layers configs
        self.facenetModel = cv2.dnn.readNet(modelweights,
                                            modelconfig,
                                            framework='Caffe')
        self.detectedfaces = []
        self.AppendFace = self.detectedfaces.append

    
    def detect(self, frame, threshold=0.6, Width=640, Height=480):
        self.detectedfaces.clear()
        imBlob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)), 1.0,
            size=(300,300),
            mean=(104.0, 177.0, 123.0))
        self.facenetModel.setInput(imBlob)
        return self.facenetModel.forward()





def peektoGenerator(iterable):
    try: firstobj = next(iterable)
    except StopIteration:
        return None
    return firstobj, itertools.chain([firstobj], iterable) ##### chain list of iterable
#################################################################################
class MotionDetection:
    def __init__(self, history=100, mthreshold=40, drawOnImage=None) -> None:
        self.backgroundSuptractor = self.motiondetector = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=mthreshold)
        self.mincntArea = 3000
        self.drawOnImage = drawOnImage
        self.fontStyle = cv2.FONT_HERSHEY_SIMPLEX
        self.color =  (0,0,255)

    def detect(self, frame):
        mask = self.motiondetector.apply(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = (c for c in contours if cv2.contourArea(c) > self.mincntArea)      
        
        cntsIterObj = peektoGenerator(contours)
        if cntsIterObj is not None:
            if self.drawOnImage:    
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    text = "Status: Movement"            
                    cv2.putText(frame, text,(10, 20), self.fontStyle, 1, self.color, 2)
            return True
        else:
            return False