from threading import Thread
import numpy as np 
import cv2, glob, time
# from cv2.dnn import blobFromImage

#TODO  Create Features Class (faceRECOGNITION, motionDETECTION, faceDETECTION) 


# class TimeTracker:
#     def __init__(self):
#         self.pTime = time.time()

#     @property
#     def cTime(self):
#         return time.time()

#     def pass_ms(self,ms=1):
        
#         if self.cTime - self.pTime >= ms/1000:
#             self.pTime = self.cTime
#             return True

#     def calcFps(self):
#         # currentime = time.time()
#         fps = 1/ (self.cTime - self.pTime)
#         self.pTime = self.cTime
#         return fps

#     def markTime(self, format="%y-%m-%d %H:%M"):   
#         return time.strftime(format, time.localtime(self.cTime))
        




##---------------------------------------------------------##

class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.camOpen, self.frame = self.stream.read()
        self.stopped = False
    
    def start(self):
        t = Thread(target=self.update, name='webcamStream',args=())
        t.daemon = False
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
                
            (self.camOpen, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True



##---------------------------------------------------------##
class face_detecotor:
    def __init__(self, cuda=False):
        modelparamters = "./models/res10_300x300_ssd_iter_140000_fp16.caffemodel" # model paramters
        modelconfig= './models/res10_structure_paramters.prototxt' # model layers configs
        self.facenetModel = cv2.dnn.readNetFromCaffe(modelconfig,modelparamters) # load the pre-trained model
        self.detectedfaces = []
        self.AppendFace = self.detectedfaces.append

        if cuda:
            self.facenetModel.setPerferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.facenetModel.setPerferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    def detect(self, frame, threshold=0.6):
        self.detectedfaces.clear()
        (h, w) = frame.shape[0:2]

        imBlob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)), 1.0,
            size=(300,300),
            mean=(104.0, 177.0, 123.0))

        self.facenetModel.setInput(imBlob)
        preds_faces = self.facenetModel.forward()

        for i in range(preds_faces.shape[2]):
            preds_confdence = preds_faces[0,0,i,2]
            if preds_confdence >= threshold:
                boundingBox = preds_faces[0,0,i,3:7] * np.array([w,h,w,h])
                (x, y, boxwidth, boxheight) = boundingBox.astype('int')
                self.AppendFace([x,y,boxwidth,boxheight])
        return self.detectedfaces



##---------------------------------------------------------##
class Embedder:
    def __init__(self, cuda=False):
        openfacepath="./models/nn4.small2.v1.t7"
        self.embedder = cv2.dnn.readNetFromTorch(openfacepath)

        if cuda:
            self.embedder.setPerferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.embedder.setPerferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    
    def embed(self, face):
        imBlob = cv2.dnn.blobFromImage(face, 1.0/255,
            (96, 96), (0,0,0),swapRB=True, crop=False)
        self.embedder.setInput(imBlob)
        return self.embedder.forward()


class DINET:
    def __init__(self, modelpath, modelconfig=None, framework="Caffe", cuda=False):
        self.net = cv2.dnn.readNet(model=modelpath,config=modelconfig,
            framework=framework)
        if cuda:   
            self.net.setPerferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPerferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    def processInput(self, netInput):
        self.net.setInput(netInput)
        return self.net.forward()



def detectmotion(currentframe, prevframe, threshold=4000, draw=True):
    diff = cv2.absdiff(prevframe, currentframe)
    gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #! NOT TESTED
    # BigContours = map((lambda c : cv2.contourArea(c) > threshold), contours)
    # if not draw: return BigContours
    # for c in BigContours:
    #     x, y, w, h = cv2.boundingRect(c)
    #     cv2.rectangle(currentframe, (x, y), (x+w, y+h), (0, 0, 255), 2)

    if not draw: return contours
    for c in contours:
        if cv2.contourArea(c) < threshold: return
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(currentframe, (x, y), (x+w, y+h), (0, 0, 255), 2)





    









def attendance(time):
    pass



def loadImagsDir(rootpath="./faces_data/",valid_exts=["jpg"]):
    facesList = []
    for f in glob.iglob(rootpath + '*/*', recursive=True):
        fext = f.split('.')[-1]
        if fext not in valid_exts:
            continue
        img = cv2.imread(f)
        facesList.append(img)
    return np.array(facesList)


def load_images_generator(rootpath="./faces_data/"):
    "return the file path and the image array"
    for f in glob.iglob(rootpath + '*/*.jpg', recursive=True):
        img = cv2.imread(f)
        yield (f, img) 

















from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle

def train_recognizer(face, model):
    """ this function will train face recognition model embeds with ML SVM"""
    print("[INFO] Loading face Emedddings...")
    embedings_data = pickle.load("embedding.pkl", "rb").read() 
    print("[ENCODING] encoding the labels...")
    le = LabelEncoder()
    lbls = le.fit_transform(embedings_data["names"]) 




def ProcessandRecognize(face, openface, recognizer):
    processedImg = cv2.dnn.blobFromImage(face, 1.0/255, (96, 96), (0,0,0),swapRB=True, crop=False)
    openface.setInput(processedImg)
    embeds_vec = openface.forward()
    # ? perform classification to recognize the face
    # preds = recognizer.predict_proba(embeds_vec)[0] #! of the pickle file
    # p = np.argmax(preds)
    # proba = preds[p]
    # facename = le.classes_[p]
    # cv2.putText(frame, f"{facename}", (x, y-10), font, 1.0, color, strock)

#?  first train step
#* load the actual face recognition along with the label encoder
# recognizer = pickle.loads(open("recognizer.pickle","rb").read())
# le = pickle.loads(open("le.pickle", "rb").read())