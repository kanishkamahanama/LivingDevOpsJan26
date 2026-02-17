from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# PostgreSQL configuration using individual environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'students_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_SSL_MODE = os.environ.get('DB_SSL_MODE', 'prefer')  # Options: disable, allow, prefer, require, verify-ca, verify-full

# Construct database URL with SSL support
# For AWS RDS, SSL is typically required
if DB_SSL_MODE and DB_SSL_MODE != 'disable':
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSL_MODE}'
else:
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'sslmode': DB_SSL_MODE
    }
}

db = SQLAlchemy(app)

# Student model
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Student {self.name}>'

# Create tables before first request
def init_db():
    """Initialize database tables with retries"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Create tables - assume database already exists
            db.create_all()
            print(f"✓ Database tables created successfully (attempt {attempt + 1})")
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database initialization attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"✗ Failed to initialize database after {max_retries} attempts")
                print(f"Error: {e}")
                print("\nTroubleshooting:")
                print("  1. Ensure RDS security group allows EC2 on port 5432")
                print("  2. Verify database exists and credentials are correct")
                print("  3. Run: ./test_connection.sh")
                return False
    return False

# Initialize database when app starts
with app.app_context():
    init_db()

HOME_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kanishka Mahanama</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* --- Animated gradient background --- */
        body::before {
            content: '';
            position: fixed;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 20% 50%, rgba(56,189,248,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(139,92,246,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 50% 80%, rgba(16,185,129,0.06) 0%, transparent 50%);
            animation: bgShift 12s ease-in-out infinite alternate;
            z-index: -1;
        }
        @keyframes bgShift {
            0%   { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(30px, -20px) rotate(3deg); }
        }

        /* --- Fade-up animation --- */
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .fade-up {
            opacity: 0;
            animation: fadeUp 0.7s ease-out forwards;
        }

        /* Navigation */
        nav {
            background: #1e293b;
            border-bottom: 1px solid #334155;
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        nav .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            gap: 24px;
            align-items: center;
        }
        nav a {
            color: #94a3b8;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        nav a:hover, nav a.active {
            color: #38bdf8;
        }

        .container { max-width: 800px; margin: 0 auto; padding: 60px 24px; }

        .header { text-align: center; margin-bottom: 48px; }
        .header h1 {
            font-size: 2.5rem; color: #f8fafc; margin-bottom: 8px;
        }
        .header .tagline {
            font-size: 1.1rem; color: #94a3b8; margin-bottom: 16px;
        }
        .header .social a {
            color: #38bdf8; text-decoration: none;
            transition: color 0.3s, text-shadow 0.3s;
        }
        .header .social a:hover {
            color: #7dd3fc;
            text-shadow: 0 0 10px rgba(56,189,248,0.5);
        }

        .section {
            background: #1e293b; border-radius: 12px;
            padding: 32px; margin-bottom: 24px;
            border: 1px solid transparent;
            transition: border-color 0.4s, box-shadow 0.4s, transform 0.3s;
        }
        .section:hover {
            border-color: rgba(56,189,248,0.3);
            box-shadow: 0 0 24px rgba(56,189,248,0.1);
            transform: translateY(-4px);
        }
        .section h2 {
            font-size: 1.3rem; color: #38bdf8; margin-bottom: 16px;
            border-bottom: 2px solid #334155; padding-bottom: 8px;
        }
        .section p { line-height: 1.7; color: #cbd5e1; }

        .skills-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 12px;
        }

        /* --- Skill tag pop-in --- */
        @keyframes popIn {
            from { opacity: 0; transform: scale(0.7); }
            to   { opacity: 1; transform: scale(1); }
        }
        .skill-tag {
            background: #334155; padding: 10px 16px; border-radius: 8px;
            text-align: center; font-size: 0.95rem; color: #e2e8f0;
            opacity: 0;
            animation: popIn 0.4s ease-out forwards;
            transition: background 0.3s, transform 0.2s, box-shadow 0.3s;
            cursor: default;
        }
        .skill-tag:nth-child(1) { animation-delay: 0.8s; }
        .skill-tag:nth-child(2) { animation-delay: 0.9s; }
        .skill-tag:nth-child(3) { animation-delay: 1.0s; }
        .skill-tag:nth-child(4) { animation-delay: 1.1s; }
        .skill-tag:nth-child(5) { animation-delay: 1.2s; }
        .skill-tag:nth-child(6) { animation-delay: 1.3s; }
        .skill-tag:nth-child(7) { animation-delay: 1.4s; }
        .skill-tag:nth-child(8) { animation-delay: 1.5s; }
        .skill-tag:hover {
            background: #38bdf8;
            color: #0f172a;
            transform: scale(1.08);
            box-shadow: 0 0 16px rgba(56,189,248,0.4);
        }

        footer {
            text-align: center; padding: 32px 0; color: #475569; font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="active">Home</a>
            <a href="/students">Students</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="header">
            <h1>Kanishka Mahanama</h1>
            <p class="tagline">Senior IT Professional | Network Engineer | DevOps Enthusiast</p>
            <p class="social">
                <a href="https://x.com/__kanishka__" target="_blank">@__kanishka__</a>
            </p>
        </div>
        <div class="section">
            <h2>About Me</h2>
            <p>
                Senior IT Professional with over 15 years of experience in the industry.
                Skilled in networks, security, and automation, with a proven track record
                of delivering strategic outcomes for clients. Strong stakeholder engagement
                and recognized as a trusted advisor. Currently leveraging deep networking
                expertise to transition into a DevOps role with a focus on automation and
                cloud-native practices.
            </p>
        </div>
        <div class="section">
            <h2>Networking Background</h2>
            <p>
                With extensive hands-on experience as a network engineer, I have designed,
                deployed, and managed enterprise-grade network infrastructures including
                routing &amp; switching, firewalls, VPNs, and load balancers. Proficient in
                troubleshooting complex network issues across LAN, WAN, and data centre
                environments. This deep networking foundation drives my approach to
                infrastructure-as-code, cloud networking, and building reliable automated
                pipelines.
            </p>
        </div>
        <div class="section">
            <h2>Skills</h2>
            <div class="skills-grid">
                <div class="skill-tag">Azure</div>
                <div class="skill-tag">Terraform</div>
                <div class="skill-tag">Red Hat Linux</div>
                <div class="skill-tag">Cisco</div>
                <div class="skill-tag">Routing &amp; Switching</div>
                <div class="skill-tag">Firewalls &amp; VPN</div>
                <div class="skill-tag">Network Security</div>
                <div class="skill-tag">Automation</div>
            </div>
        </div>
        <footer>&copy; 2026 Kanishka Mahanama</footer>
    </div>

</body>
</html>"""

