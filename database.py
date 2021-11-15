from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,logout_user,LoginManager,current_user
from datetime import datetime
from app import db


######################################### TEST PART OF THE DATABASE ##################################################


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ << Comments by Mutai Tony >> #

######################################## USERS PART OF THE DATABASE ##################################################
class Student(db.Model,UserMixin):
        id =db.Column(db.Integer,primary_key=True)
        firstname = db.Column(db.String(200),nullable=False)
        middlename = db.Column(db.String(200),nullable=True)
        lastname = db.Column(db.String(200),nullable=False)
        regno = db.Column(db.String(200),nullable=False,unique=True)
        username = db.Column(db.String(200),nullable=False,unique=True)
        email = db.Column(db.String(200),nullable=False,unique=True)
        password = db.Column(db.String(200),nullable=False)
        image = db.Column(db.String(200),nullable=True)
        def __repr__(self):
        	return 'Student {}'.format(self.id)

class Examiners(db.Model,UserMixin):
        id =db.Column(db.Integer,primary_key=True)
        title=db.Column(db.String(20),nullable=True)
        firstname = db.Column(db.String(200),nullable=False)
        middlename = db.Column(db.String(200),nullable=True)
        lastname = db.Column(db.String(200),nullable=False)
        username = db.Column(db.String(200),nullable=False,unique=True)
        email = db.Column(db.String(200),nullable=False,unique=True)
        password = db.Column(db.String(200),nullable=False)
        def __repr__(self):
            return 'Examiners {}'.format(self.id)

class units(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitname = db.Column(db.String(200),nullable=False)
		unitcode = db.Column(db.String(200),unique=True,nullable=False)
		description= db.Column(db.String(4294000000),nullable=False)
		lecturer = db.Column(db.String(200),nullable=False)
		status= db.Column(db.String(200),nullable=False)
		image = db.Column(db.String(200),nullable=True)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

class studentunits(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitname = db.Column(db.String(200),nullable=False)
		unitcode = db.Column(db.String(200),unique=False,nullable=False)
		regno = db.Column(db.String(200),nullable=False,unique=False)
		username = db.Column(db.String(200),nullable=False,unique=False)
		description= db.Column(db.String(4294000000),nullable=False)
		lecturer = db.Column(db.String(200),nullable=False)
		status= db.Column(db.String(200),nullable=False)
		image = db.Column(db.String(200),nullable=True)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ << Comments by Mutai Tony >> #

############################ EXAMINATION PART OF THE DATABASE ######################################################

class Examination(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitname = db.Column(db.String(200),nullable=False)
		unitcode = db.Column(db.String(200),nullable=False)
		description= db.Column(db.String(4294000000),nullable=False)
		rules = db.Column(db.String(4294000000), nullable=True)
		totalmarks = db.Column(db.Integer,nullable=False)
		passmark = db.Column(db.Integer, nullable=False)
		startdate = db.Column(db.DateTime)
		examduration = db.Column(db.Integer, nullable=False)
		status= db.Column(db.String(200),nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		def __repr__(self):
			return 'Unit {}'.format(self.id)
class Questions(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitcode = db.Column(db.String(200),nullable=False)
		questiontype = db.Column(db.String(200),nullable=False)
		questionid = db.Column(db.String(4294000000),nullable=False)
		creator = db.Column(db.String(200),nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

class QuestionsMultiple(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitcode = db.Column(db.String(200),nullable=False)
		question = db.Column(db.String(4294000000),nullable=False)
		questionid = db.Column(db.String(4294000000),nullable=False)
		uploads = db.Column(db.String(200),nullable=True)
		select1 = db.Column(db.String(4294000000),nullable=True)
		select2 = db.Column(db.String(4294000000),nullable=True)
		select3 = db.Column(db.String(4294000000),nullable=True)
		select4 = db.Column(db.String(4294000000),nullable=True)
		answer = db.Column(db.String(4294000000),nullable=True)
		marks = db.Column(db.Integer,nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		status = db.Column(db.String(200),nullable=True)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

class QuestionsTrueFalse(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitcode = db.Column(db.String(200),nullable=False)
		question = db.Column(db.String(4294000000),nullable=False)
		questionid = db.Column(db.String(4294000000),nullable=False)
		uploads = db.Column(db.String(200),nullable=True)
		answer = db.Column(db.String(4294000000),nullable=True)
		marks = db.Column(db.Integer,nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		status = db.Column(db.String(200),nullable=True)
		def __repr__(self):
			return 'Unit {}'.format(self.id)
		
class QuestionsMulti(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitcode = db.Column(db.String(200),nullable=False)
		question = db.Column(db.String(4294000000),nullable=False)
		questionid = db.Column(db.String(4294000000),nullable=False)
		choises = db.Column(db.Integer,nullable=False)
		uploads = db.Column(db.String(200),nullable=True)
		select1 = db.Column(db.String(4294000000),nullable=True)
		select2 = db.Column(db.String(4294000000),nullable=True)
		select3 = db.Column(db.String(4294000000),nullable=True)
		select4 = db.Column(db.String(4294000000),nullable=True)
		select5 = db.Column(db.String(4294000000),nullable=True)
		select6 = db.Column(db.String(4294000000),nullable=True)
		select7 = db.Column(db.String(4294000000),nullable=True)
		select8 = db.Column(db.String(4294000000),nullable=True)
		select9 = db.Column(db.String(4294000000),nullable=True)
		select10 = db.Column(db.String(4294000000),nullable=True)
		marks = db.Column(db.Integer,nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		status = db.Column(db.String(200),nullable=True)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

class QuestionsProse(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		unitcode = db.Column(db.String(200),nullable=False)
		question = db.Column(db.String(4294000000),nullable=False)
		questionid = db.Column(db.String(4294000000),nullable=False)
		marks = db.Column(db.Integer,nullable=False)
		uploads = db.Column(db.String(200),nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		status = db.Column(db.String(200),nullable=True)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ << Comments by Mutai Tony >> #

class StudentsAnswers(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		studentname = db.Column(db.String(200),nullable=False)
		regno = db.Column(db.String(200),nullable=False)
		unitname = db.Column(db.String(200),nullable=False)
		unitcode = db.Column(db.String(200),nullable=False)
		question = db.Column(db.String(4294000000),nullable=False)
		questionid = db.Column(db.String(200),nullable=False)
		questiontype = db.Column(db.String(200),nullable=False)
		studentanswer = db.Column(db.String(4294000000),nullable=False)
		marks = db.Column(db.Integer,nullable=False)
		marksawarded = db.Column(db.Integer,nullable=True)
		examinername = db.Column(db.String(4294000000), nullable=True)
		uploads = db.Column(db.String(200),nullable=True)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		status = db.Column(db.String(200),nullable=True)
		def __repr__(self):
			return 'Unit {}'.format(self.id)

class Results(db.Model):
		id = db.Column(db.Integer,primary_key=True)
		regno = db.Column(db.String(200),nullable=False)
		unitcode = db.Column(db.String(200),nullable=False)
		question = db.Column(db.String(4294000000),nullable=False)
		result = db.Column(db.String(200),nullable=False)
		date = db.Column(db.DateTime,default=datetime.utcnow)
		status = db.Column(db.String(200),nullable=True)
		def __repr__(self):
			return 'Unit {}'.format(self.id)