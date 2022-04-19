import json
from channels.generic.websocket import AsyncWebsocketConsumer
import numpy as np
import  tools.utils as utils


class VideoHandlerConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tt = utils.TimeTracker()
        self.facedetector = utils.FaceDetector()
        self.motiondetecotor =utils.MotionDetection(drawOnImage=True)
       




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



    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.roomName,{
                'type':'videoStream',
                'data':bytes_data}
        )

    async def videoStream(self, event):
        image_bytes = event['data']

        imagearr = utils.decode_byte_frame(image_bytes)
        self.process(imagearr)
        
        # ## concatenate the fps data to the image 
        # fps = f'{self.tt.fps_calculate():.0f}'
        # image_bytes += str.encode(fps)

        await self.send(bytes_data=image_bytes)

    
    async def process(self, image):
        Width = 640
        Height = 480
        motiondetected = self.motiondetection(image)
        ################################### face detections
        detectedfaces =  await self.facedetector.detect(image)
        for i in range(detectedfaces.shape[2]):
            preds_confdence = detectedfaces[0,0,i,2]
            if preds_confdence >= 0.6:
                boundingBox = detectedfaces[0,0,i,3:7] * np.array([Width,Height,Width,Height])
                (x, y, boxwidth, boxheight) = boundingBox.astype('int')
                faceroi = image[y:boxheight, x:boxwidth]
                
        if motiondetected:
            print("motiondetected")

    async def motiondetection(self, image):
        motiondetected = await self.motiondetecotor.detect(image)
        return motiondetected
