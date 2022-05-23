from flask import Flask, flash, redirect, render_template, Response, request, url_for
import cv2
import datetime, time, sqlite3
import os, sys
import numpy as np


# conn = sqlite3.connect('database.db')
# print("Opened database successfully")
# conn.execute('CREATE TABLE students_details (name TEXT, roll_no TEXT)')
# conn.close()

global switch, rec, out,attendance
switch=1
rec=0
attendance=1
haar_file= cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#make shots directory to save pics
try:
    os.mkdir('./datasets')
except OSError as error:
    pass

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')
app.secret_key="sas"

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

@app.route('/')
def start():
    return render_template('login.html')
       
@app.route('/',methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password= request.form['password']
        print(username, password)
        if username=='ngit' and password=='password':
            return redirect(url_for('index'))
        else:
            flash('Login failed! Please try again')
            return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')        

@app.route('/add_student')
def add_student():
    return render_template('create__student_db.html')

@app.route('/attendance')
def mark_attendance():
    return render_template('attendance.html')

@app.route('/video_feed')
def video_feed():
    print('1')
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')    

@app.route('/add_student',methods=['POST','GET'])
def add_student_details():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Next':
            print(request.form)
            name=request.form.get('name')
            roll_no=request.form.get('roll_no')
            if(name=='' or roll_no==''): 
                flash('Invalid details! Please Enter again')
                return render_template('create__student_db.html')
            addStudentUtil(name,roll_no)

def addStudentUtil(name,roll_no):
        camera = cv2.VideoCapture(0)
        while True: 
            success, frame = camera.read() 
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
                    # cv2.imshow('OpenCV', frame)
                    key=cv2.waitKey(10)
                    if key==27:
                        break
            name=''
            roll_no=''      
            print('4')
            flash('Student Details added to database')
            return render_template('index.html')       
             

def addStudentToDatabase(name,roll_no):
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO students (name,roll_no) VALUES (?,?)",(name,roll_no))
            con.commit()
            msg = "Record successfully added"
    except:
         con.rollback()
         msg = "error in insert operation"
      
    finally:
         return render_template(".html",msg = msg)
         con.close()

       
    
if __name__ == '__main__':
    app.run(debug=True)

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
    print('2')
    camera = cv2.VideoCapture(0)
    global out, capture,roll_no,name,attendance
    while True: 
            if(capture):
                print('3')
                success, frame = camera.read() 
                video_feed()
                capture=0
                # now = datetime.datetime.now()
                # p = os.path.sep.join(['datasets', "shot_{}.png".format(str(now).replace(":",''))])
                #cv2.imwrite(p, frame)
                #frame= cv2.putText(cv2.flip(frame,1),"Capturing...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                print('4')
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
                        # cv2.imshow('OpenCV', frame)
                        key=cv2.waitKey(10)
                        if key==27:
                            break
                #frame= cv2.putText(cv2.flip(frame,1),"Done!", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                name=''
                roll_no=''        
                
 