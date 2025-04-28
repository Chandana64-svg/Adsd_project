from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Mail configuration (example: Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # <-- your email
app.config['MAIL_PASSWORD'] = 'your_app_password'     # <-- your app password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

# Initialize DB
def init_db():
    with sqlite3.connect('appointments.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            );
        ''')
init_db()

# Function to import data from CSV to SQLite
def import_csv_to_db():
    with open('patients_dataset.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        
        with sqlite3.connect('appointments.db') as conn:
            for row in csv_reader:
                name, email, service, date, time = row
                conn.execute('''
                    INSERT INTO appointments (name, email, service, date, time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, email, doctor, date, time))

# Import the CSV data into the database (you can call this once or trigger it as needed)
import_csv_to_db()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    email = request.form['email']
    service = request.form['service']
    date = request.form['date']
    time = request.form['time']

    with sqlite3.connect('appointments.db') as conn:
        conn.execute('INSERT INTO appointments (name, email, service, date, time) VALUES (?, ?, ?, ?, ?)',
                     (name, email, service, date, time))

    # Send email confirmation
    msg = Message("Appointment Confirmation", recipients=[email])
    msg.body = f"Hello {name},\n\nYour appointment for '{service}' has been successfully booked on {date} at {time}.\n\nThank you!"
    mail.send(msg)

    flash('✅ Appointment booked successfully! A confirmation email has been sent.')
    return redirect(url_for('appointments'))

@app.route('/appointments')
def appointments():
    with sqlite3.connect('appointments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments')
        data = cursor.fetchall()
    return render_template('appointments.html', appointments=data)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        updated = (
            request.form['name'],
            request.form['email'],
            request.form['service'],
            request.form['date'],
            request.form['time'],
            id
        )
        with sqlite3.connect('appointments.db') as conn:
            conn.execute('''
                UPDATE appointments 
                SET name=?, email=?, service=?, date=?, time=? 
                WHERE id=?
            ''', updated)
        flash('✏️ Appointment updated successfully!')
        return redirect(url_for('appointments'))

    with sqlite3.connect('appointments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE id=?', (id,))
        appointment = cursor.fetchone()
    return render_template('edit.html', appointment=appointment)

@app.route('/delete/<int:id>')
def delete(id):
    with sqlite3.connect('appointments.db') as conn:
        conn.execute('DELETE FROM appointments WHERE id=?', (id,))
    flash('🗑️ Appointment deleted successfully!')
    return redirect(url_for('appointments'))

if __name__ == '__main__':
    app.run(debug=True)
