from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import UserMixin,login_user,login_required,logout_user,LoginManager,current_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit
from wtforms.validators import InputRequired, Length, ValidationError
from wtforms import *
from wtforms.fields.html5 import *
from werkzeug.utils import secure_filename
from datetime import datetime
import time
from imageio import imread
#from camera import VideoCamera
import requests
import base64,cv2,io,imutils
import imghdr
import math
#from face_recognition.face_recognition_cli import image_files_in_folder
from sklearn import neighbors
from PIL import Image, ImageDraw
import os
#import io
import os.path
import numpy as np
import imutils


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'vfktyifuvjhbjhfvtyudydlcplxddaqweqplvjhjkbhv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 *5
app.config['UPLOAD_EXTENSIONS'] = ['txt','pdf','png','jpg','jpeg','gif']
app.config['UPLOAD_PATH'] = 'static/uploads'
app.config['UPLOAD_PROFILES'] = 'static/profiles'

db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

#db.create_all()
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"


from database import *

@login_manager.user_loader
def load_user(user_id):
    #try:
    #    return Student.query.get(int(user_id))
    #except:
    return Examiners.query.get(int(user_id))

#@login_manager.user_loader
#def load_examiner(user_id):
    
def ValidateUsername(username):
    existingusername = Student.query.filter_by(username=username).first()
    if existingusername:
        return existingusername
def ValidateEmail(email):
    existingemail = Student.query.filter_by(email=email).first()

    if existingemail:
        return existingemail
def ValidateexaminerUsername(username):
    existingusername = Examiners.query.filter_by(username=username).first()

    if existingusername:
        return existingusername
def ValidateexaminerEmail(email):
    existingemail = Examiners.query.filter_by(email=email).first()

    if existingemail:
        return existingemail 
def Validateunitid(unitid):
    existingunitid = units.query.filter_by(unitcode=unitid).first()

    if existingunitid:
        return existingunitid    
def Validateunit(unitcode,regno):
    unitvalid = studentunits.query.filter_by(unitcode=unitcode,regno=regno).first()

    if unitvalid:
        return unitvalid
def search(element): 
    searchunitbycode = units.query.filter(units.unitcode.like("%"+str(element)+"%")).all()
    searchunitbyname = units.query.filter(units.unitname.like("%"+str(element)+"%")).all()
    searchunitbylec = units.query.filter(units.lecturer.like("%"+str(element)+"%")).all()
    if searchunitbycode:
        return searchunitbycode
    if searchunitbyname:
        return searchunitbyname
    if searchunitbylec:
        return searchunitbylec

class examaddition(FlaskForm):
    examname = TextField(u'Exam Name',[validators.required(),validators.length(max=25)])
    startdate = DateField(u'Exam Date',[validators.required()],format='%Y-%m-%d')
    starttime = TimeField(u'Exam Time',[validators.required()],format='%H:%M')
    examduration = TextField(u'Exam Duration',[validators.required()])
    description = TextAreaField(u'Description',[validators.required(),validators.length(max=250)])
    totalmarks = IntegerField(u'Total Marks',[validators.required()])
    passmark = IntegerField(u'Passmark',[validators.required()])
    rules = TextAreaField(u'Exam Rules',[validators.required()])
@app.route('/',methods=['POST','GET'])
def index():
    session.pop('user', None)
    return render_template("index.html")
@app.route('/help')
@login_required
def help():
    
    return render_template("help.html",name=session['studentusername']\
        , fname=session['firstname'],mname=session['middlename'],lname=session['lastname'])

    
@app.route('/account', methods=['POST'])
def account():
    usernameoremail = request.form['login-username-email']
    password = request.form['login-pass']
    student = Student.query.filter_by(username=usernameoremail).first()
    email = Student.query.filter_by(email=usernameoremail).first()
    if student:
        if bcrypt.check_password_hash(student.password,password):
            login_user(student)
            session['studentid'] = student.id
            return redirect("/dashboard")
        else:
            flash("Wrong Password!")
            return render_template("index.html")
    elif email:
        if bcrypt.check_password_hash(email.password,password):
            login_user(email)
            session['studentid'] = email.id
            return redirect("/dashboard")
        else:
            flash("Wrong Password!")
            return render_template("index.html")
    else:
        flash("Wrong Email or Username")
        return render_template("index.html")
@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    session.pop('user', None)
    session.pop('studentid', None)
    logout_user()
    return redirect('/')

