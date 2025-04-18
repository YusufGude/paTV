from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "PineAppleTV"

# Veritabanı bağlantısı
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'db', 'user.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# "/" adresi login sayfasına yönlendirilsin
@app.route('/')
def redirect_to_main():
    return redirect(url_for('login'))

# Ana sayfa - Artık "/main_page" URL'sinde
@app.route('/main_page')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Kullanıcı girişi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            flash('Giriş başarılı!', 'success')
            session['user'] = username
            return redirect(url_for('index'))  # Bu 'index', yukarıdaki '/main_page' ile eşleşiyor
        else:
            flash('Hatalı kullanıcı adı veya şifre.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Kullanıcı kaydı
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            flash('Bu kullanıcı adı zaten alınmış.', 'error')
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Çıkış işlemi
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Çıkış başarılı.', 'info')
    return redirect(url_for('login'))

# Videoları kategoriye göre listeleme
@app.route('/videos/<category>')
def videos(category):
    if 'user' not in session:
        return redirect(url_for('login'))

    if category == 'diziler':
        video_path = 'static/videos/diziler'
    elif category == 'filmler':
        video_path = 'static/videos/filmler'
    else:
        flash('Geçersiz kategori.', 'error')
        return redirect(url_for('index'))

    try:
        # Videoları sadece mp4 dosyalarıyla filtrele
        videos = [f for f in os.listdir(video_path) if f.endswith('.mp4')]
    except FileNotFoundError:
        videos = []

    return render_template('videos.html', category=category, videos=videos)


# Video izleme sayfası
@app.route('/video/<name>')
def video(name):
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('video.html', video_name=name)

# Videoları akışa sunma
@app.route('/videos/stream/<path:filename>')
def stream_video(filename):
    video_folder = os.path.join('static', 'videos')
    return send_from_directory(video_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)