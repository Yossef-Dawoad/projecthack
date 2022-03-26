import json
from channels.generic.websocket import AsyncWebsocketConsumer
import numpy as np
import cv2
import mediapipe as mp #########? install
# import utils
import numpy as np
from pathlib import Path
import time


class TimeTracker:
    def __init__(self) -> None:
        self.primetime = time.time()
        self.ptime2 = time.time() ### track the seconds passes
    
    def current_time(self):
        return time.time()

    def fps_calculate(self):
        fps = 1 / (self.current_time() - self.primetime)
        self.primetime = self.current_time()
        return fps
    
    def format_time(self, format: str="%y_%m_%d_%H_%M_%S"):
        return time.strftime(format, time.localtime(self.current_time()))

    def time_pass(self, time_pass_ms):
        if (self.current_time() - self.ptime2)*1000.0 > time_pass_ms:
            self.ptime2 = self.current_time()
            return True


def decodeframes(imgbytes):
    '''function that convert binary image(bytes) to usable image frame'''
    arr = np.frombuffer(imgbytes, dtype=np.int8) # convert bytes into array of int8
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR) # incode the image back to normal
    return img

class VideoHandlerConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ######################### setup recoding folder
        Path('./project/static/recordings').mkdir(parents=True, exist_ok=True)
        self.recPath = Path('././project/static/recordings').absolute()

        ##################### classes initilizations
        self.fastfacedetect = mp.solutions.face_detection
        self.tt = TimeTracker()
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID') ##### video encoding setup,   *'mp4v' -> mp4

        ####################### video recording flags
        self.RECORDING_EN = False
        self.STOPED_DETECTION_FLAG = False
        self.STOP_TOLERANCE_IN_SECONDS = 5
        ####################### Camera configrations
        self.WIDTH = 640
        self.HEIGHT = 480
        self.ColorConversion = cv2.cvtColor
        self.adjust_result = self.handel_net_result
        self.mp_drawing = mp.solutions.drawing_utils
    
    def handel_net_result(self, dim):
        xmin, ymin, width, height = dim.xmin , dim.ymin, dim.width, dim.height
        width = width * self.WIDTH
        height = height * self.HEIGHT
        xmin = xmin * (128 + self.WIDTH) - (width/2)
        ymin = ymin * (128 + self.HEIGHT) - (height/2)
        return  int(xmin), int(ymin) , int(width), int(height)
    ############################################################## 
    async def connect(self):
        self.roomName = "video_pool"
        await self.channel_layer.group_add( #create video_pool group
            self.roomName,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomName,
            self.channel_name
        )
        ############################ when session terminated by the user 
        self.videooutput.release()
        print('[RECODEING OR CAMERA STOPED] camera terminated by the user.')

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.roomName,{
                'type':'videoStream',
                'data':bytes_data}
        )

    async def videoStream(self, event):
        image_bytes = event['data']
        # image =  decodeframes(event['data'])

        # ################################## main program
        # with self.fastfacedetect.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        #     FaceDetect = face_detection.process
        # #     # image as not writeable to pass by reference. //performance-ish Tip
        # #     image.flags.writeable = False

        #     results = FaceDetect(image)
        #     if results.detections:
        #         for detection in results.detections:
        #             # print('Nose tip:')
        #             # print(self.fastfacedetect.get_key_point(
        #             #     detection, self.fastfacedetect.FaceKeyPoint.NOSE_TIP))
        #             self.mp_drawing.draw_detection(image, detection)
        #     image_bytes = cv2.imencode('.jpg', image)[1].tobytes()

        #         ############################# Video Recorder Handler
        #         if not self.RECORDING_EN:
        #             self.RECORDING_EN =True
        #             self.videooutput = cv2.VideoWriter(str(self.recPath.joinpath(f"{self.tt.format_time()}.avi")),
        #                                                                 self.fourcc, 30.0, (self.WIDTH, self.HEIGHT))
        #             print('[RECODEING STARTED] face detected recording started....')
        #         else:
        #             self.STOPED_DETECTION_FLAG = False
        #         ###################################################
        #         faces_detected = ((res.score[0], res.location_data.relative_bounding_box) for res in results.detections)
        #         for score, faceRoI in faces_detected:
        #             xmin, ymin, width, height = self.adjust_result(faceRoI)
        #             faceRoI = image[ymin-50:ymin+height, xmin:xmin+width+50] ###### get the face bounding box  coordinates

        #     ############################ continue Video Recorder Handler
        #     else: ##### No Detection
        #         if not self.STOPED_DETECTION_FLAG and self.RECORDING_EN:
        #             self.STOPED_DETECTION_FLAG = True
        #             self.TIMER_START = self.tt.current_time()
        #         elif self.STOPED_DETECTION_FLAG:
        #             if self.tt.current_time() - self.TIMER_START >= self.STOP_TOLERANCE_IN_SECONDS:
        #                 self.RECORDING_EN =False
        #                 self.STOPED_DETECTION_FLAG = False
        #                 self.videooutput.release() #### stop recording that file
        #                 print('[RECODEING STOPED] the video has been written to the disk.')

        #     ####################################################
        #     if self.RECORDING_EN: self.videooutput.write(image)
        #     fps = self.tt.fps_calculate(); print(fps, end="\r") ####### display the fps 
        await self.send(bytes_data=image_bytes)