@app.route('/view')
@login_required
def view():
    
    people = Database.query.order_by(Database.date).all()
    return render_template("view.html", people = people,name=session['studentusername']\
        , fname=session['firstname'],mname=session['middlename'],lname=session['lastname'])
    
@app.route('/delete/<int:id>')    
@login_required
def delete(id):
   
    persontodelete = Database.query.get_or_404(id)
    try:
        db.session.delete(persontodelete)
        db.session.commit()
        return redirect("/view")
    except:
        return "An error occured while trying to delete"  
@app.route('/update/<int:id>', methods=["POST","GET"])
@login_required
def update(id):
    return "update done here"
@app.route('/check/<int:id>', methods=["POST","GET"])
@login_required
def check(id):
    return "file "+str(id)+" is here"
@app.route('/dashboard', methods=["POST","GET"])
@login_required
def dashboard():
    studentid = session['studentid']
    student = Student.query.filter_by(id=studentid).first()
    if student:
        session['studentusername'] = student.username
        session['firstname'] = student.firstname
        session['middlename'] = student.middlename
        session['lastname'] = student.lastname
        session['regno'] = student.regno
        session['image'] = student.image

        myunits = studentunits.query.filter_by(regno=session['regno']).all()
        return render_template("studentdashboard.html",name = session['studentusername'],\
            fname=session['firstname'],image=session['image'],mname=session['middlename'],lname=session['lastname'],\
            myunits = myunits)

@app.route('/test/<int:examid>', methods=["POST","GET"])
@login_required
def test(examid):

    myunits = studentunits.query.filter_by(regno=session['regno']).all()
    exam = studentunits.query.filter_by(regno=session['regno'], id=examid).first()
    examss = Examination.query.filter_by(unitcode=exam.unitcode).first()
    if examss:
        return render_template("testopen.html", examid=examid,name=session['studentusername']\
            , fname=session['firstname'],mname=session['middlename'],lname=session['lastname'],\
            myunits=myunits,exam = exam, exams = examss,image=session['image'])
    else:
        flash("No Examination yet!")
        return redirect("/dashboard")

def gen(camera):
    while True:
        data= camera.get_frame()    
        frame=data[0] 
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/openhtml')
@login_required
def openhtml():
    return render_template("open.html")
@app.route('/examination/<string:unitcode>', methods=["POST","GET"])
@login_required
def examination(unitcode):
    questions = Questions.query.filter_by(unitcode=unitcode).all()
    exam = units.query.filter_by(unitcode=unitcode).first()

    examss = Examination.query.filter_by(unitcode=exam.unitcode).first()
    time = int(examss.examduration)*60 

    return render_template("exampage.html", questions=questions,exam = exam,\
        username=session['studentusername'],num=time,image=session['image'])

@app.route('/opencvcam/<string:username>', methods=["POST","GET"])
def opencvcam(username):
    return render_template("opencv.html",username=username,image=session['image'])
@app.route('/studentsignup1')
def addstudent():
    
    return render_template("studentsignup.html")
@app.route('/studentsignup2')
def addstudenttwo():
    return render_template("studentsignuptwo.html")
@app.route('/imagesupload',methods=['POST','GET']) 
def imagesupload():
    if request.method == 'POST':
        image1 = request.files['file1']
    
        return "Next .........."+str(image1)+"->"
@app.route('/studentsignup')
def addface():
    classifier = VideoCamera.train("static/profiles", model_save_path="facesmodel.clf", n_neighbors=2) 
    return redirect('/')
def vidd(data):
    return Response(gen(VideoCamera(data)), mimetype='multipart/x-mixed-replace; boundary=frame')
#@socketio.on('catch-frame')
#def catch_frame(data):
#    print(data) 
#    emit('response_back', vidd(data))
@socketio.on('image')
def image(data_image):
    #print(data_image)
    sbuff = io.StringIO()
    #sbuff.write(base64.b64decode(data_image))
    sbuff = io.BytesIO(base64.b64decode(data_image))
    img = imread(sbuff)
    #pimg = Image.open(buff)

    #frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
    frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    frame = imutils.resize(frame, width=700)

    feed = vidd(frame)
    imgencode = cv2.imencode('.jpg', frame)[1]

    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpg;base64,'
    stringData = b64_src + stringData

    emit('response_back', stringData)
