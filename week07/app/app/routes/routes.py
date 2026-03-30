import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app.models.models import Student, Attendance, db, Class
from datetime import datetime, date

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def dashboard():
    today = date.today()

    # Get total students
    total_students = Student.query.count()

    # Get today's attendance
    today_attendance = Attendance.query.filter_by(date=today, status="Present").count()

    # Calculate total attendance rate
    total_marked_days = Attendance.query.distinct(Attendance.date).count()
    total_present = Attendance.query.filter_by(status="Present").count()
    total_records = Attendance.query.count()

    attendance_rate = round(
        (total_present / total_records * 100) if total_records > 0 else 0, 1
    )

    at_risk = []
    for student in Student.query.all():
        total_days = Attendance.query.filter_by(student_id=student.id).count()
        if total_days > 0:
            present_days = Attendance.query.filter_by(student_id=student.id, status="Present").count()
            rate = round(present_days / total_days * 100, 1)
            if rate < 75:
                at_risk.append({"student": student, "rate": rate})

    return render_template(
        "dashboard.html",
        total_students=total_students,
        today_attendance=f"{today_attendance}/{total_students}",
        attendance_rate=attendance_rate,
        at_risk=at_risk,
    )


@bp.route("/students")
@login_required
def students():
    students = Student.query.all()
    for student in students:
        total_days = Attendance.query.filter_by(student_id=student.id).count()
        if total_days > 0:
            present_days = Attendance.query.filter_by(
                student_id=student.id, status="Present"
            ).count()
            student.attendance_rate = round(present_days / total_days * 100, 1)
        else:
            student.attendance_rate = 0
    return render_template("students.html", students=students)


@bp.route("/attendance")
@login_required
def attendance():
    selected_date = request.args.get("date", date.today().isoformat())
    students = Student.query.all()

    for student in students:
        student.today_attendance = Attendance.query.filter_by(
            student_id=student.id, date=selected_date
        ).first()

    return render_template(
        "attendance.html", students=students, selected_date=selected_date
    )


@bp.route("/add_student", methods=["POST"])
@login_required
def add_student():
    name = request.form.get("name")
    if name:
        student = Student(name=name)
        db.session.add(student)
        db.session.commit()
        flash("Student added successfully", "success")
    return redirect(url_for("main.students"))


@bp.route("/mark_attendance", methods=["POST"])
@login_required
def mark_attendance():
    try:
        attendance_date = request.form.get("date", date.today().isoformat())
        students = Student.query.all()

        for student in students:
            status = request.form.get(f"status_{student.id}")
            if status:
                # Update existing or create new attendance record
                attendance = Attendance.query.filter_by(
                    student_id=student.id, date=attendance_date
                ).first()

                if attendance:
                    attendance.status = status
                else:
                    attendance = Attendance(
                        student_id=student.id, date=attendance_date, status=status
                    )
                    db.session.add(attendance)

        db.session.commit()
        flash("Attendance marked successfully", "success")
        return redirect(url_for("main.attendance", date=attendance_date))
    except Exception as e:
        flash("Error marking attendance", "error")
        return redirect(url_for("main.attendance"))


@bp.route("/student/<int:id>")
@login_required
def student_report(id):
    student = Student.query.get_or_404(id)
    records = Attendance.query.filter_by(student_id=id).order_by(Attendance.date.desc()).all()
    total_days = len(records)
    present_days = sum(1 for r in records if r.status == "Present")
    absent_days = total_days - present_days
    rate = round(present_days / total_days * 100, 1) if total_days > 0 else 0
    return render_template(
        "student_report.html",
        student=student,
        records=records,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        rate=rate,
    )


@bp.route("/export/attendance")
@login_required
def export_attendance():
    students = Student.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Student Name", "Date", "Status"])
    for student in students:
        records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date).all()
        for record in records:
            writer.writerow([student.id, student.name, record.date, record.status])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance.csv"},
    )


@bp.route("/edit_student/<int:id>", methods=["POST"])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    student.name = data["name"]
    db.session.commit()
    return "", 204


@bp.route("/delete_student/<int:id>", methods=["POST"])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return "", 204


@bp.route("/classes")
@login_required
def classes():
    classes = Class.query.order_by(Class.date.desc()).all()
    return render_template("classes.html", classes=classes)


@bp.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    if request.method == "POST":
        try:
            new_class = Class(
                date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
                time=request.form["time"],
                session_link=request.form["session_link"],
                code_link=request.form["code_link"],
                recording_link=request.form["recording_link"],
                resource_link=request.form["resource_link"],
                remarks=request.form["remarks"],
                created_by=current_user.id,
            )
            db.session.add(new_class)
            db.session.commit()
            flash("Class added successfully!", "success")
            return redirect(url_for("main.classes"))
        except Exception as e:
            flash("Error adding class.", "error")
            return redirect(url_for("main.add_class"))
    return render_template("add_class.html")


@bp.route("/delete_class/<int:id>", methods=["POST"])
@login_required
def delete_class(id):
    class_obj = Class.query.get_or_404(id)
    db.session.delete(class_obj)
    db.session.commit()
    return "", 204


@bp.route("/edit_class/<int:id>", methods=["GET", "POST"])
@login_required
def edit_class(id):
    class_obj = Class.query.get_or_404(id)

    if request.method == "POST":
        try:
            class_obj.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
            class_obj.time = request.form["time"]
            class_obj.session_link = request.form["session_link"]
            class_obj.code_link = request.form["code_link"]
            class_obj.recording_link = request.form["recording_link"]
            class_obj.resource_link = request.form["resource_link"]
            class_obj.remarks = request.form["remarks"]

            db.session.commit()
            flash("Class updated successfully!", "success")
            return redirect(url_for("main.classes"))
        except Exception as e:
            flash("Error updating class.", "error")

    return render_template("edit_class.html", class_obj=class_obj)
