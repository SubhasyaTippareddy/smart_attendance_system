
from distutils.log import debug
from flask import Flask, render_template, Response, request
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread


global capture,rec_frame, grey, switch, neg, face, rec, out, name, roll_no
capture=0
grey=0
neg=0
face=0
switch=1
rec=0
name=''
roll_no=''
haar_file= cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#make shots directory to save pics
try:
    os.mkdir('./datasets')
except OSError as error:
    pass

#Load pretrained face detection model    
#net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')


camera = cv2.VideoCapture(0)

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)


# def detect_face(frame):
#     global net
#     (h, w) = frame.shape[:2]
#     blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
#         (300, 300), (104.0, 177.0, 123.0))   
#     net.setInput(blob)
#     detections = net.forward()
#     confidence = detections[0, 0, 0, 2]

#     if confidence < 0.5:            
#             return frame           

#     box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
#     (startX, startY, endX, endY) = box.astype("int")
#     try:
#         frame=frame[startY:endY, startX:endX]
#         (h, w) = frame.shape[:2]
#         r = 480 / float(h)
#         dim = ( int(w * r), 480)
#         frame=cv2.resize(frame,dim)
#     except Exception as e:
#         pass
#     return frame


def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame,roll_no,name
    while True:
        success, frame = camera.read() 
        if success:
            # if(face):                
            #     frame= detect_face(frame)
            # if(grey):
            #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # if(neg):
            #     frame=cv2.bitwise_not(frame)    
            if(capture):
                capture=0
                # now = datetime.datetime.now()
                # p = os.path.sep.join(['datasets', "shot_{}.png".format(str(now).replace(":",''))])
                #cv2.imwrite(p, frame)
                #frame= cv2.putText(cv2.flip(frame,1),"Capturing...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                count=1
                sub_data=roll_no
                path=os.path.join('datasets',sub_data)
                if not os.path.isdir(path):
                    os.mkdir(path)
                (width, height)=(130,100)
                face_cascade = cv2.CascadeClassifier(haar_file)
                while count<101:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray,1.3,4)
                    for(x,y,w,h) in faces:
                        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0),2)
                        face=gray[y:y+h,x:x+w]
                        face_resize = cv2.resize(face, (width, height))
                        cv2.imwrite('%s/%s.png' % (path, count), face_resize)
                        count+=1
                        cv2.imshow('OpenCV', frame)
                        key=cv2.waitKey(10)
                        if key==27:
                            break
                #frame= cv2.putText(cv2.flip(frame,1),"Done!", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                name=''
                roll_no=''        
            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Next':
            print(request.form)
            global capture, name, roll_no
            capture=1
            name=request.form.get('name')
            roll_no=request.form.get('roll_no')
        elif  request.form.get('grey') == 'Grey':
            global grey
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg
        elif  request.form.get('face') == 'Face Only':
            global face
            face=not face 
            if(face):
                time.sleep(4)   
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                #camera = cv2.VideoCapture(0)
                switch=1
        # elif  request.form.get('rec') == 'Start/Stop Recording':
        #     global rec, out
        #     rec= not rec
        #     if(rec):
        #         now=datetime.datetime.now() 
        #         fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #         out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
        #         #Start new thread for recording the video
        #         thread = Thread(target = record, args=[out,])
        #         thread.start()
        #     elif(rec==False):
        #         out.release()
                          
                 
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)