@app.route('/signupone',methods=['POST']) 
def signupone():
    if request.method == "POST":
        firstname = request.form['firstname']
        regno = request.form['regno']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        email=request.form['email']
        username = request.form['username']
        password = request.form['password']
        confpassword = request.form['confpassword']
        file = request.files['file']
        filename = secure_filename(file.filename)
        
        if password == confpassword:
            if ValidateUsername(username) == None:
                if ValidateEmail(email) == None:
                    hashed_password = bcrypt.generate_password_hash(password)
                    if filename != "":
                        file_ext = os.path.splitext(filename)[1]
                        try:
                            newpath = app.config['UPLOAD_PROFILES']+'/'+username
                            os.mkdir(newpath)
                            file.save(os.path.join(newpath, filename))
                            newstudent = Student(firstname=firstname,middlename=middlename,\
                            lastname=lastname,email=email,image=filename,username=username,regno=regno,password=hashed_password)
                        except OSError:
                            file.save(os.path.join(app.config['UPLOAD_PROFILES']+'/'+username, filename))
                            newstudent = Student(firstname=firstname,middlename=middlename,\
                            lastname=lastname,email=email,image=filename,username=username,regno=regno,password=hashed_password)
                    try:
                        db.session.add(newstudent)
                        db.session.commit()
                        flash("Account created succefully")
                        return redirect("/")
                    except:
                        flash("An issue occured while saving your data")
                        return render_template("studentsignup.html")
                else:
                    flash("Email already exist! Try another one.")
                    return render_template("studentsignup.html")
            else:
                flash("Username already exist! Try another one.")
                return render_template("studentsignup.html")
        else:
            flash("Passwords do not match!")
            return render_template("studentsignup.html")
    else:
        flas("Wrong method!")
        return redirect("/studentsignup")

##Examiner side of the system ##################################################################################################################################################

