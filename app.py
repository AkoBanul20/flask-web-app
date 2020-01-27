from flask import Flask,render_template,request,session,url_for,redirect,flash
from flask_mysqldb import MySQL
from datetime import datetime, date
from datetime import timedelta
import re
app = Flask(__name__)

app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '153303AaCc'
app.config['MYSQL_DB'] = 'cssdb'

mysql = MySQL(app)

@app.template_filter('datetimeformat')
def datetimeformat(value, format = '%H:%M:%S'):
    return value.strftime(format)

@app.route('/')
def index():
   return render_template('index.html')


# STudents functions naman dito
@app.route('/student_register',  methods=['POST','GET'])
def registration():
    if request.method == 'POST':
        lastname = request.form['lname']
        firstname = request.form['fname']
        middlename = request.form['mname']
        grade = request.form['grade']
        strand = request.form['strand']
        section = request.form['section']
        lrn = request.form['lrn']
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student_tbl (student_lrn,student_lastname,student_firstname,student_middlename,grade_id,strand_id,section_id,student_username,student_password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(lrn,lastname,firstname,middlename,grade,strand,section,username,password))
        mysql.connection.commit()
        cur.close()
        flash("Succesfully Registered!")
        # return render_template('student_login.html')
        return redirect(url_for('login_student'))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `grade_tbl`")
        data = cur.fetchall()
        cur.execute("SELECT * FROM `strand_tbl`")
        data2 =  cur.fetchall()
        cur.close()
        return render_template('signup.html',grade=data,strand=data2)
