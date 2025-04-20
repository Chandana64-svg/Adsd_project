from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

# Initialize the database
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    data = (
        request.form['name'],
        request.form['email'],
        request.form['service'],
        request.form['date'],
        request.form['time']
    )
    with sqlite3.connect('appointments.db') as conn:
        conn.execute('INSERT INTO appointments (name, email, service, date, time) VALUES (?, ?, ?, ?, ?)', data)

    flash('✅ Appointment booked successfully!')
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
