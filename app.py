from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'moaz_pro_max_secret'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin', 
    'database': 'SkillBridge_DB'
}

def get_db():
    return mysql.connector.connect(**db_config)

# ==========================================
# PUBLIC & STUDENT ROUTES
# ==========================================
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM STUDENT WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['student_id']
            session['role'] = 'student'
            session['name'] = user['name']
            
            # --- CHANGE 1: Gender bhi session mein save kiya ---
            session['gender'] = user['gender'] 
            # ---------------------------------------------------

            conn.close()
            return redirect(url_for('student_dashboard'))
        else:
            conn.close()
            flash('Student email not found!', 'danger')
    return render_template('login_student.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        major = request.form['major']
        grad_year = request.form['graduation_year']
        
        # --- CHANGE 2: Form se Gender liya ---
        gender = request.form['gender']
        # -------------------------------------

        conn = get_db()
        cursor = conn.cursor()
        try:
            # --- CHANGE 3: Query mein gender add kiya ---
            cursor.execute("INSERT INTO STUDENT (name, email, major, graduation_year, gender) VALUES (%s, %s, %s, %s, %s)", 
                           (name, email, major, grad_year, gender))
            conn.commit()
            flash('Registration Successful! Login Now.', 'success')
            return redirect(url_for('student_login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('student_login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    student_id = session['user_id']
    
    # 1. Fetch Student's Skills
    cursor.execute("""
        SELECT s.skill_name 
        FROM STUDENT_SKILL ss 
        JOIN SKILL s ON ss.skill_id = s.skill_id 
        WHERE ss.student_id = %s
    """, (student_id,))
    my_skills = cursor.fetchall()
    
    if not my_skills:
        conn.close()
        flash('Please select your skills first.', 'info')
        return redirect(url_for('manage_skills'))

    # 2. MATCHING INTERNSHIPS
    cursor.execute("""
        SELECT DISTINCT i.title, c.name as company, i.duration, i.role, i.internship_id
        FROM INTERNSHIP i 
        JOIN COMPANY c ON i.company_id = c.company_id
        JOIN STUDENT_SKILL ss ON ss.student_id = %s
        JOIN SKILL s ON ss.skill_id = s.skill_id
        WHERE i.title LIKE CONCAT('%', s.skill_name, '%') OR i.role LIKE CONCAT('%', s.skill_name, '%')
    """, (student_id,))
    internships = cursor.fetchall()

    # 3. MATCHING PROJECTS
    cursor.execute("""
        SELECT DISTINCT p.* FROM PROJECT p
        JOIN PROJECT_SKILL ps ON p.project_id = ps.project_id
        JOIN STUDENT_SKILL ss ON ps.skill_id = ss.skill_id
        WHERE ss.student_id = %s
    """, (student_id,))
    projects = cursor.fetchall()

    # 4. MATCHING COURSES
    cursor.execute("""
        SELECT DISTINCT c.* FROM COURSE c
        JOIN COURSE_SKILL cs ON c.course_id = cs.course_id
        JOIN STUDENT_SKILL ss ON cs.skill_id = ss.skill_id
        WHERE ss.student_id = %s
    """, (student_id,))
    courses = cursor.fetchall()

    # 5. Application Status
    cursor.execute("""
        SELECT i.title, c.name as company, sa.status 
        FROM STUDENT_APPLICATION sa
        JOIN INTERNSHIP i ON sa.internship_id = i.internship_id
        JOIN COMPANY c ON i.company_id = c.company_id
        WHERE sa.student_id = %s
    """, (student_id,))
    my_apps = cursor.fetchall()

    conn.close()
    return render_template('student_dashboard.html', 
                           student=session['name'], 
                           skills=my_skills, 
                           internships=internships, 
                           projects=projects,
                           applications=my_apps,
                           courses=courses)

@app.route('/student/skills', methods=['GET', 'POST'])
def manage_skills():
    if session.get('role') != 'student': return redirect(url_for('student_login'))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute("DELETE FROM STUDENT_SKILL WHERE student_id = %s", (session['user_id'],))
        for skill_id in request.form.getlist('skills'):
            cursor.execute("INSERT INTO STUDENT_SKILL (student_id, skill_id) VALUES (%s, %s)", (session['user_id'], skill_id))
        conn.commit()
        return redirect(url_for('student_dashboard'))
    cursor.execute("SELECT * FROM SKILL")
    all_skills = cursor.fetchall()
    cursor.execute("SELECT skill_id FROM STUDENT_SKILL WHERE student_id = %s", (session['user_id'],))
    my_ids = [row['skill_id'] for row in cursor.fetchall()]
    conn.close()
    return render_template('skills.html', all_skills=all_skills, my_ids=my_ids)

@app.route('/student/apply/<int:internship_id>')
def apply_internship(internship_id):
    if session.get('role') != 'student': return redirect(url_for('student_login'))
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM STUDENT_APPLICATION WHERE student_id=%s AND internship_id=%s", 
                       (session['user_id'], internship_id))
        if cursor.fetchone():
            flash('You have already applied for this internship!', 'warning')
        else:
            cursor.execute("INSERT INTO STUDENT_APPLICATION (student_id, internship_id, status) VALUES (%s, %s, 'Pending')", 
                           (session['user_id'], internship_id))
            conn.commit()
            flash('Application Submitted Successfully!', 'success')
    except Exception as e:
        flash(f'Error applying: {str(e)}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('student_dashboard'))


# ==========================================
# 3. ADMIN ROUTES
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '12345':
            session['role'] = 'admin'
            session['name'] = 'Administrator'
            return redirect(url_for('admin_dashboard'))
        flash('Invalid Credentials', 'danger')
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    
    active_tab = request.args.get('tab', 'companies') 

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM COMPANY")
    companies = cursor.fetchall()
    
    cursor.execute("SELECT i.*, c.name as company_name FROM INTERNSHIP i JOIN COMPANY c ON i.company_id = c.company_id")
    internships = cursor.fetchall()
    
    # 4. Fetch Projects (Updated to include Skill Name)
    cursor.execute("""
        SELECT p.*, s.skill_name 
        FROM PROJECT p
        JOIN PROJECT_SKILL ps ON p.project_id = ps.project_id
        JOIN SKILL s ON ps.skill_id = s.skill_id
    """)
    projects = cursor.fetchall()
    
    cursor.execute("SELECT * FROM SKILL")
    skills = cursor.fetchall()
    
    cursor.execute("SELECT * FROM STUDENT")
    students = cursor.fetchall()

    cursor.execute("""
        SELECT c.*, s.skill_name 
        FROM COURSE c 
        JOIN COURSE_SKILL cs ON c.course_id = cs.course_id 
        JOIN SKILL s ON cs.skill_id = s.skill_id
    """)
    courses = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                           companies=companies, 
                           internships=internships, 
                           projects=projects, 
                           skills=skills,
                           students=students,
                           courses=courses,
                           active_tab=active_tab)

# --- ADMIN ACTIONS ---

@app.route('/admin/add/company', methods=['POST'])
def add_company():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO COMPANY (name, industry, location) VALUES (%s, %s, %s)",
                   (request.form['name'], request.form['industry'], request.form['location']))
    conn.commit()
    conn.close()
    flash('Company Added!', 'success')
    return redirect(url_for('admin_dashboard', tab='internships'))

@app.route('/admin/add/internship', methods=['POST'])
def add_internship():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO INTERNSHIP (title, role, start_date, duration, company_id) VALUES (%s, %s, %s, %s, %s)", 
                   (request.form['title'], request.form['role'], request.form['start_date'], request.form['duration'], request.form['company_id']))
    conn.commit()
    conn.close()
    flash('Internship Added!', 'success')
    return redirect(url_for('admin_dashboard', tab='internships'))

