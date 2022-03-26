import glob
import cv2



cascades = cv2.__file__ + '/data/haarcascade_frontalface_default.xml'
detector = cv2.CascadeClassifier(cascades)

for img in glob("*.jpg"):
    imarr = cv2.imread(img)
    gray_imarr = cv2.cvtColor(imarr, cv2.COLOR_BGR2RGB)
    faces = detector.detectMultiScale(
		gray_imarr, scaleFactor=1.05, minNeighbors=5,
		minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faces:
        roi = imarr[y:y+h, x:x+w]
        