@app.route('/examinerhelp')
@login_required
def examinerhelp():
    
    return render_template("examinerhelp.html", title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'])

@app.route('/editor')
@login_required
def editor():
    
    return render_template("editor.html")
@app.route('/examiner', methods=['POST'])
def examiner():
    eusernameoremail = request.form['login-username-email']
    epassword = request.form['login-pass']
    examiner = Examiners.query.filter_by(username=eusernameoremail).first()
    examineremail = Examiners.query.filter_by(email=eusernameoremail).first()
    if examiner:
        if bcrypt.check_password_hash(examiner.password,epassword):
            login_user(examiner)
            session['examinerid'] = examiner.id
            return redirect("/examinerdashboard")
        else:
            flash("Wrong Password!")
            return render_template("index.html")
    elif examineremail:
        if bcrypt.check_password_hash(examineremail.password,epassword):
            login_user(examineremail)
            session['examinerid'] = examineremail.id
            return redirect("/examinerdashboard")
        else:
            flash("Wrong Password!")
            return render_template("index.html")
    else:
        flash("Wrong Email or Username!")
        return render_template("index.html")
@app.route('/examinerdashboard')
@login_required
def examinerdashboard():
    examinerid = session['examinerid']
    examiner = Examiners.query.filter_by(id=examinerid).first()
    if examiner:
        session['title'] = examiner.title
        session['efirstname'] = examiner.firstname
        session['emiddlename'] = examiner.middlename
        session['elastname'] = examiner.lastname
        courses = units.query.order_by(units.date.desc()).limit(3).all()
        return render_template("examinerindex.html", title=session['title'],firstname=session['efirstname'],\
                    middlename=session['emiddlename'],lastname=session['elastname'], units=courses)

@app.route("/addunit",methods=['GET','POST'])
@login_required
def upload_file ():
    if request.method == 'POST' :
        unitname = request.form['unitname']
        unitid = request.form['unitid']
        unitdescription = request.form['description']
        file = request.files['file']
        filename = secure_filename(file.filename)
        date = datetime.now()
        lecturename = session['title'] + " " + session['efirstname'] + " " + session['elastname']
        if Validateunitid(unitid) == None:
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                #if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                #    abort(400)
                file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                newunit = units(unitname=unitname, unitcode=unitid,description=unitdescription\
                        ,lecturer=lecturename,date=date,image=filename,status='True')
                try:
                        db.session.add(newunit)
                        db.session.commit()
                        flash("Unit added successfully")
                        return redirect("/units")
                except:
                    flash("There was an issue while adding unit!")
                    return redirect("/units")
                flash("No image selected")
                return redirect("/units")
        else:
            flash("Wrong request!")
            return redirect("/units")
@app.route('/deleteunit/<int:id>')    
@login_required
def deleteunit(id):
   
    unittodelete = units.query.get_or_404(id)
    try:
        db.session.delete(unittodelete)
        db.session.commit()
        return redirect("/units")
    except:
        return "An error occured while trying to delete"  
@app.route('/updateunit/<int:id>', methods=["POST","GET"])
@login_required
def updatunit(id):
    return "update unit "+str(id)+" here"
@app.route('/checkunit/<string:unitcode>', methods=["POST","GET"])
@login_required
def checkunit(unitcode):
    courses = units.query.filter_by(unitcode=unitcode).all()
    questions = Questions.query.order_by(Questions.id).filter_by(unitcode=unitcode).all()
    return render_template("viewunits.html", units = courses, title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'],questions=questions)

@app.route('/addexamt/<string:unitcode>', methods=["POST","GET"])
@login_required
def addexamt(unitcode):
    form = examaddition()
    exam = Examination.query.filter_by(unitcode=unitcode).order_by(Examination.date).all()
    return render_template("examadd.html",form=form,unitcode=unitcode, exams = exam, title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'])
@app.route('/addexaminfo', methods=["POST"])
@login_required
def addexaminfo():
    form = examaddition()

    if form.is_submitted():
        unitcode = request.form['unitcode']
        examname = form.examname.data
        examdate = form.startdate.data
        examtime = form.starttime.data
        examduration = form.examduration.data
        description = form.description.data
        rules = form.rules.data
        passmark = form.passmark.data
        marks = form.totalmarks.data
        year = examdate.year
        month = examdate.month
        day = examdate.day
        hour = examtime.hour
        minute = examtime.minute

        examdatetime = datetime(year,month,day,hour,minute,0,0)
        #examdatetime = str(str(examdate) +" "+str(examtime)+".000000")
        
        exam = Examination.query.filter_by(unitcode=unitcode).order_by(Examination.date).all()

        newexam = Examination(unitcode=unitcode,unitname=examname,startdate=examdatetime,examduration=examduration\
            ,description=description,rules=rules,totalmarks=marks, passmark=passmark,status='False')
        try:
            db.session.add(newexam)
            db.session.commit()
            flash("Examination created succefully")

            return redirect('/addexamt/'+str(unitcode))
        except:
            flash("Error while creating the exams1")
            return redirect('/addexamt/'+str(unitcode))
@app.route('/units')
@login_required
def unitsview():
    
    courses = units.query.order_by(units.date).all()
    return render_template("units.html", units = courses, title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'])
@app.route('/addexam')
@login_required
def addexam():
    
    return render_template("add.html", title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'])
@app.route('/questions/<string:questionid>')
@login_required
def questions(questionid):
    questiontype = Questions.query.filter_by(questionid=questionid).first()
    if questiontype.questiontype == 'Prose':
        question = QuestionsProse.query.filter_by(questionid=questionid).first()
        return render_template("one.html", question=question,type='Prose')

    elif questiontype.questiontype == 'Multiple Select':
        question = QuestionsMulti.query.filter_by(questionid=questionid).first()
        select = [question.select1,question.select2,question.select3,question.select4,question.select5,\
        question.select6,question.select7,question.select8,question.select9,question.select10]
        choices = []
        numbers = range(1,int(question.choises)+1)
        for x in numbers:
            choice = "select"+str(x)
            value = select[int(x)-1]
            choicelist = [choice,value]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
            choices.append(choicelist)
        return render_template("one.html", question=question,type='Multiple Select',choices=choices)

    elif questiontype.questiontype == 'Multiple Choice':
        question = QuestionsMultiple.query.filter_by(questionid=questionid).first()
        return render_template("one.html", question=question,type='Multiple Choice')
        
    elif questiontype.questiontype == 'True or False':
        question = QuestionsTrueFalse.query.filter_by(questionid=questionid).first()
        return render_template("one.html", question=question, type='True or False')
        #return render_template("one.html",questionid=questionid)
@app.route('/searchunit', methods=['POST'])
@login_required
def searchunit():
    element = request.form['search']
    myunits = studentunits.query.filter_by(regno=session['regno']).all()
    if element == "":
        flash("Search input is empty!")
        return render_template("studentdashboard.html",name = session['studentusername'],\
                fname=session['firstname'],mname=session['middlename'],lname=session['lastname'],\
                myunits=myunits)
    else:
        searchunit = search(element)
        if searchunit:
            return render_template("studentdashboard.html",name = session['studentusername'],\
                    fname=session['firstname'],mname=session['middlename'],lname=session['lastname'],\
                    units=searchunit,myunits=myunits)
        else:
            flash("Unit not available!")
            return redirect('/dashboard')
@app.route('/searchunit2', methods=['POST'])
@login_required
def searchunit2():
    element = request.form['search']
    if element == "":
        flash("Search input is empty!")
        return redirect('/units')
    else:
        searchunit = search(element)
        if searchunit:
            return render_template("units.html", units = searchunit, title=session['title']\
                ,firstname=session['efirstname'],middlename=session['emiddlename'],\
                lastname=session['elastname'])
        else:
            flash("Unit not available!")
            return redirect('/units')
@app.route('/enroll/<string:unitcode>')
@login_required
def enroll(unitcode):
    enrolling = units.query.filter_by(unitcode=unitcode).first()
    query = studentunits(unitname=enrolling.unitname,unitcode=enrolling.unitcode,regno=session['regno'],\
        username=session['studentusername'],description=enrolling.description,lecturer=enrolling.lecturer,\
        status='Active',image=enrolling.image)
    validunit = Validateunit(unitcode,session['regno'])
    if validunit:
        flash("Unit already enrolled!")
        return redirect('/dashboard')
    else:
        try:
            db.session.add(query)
            db.session.commit()
            flash("Unit enrolled succefully")
            return redirect('/dashboard')
        except:
            flash("Unit registration failed!")
            return redirect('/dashboard')
        
@app.route('/multiplechoice', methods=['POST'])
@login_required
def multiplechoice():
    if request.method == "POST":
        unitcode = request.form['unitcode']
        unitid = request.form['unitid']
        question = request.form['question1']
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        d = request.form['d']
        answer = request.form['answer']
        marks = request.form['marks']
        date = datetime.now()
        qid = unitcode + date.strftime('%H%M%S')
        newq = QuestionsMultiple(unitcode=unitcode,question=question,uploads='',select1=a,select2=b,\
            select3=c,select4=d,answer=answer,marks=marks,status='False',questionid=qid)
        lecturename = session['title'] + " " + session['efirstname'] + " " + session['elastname']
        newq2 = Questions(unitcode=unitcode, questiontype='Multiple Choice',questionid=qid,\
            creator=lecturename)
        try:
            db.session.add(newq)
            db.session.add(newq2)
            db.session.commit()
            flash("Question added succefully")
            return redirect('/checkunit/{}'.format(unitcode))
        except:
            flash("There was an error adding the question")
            return redirect('/checkunit/{}'.format(unitcode))
@app.route('/multipleselect', methods=['POST'])
@login_required
def multipleselect():
    if request.method == "POST":
        unitcode = request.form['unitcode']
        unitid = request.form['unitid']
        question = request.form['question']
        s1 = request.form['select1']
        s2 = request.form['select2']
        s3 = request.form['select3']
        s4 = request.form['select4']
        s5 = request.form['select5']
        s6 = request.form['select6']
        s7 = request.form['select7']
        s8 = request.form['select8']
        s9 = request.form['select9']
        s10 = request.form['select10'] 
        choices = request.form['choices']       
        marks = request.form['marks']
        date = datetime.now()
        qid = unitcode + date.strftime('%H%M%S')
        newq = QuestionsMulti(unitcode=unitcode,question=question,uploads='',choises=choices,select1=s1,select2=s2,\
            select3=s3,select4=s4,select5=s5,select6=s6,select7=s7,select8=s8,select9=s9,select10=s10,\
            marks=marks,status='False',questionid=qid)
        lecturename = session['title'] + " " + session['efirstname'] + " " + session['elastname']
        newq2 = Questions(unitcode=unitcode, questiontype='Multiple Select',questionid=qid,\
            creator=lecturename)
        try:
            db.session.add(newq)
            db.session.add(newq2)
            db.session.commit()
            flash("Question added succefully")
            return redirect('/checkunit/{}'.format(unitcode))
        except:
            flash("There was an error adding the question")
            return redirect('/checkunit/{}'.format(unitcode))
@app.route('/prose', methods=['POST'])
@login_required
def prose():
    if request.method == "POST":
        unitcode = request.form['unitcode']
        unitid = request.form['unitid']
        question = request.form['question']
        marks = request.form['marks']
        date = datetime.now()
        qid = unitcode + date.strftime('%H%M%S')
        lecturename = session['title'] + " " + session['efirstname'] + " " + session['elastname']
        newq2 = Questions(unitcode=unitcode, questiontype='Prose',questionid=qid,\
            creator=lecturename)
        newq = QuestionsProse(unitcode=unitcode,question=question,uploads='',questionid=qid,marks=marks,\
            status='False')
        try:
            db.session.add(newq)
            db.session.add(newq2)
            db.session.commit()
            flash("Question added succefully")
            return redirect('/checkunit/{}'.format(unitcode))
        except:
            flash("There was an error adding the question")
            return redirect('/checkunit/{}'.format(unitcode))
@app.route('/trueorfalse', methods=['POST'])
@login_required
def trueorfalse():
    if request.method == "POST":
        unitcode = request.form['unitcode']
        unitid = request.form['unitid']
        question = request.form['question']
        marks = request.form['marks']
        date = datetime.now()
        qid = unitcode + date.strftime('%H%M%S')
        lecturename = session['title'] + " " + session['efirstname'] + " " + session['elastname']
        newq2 = Questions(unitcode=unitcode, questiontype='True or False',questionid=qid,\
            creator=lecturename)
        newq = QuestionsTrueFalse(unitcode=unitcode,question=question,uploads='',questionid=qid,marks=marks,\
            status='False')
        try:
            db.session.add(newq)
            db.session.add(newq2)
            db.session.commit()
            flash("Question added succefully")
            return redirect('/checkunit/{}'.format(unitcode))
        except:
            flash("There was an error adding the question")
            return redirect('/checkunit/{}'.format(unitcode))
@app.route('/qbank')
@login_required
def qbank():
    questions = Questions.query.order_by(Questions.id).all()
    return render_template("questionbank.html", title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'],questions=questions)

@app.route('/about')
@login_required
def about():
    return render_template("about.html", title=session['title'],firstname=session['efirstname'],\
                middlename=session['emiddlename'],lastname=session['elastname'])

@app.route('/examinersignup')
def signupexaminer(): 
    return render_template("signupexaminer.html")
@app.route('/addexaminer',methods=['POST'])
def addexaminer(): 
    if request.method == "POST":
        title = request.form['title']
        efirstname = request.form['efirstname']
        emiddlename = request.form['emiddlename']
        elastname = request.form['elastname']
        eemail=request.form['eemail']
        eusername = request.form['eusername']
        epassword = request.form['epassword']
        econfpassword = request.form['econfpassword']
        if epassword == econfpassword:
            if ValidateexaminerUsername(eusername) == None:
                if ValidateexaminerEmail(eemail) == None:
                    ehashed_password = bcrypt.generate_password_hash(epassword)
                    newexaminer = Examiners(title=title, firstname=efirstname,middlename=emiddlename\
                        ,lastname=elastname,email=eemail,username=eusername,password=ehashed_password)
                    try:
                        db.session.add(newexaminer)
                        db.session.commit()
                        return redirect("/")
                    except:
                        flash("An issue occured while saving your data")
                        return render_template("signupexaminer.html")
                else:
                    flash("Email already exist! Try another one.")
                    return render_template("signupexaminer.html")
            else:
                flash("Username already exist! Try another one.")
                return render_template("signupexaminer.html")
        else:
            flash("Passwords do not match!")
            return render_template("signupexaminer.html")
    else:
        flash("Wrong method!")
        return render_template("signupexaminer.html")

@app.route('/logoutexaminer',methods=['POST','GET'])
@login_required
def logoutexaminer():
    session.pop('user', None)
    session.pop('examinerid', None)
    session.pop('title',None)
    session.pop('efirstname',None)
    session.pop('emiddlename',None)
    session.pop('elastname',None)
    logout_user()
    return redirect('/')

#@app.errorhandler(404)
#def page_not_found(e):
#    flash(u'Page Not Found!')
#    return render_template("pagenotfound.html")


@app.route('/<int:num>s')
@app.route('/<int:num>')
def timer(num):
    return render_template('index.html', num=num)

@app.route('/<int:num>m')
def minutes(num):
    return redirect(url_for('timer', num=num*60))


@app.route('/<int:num>h')
def hours(num):
    return redirect(url_for('timer', num=num*3600))   

if __name__ == "__main__":
    socketio.run(app,debug=True, host='0.0.0.0', port=8080)
    #app.run(debug=True)#,host="169.254.78.29")