@app.route('/admin/add/skill', methods=['POST'])
def add_skill():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO SKILL (skill_name, category) VALUES (%s, %s)",
                       (request.form['skill_name'], request.form['category']))
        conn.commit()
        flash('Skill Added!', 'success')
    except:
        flash('Error! Skill maybe exists.', 'danger')
    conn.close()
    return redirect(url_for('admin_dashboard', tab='projects'))

@app.route('/admin/add/project', methods=['POST'])
def add_project():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PROJECT (title, complexity_level, description) VALUES (%s, %s, %s)",
                   (request.form['title'], request.form['level'], request.form['desc']))
    project_id = cursor.lastrowid
    cursor.execute("INSERT INTO PROJECT_SKILL (project_id, skill_id) VALUES (%s, %s)", (project_id, request.form['skill_id']))
    conn.commit()
    conn.close()
    flash('Project Added!', 'success')
    return redirect(url_for('admin_dashboard', tab='projects'))

@app.route('/admin/add/student', methods=['POST'])
def add_student_admin():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    try:
        # --- CHANGE 4: Admin form se bhi gender liya ---
        gender = request.form['gender']
        # --- CHANGE 5: Query mein gender add kiya ---
        cursor.execute("INSERT INTO STUDENT (name, email, major, graduation_year, gender) VALUES (%s, %s, %s, %s, %s)",
                       (request.form['name'], request.form['email'], request.form['major'], request.form['grad_year'], gender))
        conn.commit()
        flash('Student Added Successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    conn.close()
    return redirect(url_for('admin_dashboard', tab='students'))

@app.route('/admin/add/course', methods=['POST'])
def add_course():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    title = request.form['title']
    provider = request.form['provider'] 
    duration = request.form['duration']
    link = request.form['link'] 
    skill_id = request.form['skill_id'] 
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO COURSE (title, provider, duration, link) VALUES (%s, %s, %s, %s)", 
                   (title, provider, duration, link))
    course_id = cursor.lastrowid 
    cursor.execute("INSERT INTO COURSE_SKILL (course_id, skill_id) VALUES (%s, %s)", (course_id, skill_id))
    conn.commit()
    conn.close()
    flash('Course added and linked successfully!', 'success')
    return redirect(url_for('admin_dashboard', tab='courses'))

