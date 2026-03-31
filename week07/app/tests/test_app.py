import os
import pytest
from datetime import date

# Point to SQLite before any app code is imported
os.environ.setdefault("DB_LINK", "sqlite:///:memory:")

from app import create_app, db
from app.models.models import User, Student, Attendance


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["WTF_CSRF_ENABLED"] = False

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client, app):
    """A test client that is already logged in as an instructor."""
    with app.app_context():
        user = User(username="instructor", email="instructor@test.com")
        user.set_password("Pass1234")
        db.session.add(user)
        db.session.commit()

    client.post("/login", data={"username": "instructor", "password": "Pass1234"})
    return client


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _add_student_with_attendance(app, name, present, absent):
    """Insert a student with a given number of present/absent records."""
    with app.app_context():
        student = Student(name=name)
        db.session.add(student)
        db.session.flush()
        for i in range(present):
            db.session.add(Attendance(student_id=student.id,
                                      date=date(2024, 1, i + 1), status="Present"))
        for i in range(absent):
            db.session.add(Attendance(student_id=student.id,
                                      date=date(2024, 2, i + 1), status="Absent"))
        db.session.commit()
        return student.id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_unauthenticated_redirects_to_login(client):
    """Unauthenticated requests to protected routes redirect to /login."""
    for path in ["/", "/students", "/attendance"]:
        resp = client.get(path)
        assert resp.status_code in (301, 302), f"{path} should redirect"
        assert "login" in resp.headers["Location"]


def test_dashboard_renders(auth_client):
    """Logged-in dashboard returns 200 and shows the three stat cards."""
    resp = auth_client.get("/")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "Total Students" in body
    assert "Attendance Rate" in body
    assert "At-Risk Students" in body


def test_students_page_has_export_and_report_links(auth_client, app):
    """Students page shows Export CSV button and View Report link."""
    _add_student_with_attendance(app, "Alice", present=3, absent=1)

    resp = auth_client.get("/students")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "Export CSV" in body
    assert "View Report" in body
    assert "/export/attendance" in body


def test_student_report_shows_correct_stats(auth_client, app):
    """Student report page calculates present/absent/rate correctly."""
    sid = _add_student_with_attendance(app, "Bob", present=3, absent=1)

    resp = auth_client.get(f"/student/{sid}")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "Bob" in body
    assert "75.0%" in body   # 3/4 = 75 %
    # 3 present, 1 absent visible in the history table
    assert body.count("Present") >= 3
    assert "Absent" in body


def test_export_csv_content(auth_client, app):
    """Export endpoint streams a valid CSV with student attendance rows."""
    _add_student_with_attendance(app, "Carol", present=2, absent=1)

    resp = auth_client.get("/export/attendance")
    assert resp.status_code == 200
    assert "text/csv" in resp.content_type
    assert "attachment" in resp.headers.get("Content-Disposition", "")

    lines = resp.data.decode().strip().splitlines()
    assert lines[0] == "Student ID,Student Name,Date,Status"
    # 3 attendance rows for Carol
    data_rows = [l for l in lines[1:] if "Carol" in l]
    assert len(data_rows) == 3


def test_at_risk_student_appears_on_dashboard(auth_client, app):
    """A student below 75 % attendance shows in the At-Risk section."""
    _add_student_with_attendance(app, "Dave", present=1, absent=3)  # 25 %

    resp = auth_client.get("/")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "Dave" in body
    assert "25.0%" in body
