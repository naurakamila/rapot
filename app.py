from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_mysqldb import MySQL
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# Konfigurasi database
app.config['SECRET_KEY'] = 'a3efc5b1c8ca743c92eac40b4eae8bf19bae99bba4238468'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Yondaktaukoktanyasaya_07'
app.config['MYSQL_DB'] = 'rapot'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Lakukan validasi data yang diterima
        if username and password and role:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))  # Ganti 'login' dengan rute login Anda
        else:
            error = 'Mohon isi semua field'
            return render_template('signup.html', error=error)

    return render_template('signup.html')


@app.route('/')
def form():
    return render_template('form.html')



@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        nama = request.form['nama']
        nilai_uh = float(request.form['nilai_uh'])
        nilai_uts = float(request.form['nilai_uts'])
        nilai_uas = float(request.form['nilai_uas'])
        nilai_akhir = (0.1 * nilai_uh) + (0.3 * nilai_uts) + (0.6 * nilai_uas)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO nilai_siswa (nama, nilai_uh, nilai_uts, nilai_uas, nilai_akhir) VALUES (%s, %s, %s, %s, %s)",
                    (nama, nilai_uh, nilai_uts, nilai_uas, nilai_akhir))
        mysql.connection.commit()
        cur.close()

        return redirect('/data')

@app.route('/data')
def data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM nilai_siswa")
    rows = cur.fetchall()
    cur.close()

    return render_template('index.html', rows=rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and password == user['password']:
            # Jika login berhasil, atur sesi dan arahkan ke halaman dashboard atau halaman lain yang diinginkan
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('data'))  # Ganti 'dashboard' dengan rute halaman dashboard Anda
        else:
            error = 'Username atau password salah'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/export_pdf', methods=['GET'])
def export_pdf():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM nilai_siswa")
    rows = cur.fetchall()
    cur.close()

    # Membuat PDF dengan menggunakan ReportLab
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
    elements = []

    # Menyiapkan data untuk tabel
    data = [['ID', 'Nama', 'Nilai UH', 'Nilai UTS', 'Nilai UAS', 'Nilai Akhir']]
    for row in rows:
        data.append([str(row['id']), row['nama'], str(row['nilai_uh']), str(row['nilai_uts']), str(row['nilai_uas']), str(row['nilai_akhir'])])

    # Menambahkan judul
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title = Paragraph("Data Nilai Siswa", title_style)
    elements.append(title)
    elements.append(Paragraph("<br/><br/>", title_style))  # Spasi setelah judul

    # Membuat tabel
    table = Table(data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    elements.append(table)

    # Membuat PDF dengan tabel
    pdf.build(elements)

    buffer.seek(0)

    # Membuat respons PDF untuk diunduh
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=nilai_rapot_siswa.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)