@app.route('/admin/delete/course/<int:id>')
def delete_course(id):
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM COURSE_SKILL WHERE course_id = %s", (id,))
    cursor.execute("DELETE FROM COURSE WHERE course_id = %s", (id,))
    conn.commit()
    conn.close()
    flash('Course deleted!', 'warning')
    return redirect(url_for('admin_dashboard', tab='courses'))

@app.route('/admin/delete/<type>/<int:id>')
def delete_item(type, id):
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db()
    cursor = conn.cursor()
    
    redirect_tab = 'companies'
    
    if type == 'company':
        cursor.execute("DELETE FROM COMPANY WHERE company_id = %s", (id,))
        redirect_tab = 'companies'
    elif type == 'internship':
        cursor.execute("DELETE FROM INTERNSHIP WHERE internship_id = %s", (id,))
        redirect_tab = 'internships'
    elif type == 'project':
        cursor.execute("DELETE FROM PROJECT_SKILL WHERE project_id = %s", (id,))
        cursor.execute("DELETE FROM PROJECT WHERE project_id = %s", (id,))
        redirect_tab = 'projects'
    elif type == 'skill':
        cursor.execute("DELETE FROM SKILL WHERE skill_id = %s", (id,))
        redirect_tab = 'skills'
    elif type == 'student':
        cursor.execute("DELETE FROM STUDENT WHERE student_id = %s", (id,))
        redirect_tab = 'students'
        
    conn.commit()
    conn.close()
    flash('Item Deleted!', 'warning')
    return redirect(url_for('admin_dashboard', tab=redirect_tab))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)