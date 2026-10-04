from flask import Flask, request, render_template_string
import requests
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os

app = Flask(__name__)

# CLASS WIFI PUBLIC IP
REQUIRED_IP = "49.207.212.5"

EXCEL_FILE = "attendance.xlsx"

# CREATE EXCEL FILE IF NOT EXISTS
if not os.path.exists(EXCEL_FILE):

    wb = Workbook()
    ws = wb.active

    ws.title = "Attendance"

    ws.append(["Name", "Roll No", "Time"])

    wb.save(EXCEL_FILE)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Attendance Portal</title>

    <style>

        body{
            background:#111;
            color:white;
            font-family:Arial;
            text-align:center;
            padding-top:60px;
        }

        .box{
            width:400px;
            margin:auto;
            background:#222;
            padding:30px;
            border-radius:15px;
        }

        input{
            width:90%;
            padding:12px;
            margin:10px;
            border:none;
            border-radius:8px;
            font-size:16px;
        }

        button{
            padding:12px 25px;
            border:none;
            border-radius:8px;
            background:limegreen;
            color:white;
            font-size:16px;
            cursor:pointer;
        }

        .error{
            color:red;
            font-size:24px;
            font-weight:bold;
        }

        .success{
            color:lime;
            font-size:24px;
            font-weight:bold;
        }

    </style>

</head>
<body>

<div class="box">

    <h1>Class Attendance</h1>

    <p><b>Current IP:</b> {{ current_ip }}</p>
    <p><b>Class IP:</b> {{ required_ip }}</p>

    {% if same %}

        <div class="success">Connected To Class WiFi</div>

        <form method="POST" action="/submit">

            <input type="text" name="name" placeholder="Enter Name" required>

            <input type="text" name="rollno" placeholder="Enter Roll Number" required>

            <br><br>

            <button type="submit">Submit Attendance</button>

        </form>

    {% else %}

        <div class="error">
            Please connect to class WiFi
        </div>

    {% endif %}

</div>

</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Attendance Submitted</title>
</head>

<body style="background:#111;color:white;font-family:Arial;text-align:center;padding-top:100px;">

    <h1 style="color:lime;">Attendance Submitted</h1>

    <h2>Name: {{ name }}</h2>

    <h2>Roll No: {{ rollno }}</h2>

    <h3>Time: {{ time }}</h3>

</body>
</html>
"""

ERROR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>

<body style="background:#111;color:white;font-family:Arial;text-align:center;padding-top:100px;">

    <h1 style="color:red;">{{ message }}</h1>

</body>
</html>
"""

@app.route('/')
def home():

    # GET CURRENT PUBLIC IP
    current_ip = requests.get("https://api.ipify.org").text

    # CHECK IP
    same = current_ip == REQUIRED_IP

    return render_template_string(
        HTML,
        current_ip=current_ip,
        required_ip=REQUIRED_IP,
        same=same
    )

@app.route('/submit', methods=['POST'])
def submit():

    # RECHECK WIFI IP
    current_ip = requests.get("https://api.ipify.org").text

    if current_ip != REQUIRED_IP:

        return render_template_string(
            ERROR_HTML,
            message="Not Connected To Class WiFi"
        )

    name = request.form['name']
    rollno = request.form['rollno']

    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # LOAD EXCEL
    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    # CHECK DUPLICATE ROLL NUMBER
    for row in ws.iter_rows(min_row=2, values_only=True):

        saved_roll = str(row[1])

        if saved_roll == rollno:

            return render_template_string(
                ERROR_HTML,
                message="Attendance Already Submitted"
            )

    # SAVE DATA
    ws.append([name, rollno, current_time])

    wb.save(EXCEL_FILE)

    return render_template_string(
        SUCCESS_HTML,
        name=name,
        rollno=rollno,
        time=current_time
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=55000, debug=True)