STUDENTS_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Students - Kanishka Mahanama</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 20% 50%, rgba(56,189,248,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(139,92,246,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 50% 80%, rgba(16,185,129,0.06) 0%, transparent 50%);
            animation: bgShift 12s ease-in-out infinite alternate;
            z-index: -1;
        }
        @keyframes bgShift {
            0%   { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(30px, -20px) rotate(3deg); }
        }

        nav {
            background: #1e293b;
            border-bottom: 1px solid #334155;
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        nav .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            gap: 24px;
            align-items: center;
        }
        nav a {
            color: #94a3b8;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        nav a:hover, nav a.active {
            color: #38bdf8;
        }

        .container { max-width: 800px; margin: 0 auto; padding: 60px 24px; }

        .header { text-align: center; margin-bottom: 48px; }
        .header h1 {
            font-size: 2.5rem; color: #f8fafc; margin-bottom: 8px;
        }

        .section {
            background: #1e293b; border-radius: 12px;
            padding: 32px; margin-bottom: 24px;
            border: 1px solid rgba(56,189,248,0.2);
        }
        .section h2 {
            font-size: 1.3rem; color: #38bdf8; margin-bottom: 16px;
            border-bottom: 2px solid #334155; padding-bottom: 8px;
        }

        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #cbd5e1;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #e2e8f0;
            font-size: 1rem;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #38bdf8;
            box-shadow: 0 0 0 3px rgba(56,189,248,0.1);
        }

        .btn {
            background: #38bdf8;
            color: #0f172a;
            padding: 12px 32px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s, box-shadow 0.3s;
        }
        .btn:hover {
            background: #7dd3fc;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(56,189,248,0.3);
        }

        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: rgba(16,185,129,0.1);
            border: 1px solid rgba(16,185,129,0.3);
            color: #10b981;
        }
        .alert-error {
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            color: #ef4444;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #334155;
            padding: 12px;
            text-align: left;
            color: #38bdf8;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #334155;
        }
        tr:hover {
            background: rgba(56,189,248,0.05);
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="/">Home</a>
            <a href="/students" class="active">Students</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="header">
            <h1>Student Registration</h1>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="section">
            <h2>Register New Student</h2>
            <form method="POST" action="{{ url_for('students') }}">
                <div class="form-group">
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <button type="submit" class="btn">Submit</button>
            </form>
        </div>

        <div class="section">
            <h2>Registered Students</h2>
            {% if students %}
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Registered</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for student in students %}
                        <tr>
                            <td>{{ student.id }}</td>
                            <td>{{ student.name }}</td>
                            <td>{{ student.email }}</td>
                            <td>{{ student.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="empty-state">
                    <p>No students registered yet. Be the first to register!</p>
                </div>
            {% endif %}
        </div>
    </div>

</body>
</html>"""


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/students", methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('students'))
        
        # Check if email already exists
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash('A student with this email is already registered!', 'error')
            return redirect(url_for('students'))
        
        try:
            new_student = Student(name=name, email=email)
            db.session.add(new_student)
            db.session.commit()
            flash('Student registered successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering student: {str(e)}', 'error')
        
        return redirect(url_for('students'))
    
    # GET request - display form and list
    students_list = Student.query.order_by(Student.created_at.desc()).all()
    return render_template_string(STUDENTS_PAGE, students=students_list)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)