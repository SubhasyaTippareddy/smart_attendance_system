import csv
from flask import Flask, flash, redirect, render_template, Response, request, url_for,g
import cv2, openpyxl
import sqlite3
import os, sys
import numpy as np, pandas as pd
from datetime import date

haar_file= cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#make shots directory to save pics
try:
    os.mkdir('./datasets')
    os.mkdir('./attendance_sheets')
except OSError as error:
    pass

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')
app.secret_key="sas"

# conn = sqlite3.connect('database.db')
# print("Opened database successfully")
# conn.execute('CREATE TABLE students_details (name TEXT, roll_no TEXT)')
# conn.close()


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

datasets='datasets'
def getEmptyAttendanceSheet():
    attend_dictionary={'Names':[],'Roll_No':[], 'Attendance':[]}
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from students_details")
        records = cur.fetchall()
        names_list=[]
        roll_list=[]
        for record in records:
            names_list.append(record['name'])
            roll_list.append(record['roll_no'])
        attend_dictionary['Names']=names_list
        attend_dictionary['Roll_No']=roll_list
        attend_dictionary['Attendance']=["absent"]*len(names_list)
    except:
         con.rollback()    
    finally:
        con.close()
    return attend_dictionary

def file_edit(names,prediction):
    # wb=Workbook()
    # ws = wb.active
    # ws.title = "Attendance"
    # filepath = "attendance_sheets/Attendance_"+datetime.now()+".xlsx"
    attendance_sheet= getEmptyAttendanceSheet()
    a=(names[prediction[0]])
    print('after excelsheet active')
    for i in range(len(attendance_sheet['Names'])):
        print('in for loop')
        if a==(attendance_sheet['Roll_No'][i]):
            attendance_sheet['Attendance'][i]="present"
            break
    print('Names RollNo Attendance')
    for i in range(len(attendance_sheet['Names'])):
        print(attendance_sheet['Names'][i], attendance_sheet['Roll_No'][i],attendance_sheet['Attendance'][i])
    attendance_df=pd.DataFrame.from_dict(attendance_sheet)
    filepath = 'attendance_sheets/Attendance'+str(date.today())+'.csv'
    file = open(filepath, 'w')
    writer = csv.writer(file)
    attendance_df.to_csv(filepath, mode='a', index=False, header=False)
    # wb.save(filename=filepath)
    

def gen_frames_for_attendance(): 
            (images, labels, names, id) = ([],[],{},0)
            for(subdirs, dirs, files) in os.walk(datasets):
                for file in dirs:
                    names[id] = file
                    subjectpath = os.path.join(datasets, file)
                    print('File paths')
                    for filename in os.listdir(subjectpath):
                        path = subjectpath+'/'+filename
                        label = id
                        images.append(cv2.imread(path,0))
                        labels.append(int(label))
                    id+=1
            (width, height) = (130,100)
            labels=np.array(labels)
            model = cv2.face.LBPHFaceRecognizer_create()
            model.train(images, labels)
            face_cascade = cv2.CascadeClassifier(haar_file)
            camera = cv2.VideoCapture(0) 
            while True:
                success, frame = camera.read()  # read the camera frame
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                print('after detectScale')
                print('FACES',faces)
                for(x,y,w,h) in faces:
                    print(x,y,w,h)
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0),2)
                    face=gray[y:y+h,x:x+w]
                    face_resize = cv2.resize(face, (width, height))
                    prediction = model.predict(face_resize)
                    print('after model prediction')
                    file_edit(names,prediction)
                    break
                break
                # key=cv2.waitKey(10)
                # if key == 27:
                #     break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 


def gen_frames_for_dbcreation(): 
    face_cascade = cv2.CascadeClassifier(haar_file)
    global camera
    camera = cv2.VideoCapture(0) 
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for(x,y,w,h) in faces:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0),2)
                    
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed_for_dbcreation():
    return Response(gen_frames_for_dbcreation(), mimetype='multipart/x-mixed-replace; boundary=frame')    

@app.route('/video_feed_attendance')
def video_feed_for_attendance():
    return Response(gen_frames_for_attendance(), mimetype='multipart/x-mixed-replace; boundary=frame')    

@app.route('/add_student',methods=['POST','GET'])
def add_student_details():
    if request.method == 'POST':
        if request.form.get('click') == 'Next':
            print(request.form)
            name=request.form.get('name')
            roll_no=request.form.get('roll_no')
            if(name=='' or roll_no==''): 
                flash('Invalid details! Please Enter again')
                return render_template('create__student_db.html')
            isAdded = addStudentUtil(name,roll_no)
            if isAdded==True:
                flash('Student added to database successfully!')
                return render_template('index.html')

def addStudentUtil(name,roll_no):
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
                    key=cv2.waitKey(10)
                    if key==27:
                        break
            camera.release()
            addStudentToDatabase(name,roll_no)
            name=''
            roll_no=''      
            return True     
             

def addStudentToDatabase(name,roll_no):
    try:
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("insert into students_details (name,roll_no) values (?,?)",(name,roll_no))
            cur.execute("select * from students_details")
            records = cur.fetchall()
            for i in records:
                print(i['name'], i['roll_no'])
            con.commit()
    except:
         con.rollback()    
    finally:
        con.close()
 
        
def deleteRecords(roll_no):
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("delete from students_details where roll_no= ? ",(roll_no)) 
    except:
         con.rollback()    
    finally:
        con.close()

def viewRecords():
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from students_details")
        records = cur.fetchall()
        for i in records:
            print(i['name'], i['roll_no'])
        return render_template('view_attendance.html',records=records)
    except:
         con.rollback()    
    finally:
        con.close()
       
    
if __name__ == '__main__':
    app.run(debug=True)