@app.route('/Student',methods=['POST','GET'])
def home():
    if "loggedin" in session:
        todaysched = datetime.today().strftime('%A')
        username = session["username"]
        id =  session["id"]
        grade = session["grade"]
        strand = session["strand"]
        section = session["section"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `schedule_tbl` WHERE `day` LIKE %s AND `grade` LIKE %s AND `strand` LIKE %s AND `section` LIKE %s",(todaysched,grade,strand,section))
        schedulelist = cur.fetchall()
        return render_template('Student_dashboard.html',username=username,id=id,schedule=schedulelist)
    else:
        return redirect(url_for('login_student')) 


@app.route('/student_login', methods=['POST','GET'])
def login_student():
    if request.method == 'POST':
        username =  request.form['username']
        password =  request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student_tbl WHERE student_username = %s AND student_password= %s",(username,password))
        account = cur.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account[0]
            session["grade"] = account[5]
            session["strand"] = account[6]
            session["section"] = account[7]
            session["username"] = account[8]
            return redirect(url_for('home'))
        else:
            flash('Incorrect username/password!')
            username = request.form['username']
            return render_template('student_login.html',username=username)
    else:
        if "loggedin" in session:
            username = session['username']
            id = session['id']
            return redirect(url_for('home'))
        else:
            return render_template('student_login.html')
@app.route('/profile')
def prof():
    if "loggedin" in session:
        username = session['username']
        id = session['id']
        return render_template('student_profile.html',username=session['username'],id=session['id'])
    else:
        return redirect(url_for('login_student'))
# Log out ng dalawang User
@app.route('/logout')
def logout():
    if "loggedinteacher" in session:
        session.pop('loggedinteacher', None)
        session.pop('tid', None)
        session.pop('tusername',None)
        return redirect(url_for('teacher_login'))
    elif "loggedin":
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username',None)
        return redirect(url_for('login_student'))


# Teacher functions na dito
@app.route('/teacher_register', methods=['POST','GET'])
def teacher_register():
    if request.method == 'POST':
        emp_no =  request.form['tno']
        lastname = request.form['tlname']
        firstname =  request.form['tfname']
        middlename = request.form['tmname']
        email = request.form['temail']
        username = request.form['tusername']
        password = request.form['tpass']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO teacher_tbl(teacher_no,teacher_lastname,teacher_firstname,teacher_middlename,teacher_email,teacher_username,teacher_password) VALUES (%s,%s,%s,%s,%s,%s,%s)",(emp_no,lastname,firstname,middlename,email,username,password))
        mysql.connection.commit()
        cur.close()
        flash('Succesfully Registered!!')
        return render_template('teacher_signup.html')
    else:
        return render_template('teacher_signup.html')
    
@app.route('/teacher_login', methods=['POST','GET'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teacher_tbl WHERE teacher_username = %s AND teacher_password= %s",(username,password))
        teacher = cur.fetchone()
        if teacher:
            session["loggedinteacher"] = True
            session["tid"] = teacher[0]
            session["tusername"] = teacher[6]
            response = 'Welcome!'
            return redirect(url_for('teacher'))
        else:
            flash('Incorrect username/password!')
            return render_template('teacher_login.html',username=username)
    else:
        if "loggedinteacher" in session:
            return redirect(url_for('teacher'))
        else:
            return render_template('teacher_login.html')


@app.route('/teacher', methods=['POST','GET'])
def teacher():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(id) FROM student_tbl")
        myresult = cur.fetchone()
        cur.execute("SELECT COUNT(id) FROM room_tbl")
        room = cur.fetchone()
        return render_template('teacher_dashboard.html',username=username,id=id,count=myresult,room=room)
    else:
        return redirect(url_for('teacher_login'))

#rooms CRUD
@app.route('/rooms', methods=['POST','GET'])
def rooms():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM room_tbl")
        roomlist = cur.fetchall()
        return render_template('rooms.html',room=roomlist,username=username,id=id)
    else:
        return redirect(url_for('teacher_login'))

@app.route('/insert_room',methods=['POST','GET'])
def insert_room():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            room = request.form['room_num']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO `room_tbl` ( `room_no`) VALUES (%s)",[room])
            mysql.connection.commit()
            flash("Data Inserted Successfully")
            return redirect(url_for('rooms'))
    else:
        return redirect(url_for('teacher_login'))
@app.route('/delete_room/<string:id_data>', methods=['GET'])
def delete_room(id_data):
    if "loggedinteacher" in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM room_tbl WHERE id=%s",(id_data))
        mysql.connection.commit()
        flash("Record Has Been Deleted Successfully")
        return redirect(url_for('rooms'))
    else:
        return redirect(url_for('rooms'))
@app.route('/update_room', methods=['POST','GET'])
def update_room():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            id_data = request.form['id']
            room_update = request.form['room_num']
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE room_tbl
                SET room_no=%s
                WHERE id=%s
                """, (room_update,id_data))
            flash("Data Updated Successfully")
            mysql.connection.commit()
            return redirect(url_for('rooms'))
    else:
        return redirect(url_for('rooms'))

#grade CRUD
@app.route('/grades', methods=['POST','GET'])
def grades():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM grade_tbl")
        grade_list = cur.fetchall()
        return render_template('grade.html',grade=grade_list,username=username,id=id)
    else:
        return redirect(url_for('teacher_login'))

@app.route('/insert_grade',methods=['POST'])
def insert_grade():
    if "loggedinteacher" in session:
        grade = request.form['grade']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `grade_tbl` ( `grade_name`) VALUES (%s)",[grade.upper()])
        mysql.connection.commit()
        flash("Data Inserted Successfully")
        return redirect(url_for('grades'))
    else:
        return redirect(url_for('grades'))

@app.route('/delete_grade/<string:id_data>',methods=['GET'])
def delete_grade(id_data):
    if "loggedinteacher" in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM grade_tbl WHERE id=%s",(id_data))
        mysql.connection.commit()
        flash("Record Has Been Deleted Successfully")
        return redirect(url_for('grades'))
    else:
        return redirect(url_for('grades'))
@app.route('/update_grade', methods=['POST','GET'])
def update_grade():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            id_data = request.form['id']
            grade_update = request.form['grade']
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE grade_tbl
                SET grade_name=%s
                WHERE id=%s
                """, (grade_update.upper(),id_data))
            flash("Data Updated Successfully")
            mysql.connection.commit()
            return redirect(url_for('grades'))
    else:
        return redirect(url_for('grades'))


# Strand CRUD
@app.route('/strand', methods= ['POST','GET'])
def strand():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM strand_tbl")
        strandlist = cur.fetchall()
        return render_template('strand.html',strand=strandlist,username=username,id=id)
    else:
        return redirect(url_for('teacher_login'))
@app.route('/insert_strand', methods=['POST','GET'])
def insert_strand():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            strand_code = request.form['strand_code']
            strand_name = request.form['strand_name']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO strand_tbl (strand_code,strand_name) VALUES (%s,%s)",(strand_code.upper(),strand_name.upper()))
            mysql.connection.commit()
            flash("Data Inserted Successfully")
            return redirect(url_for('strand'))
        else:
            return redirect(url_for('strand'))
    else:
        return redirect(url_for('strand'))
@app.route('/delete_strand/<string:id_data>',methods=['GET'])
def delete_strand(id_data):
    if "loggedinteacher" in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM strand_tbl WHERE id=%s",(id_data))
        mysql.connection.commit()
        flash("Record Has Been Deleted Successfully")
        return redirect(url_for('strand'))
    else:
        return redirect(url_for('strand'))


@app.route('/update_strand',methods=['POST','GET'])
def update_strand():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            id_data = request.form['id']
            strand_code = request.form['strand_code']
            strand_name = request.form['strand_name']
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE strand_tbl
                SET strand_code=%s, strand_name=%s
                WHERE id=%s
                """, (strand_code.upper(),strand_name.upper(),id_data))
            flash("Data Updated Successfully")
            mysql.connection.commit()
            return redirect(url_for('strand'))
        else:
            return redirect(url_for('strand'))
    else:
        return redirect(url_for('strand'))

#section CRUD
@app.route('/section', methods= ['POST','GET'])
def section():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM section_tbl")
        sectionlist = cur.fetchall()
        return render_template('section.html',section=sectionlist,username=username,id=id)
    else:
        return redirect(url_for('teacher_login'))
@app.route('/insert_section', methods=['POST','GET'])
def insert_section():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            section_name = request.form['section_name']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO section_tbl (section_name) VALUES (%s)",[section_name])
            mysql.connection.commit()
            flash("Data Inserted Successfully")
            return redirect(url_for('section'))
        else:
            return redirect(url_for('section'))
    else:
        return redirect(url_for('section'))
@app.route('/delete_section/<string:id_data>',methods=['GET'])
def delete_section(id_data):
    if "loggedinteacher" in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM section_tbl WHERE id=%s",(id_data))
        mysql.connection.commit()
        flash("Record Has Been Deleted Successfully")
        return redirect(url_for('section'))
    else:
        return redirect(url_for('section'))


@app.route('/update_section',methods=['POST','GET'])
def update_section():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            id_data = request.form['id']
            section_name = request.form['section_name']
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE section_tbl
                SET section_name=%s
                WHERE id=%s
                """, (section_name.upper(),id_data))
            flash("Data Updated Successfully")
            mysql.connection.commit()
            return redirect(url_for('section'))
        else:
            pass
    else:
        return redirect(url_for('section'))

#subject CRUD

@app.route('/subject', methods= ['POST','GET'])
def subject():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM subject_tbl")
        subjectlist = cur.fetchall()
        return render_template('subject.html',subject=subjectlist,username=username,id=id)
    else:
        return redirect(url_for('teacher_login'))
@app.route('/insert_subject', methods=['POST','GET'])
def insert_subject():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            subject_code = request.form['subject_code']
            subject_name = request.form['subject_name']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO subject_tbl (subject_code,subject_name) VALUES (%s,%s)",(subject_code.upper(),subject_name.upper()))
            mysql.connection.commit()
            flash("Data Inserted Successfully")
            return redirect(url_for('subject'))
        else:
            return redirect(url_for('subject'))
    else:
        return redirect(url_for('subject'))
@app.route('/delete_subject/<string:id_data>',methods=['GET'])
def delete_subject(id_data):
    if "loggedinteacher" in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM subject_tbl WHERE id=%s",(id_data))
        mysql.connection.commit()
        flash("Record Has Been Deleted Successfully")
        return redirect(url_for('subject'))
    else:
        return redirect(url_for('subject'))


@app.route('/update_subject',methods=['POST','GET'])
def update_subject():
    if "loggedinteacher" in session:
        if request.method == 'POST':
            id_data = request.form['id']
            strand_code = request.form['subject_code']
            strand_name = request.form['subject_name']
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE subject_tbl
                SET subject_code=%s, subject_name=%s
                WHERE id=%s
                """, (strand_code.upper(),strand_name.upper(),id_data))
            flash("Data Updated Successfully")
            mysql.connection.commit()
            return redirect(url_for('subject'))
        else:
            return redirect(url_for('subject'))
    else:
        return redirect(url_for('subject'))

#schedule Crud
@app.route('/schedule',methods=['POST','GET'])
def schedule():
    if "loggedinteacher" in session:
        username = session["tusername"]
        id =  session["tid"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM schedule_tbl")
        schedulelist = cur.fetchall()
        cur.execute("SELECT * FROM day_tbl")
        daylist =  cur.fetchall()
        cur.execute("SELECT * FROM room_tbl")
        roomlist= cur.fetchall()
        cur.execute("SELECT * FROM subject_tbl")
        subjectlist= cur.fetchall()
        cur.execute("SELECT * FROM grade_tbl")
        gradelist = cur.fetchall()
        cur.execute("SELECT * FROM strand_tbl")
        strandlist = cur.fetchall()
        cur.execute("SELECT * FROM section_tbl")
        sectionlist = cur.fetchall()

        return render_template('schedule.html',schedule=schedulelist,day=daylist,room=roomlist,subject=subjectlist,grade=gradelist,strand=strandlist,section=sectionlist,username=username,id=id)
    else:
        return redirect(url_for('teacher_login'))
@app.route('/insert_sched',methods=['POST','GET'])
def insert_sched():
    if "loggedinteacher" in session:
        today = date.today()
        if request.method == 'POST':
            day = request.form['day']
            room = request.form['room']
            start_time = (str(today)) + ' ' + request.form['start']
            end_time = (str(today)) + ' ' + request.form['end']
            subject = request.form['subject']
            grade = request.form['grade']
            strand = request.form['strand']
            section = request.form['section']
            school_year = request.form['school_year']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO schedule_tbl (day,room,time_start,time_end,subject,grade,strand,section,school_year) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(day,room,start_time.upper(),end_time.upper(),subject,grade,strand,section,school_year))
            mysql.connection.commit()
            return redirect(url_for('schedule'))
        else:
            return redirect(url_for('schedule'))
    else:
        return redirect(url_for('schedule'))



if __name__  == "__main__":
    app.run(debug=True)