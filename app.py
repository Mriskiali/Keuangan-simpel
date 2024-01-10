from flask import Flask, render_template, request, redirect, url_for
import os
import locale
import json

app = Flask(__name__)
locale.setlocale(locale.LC_ALL, 'id_ID')

# Load data from file on application startup
records = []
saldo_awal = 0

def save_data_to_file():
    data = {'records': records, 'saldo_awal': saldo_awal}
    with open('data.json', 'w') as file:
        json.dump(data, file)

def load_data_from_file():
    global records, saldo_awal
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            records = data.get('records', [])
            saldo_awal = data.get('saldo_awal', 0)
    except FileNotFoundError:
        pass

load_data_from_file()

# Define the CRON_SECRET from the environment variable
cron_secret = os.environ.get('CRON_SECRET')

@app.route('/')
def index():
    return render_template('index.html', records=records, saldo_awal=saldo_awal)

@app.route('/set_saldo_awal', methods=['POST'])
def set_saldo_awal():
    global saldo_awal
    saldo_awal = float(request.form.get('saldo_awal'))
    save_data_to_file()
    return redirect(url_for('index'))

@app.route('/tambah_catatan', methods=['POST'])
def tambah_catatan():
    global saldo_awal
    keterangan = request.form.get('keterangan')
    jumlah = float(request.form.get('jumlah'))

    saldo_awal -= jumlah

    catatan = {'keterangan': keterangan, 'jumlah': jumlah}
    records.append(catatan)
    save_data_to_file()
    return redirect(url_for('index'))

@app.route('/hapus_catatan/<int:index>', methods=['GET'])
def hapus_catatan(index):
    if 0 <= index < len(records):
        global saldo_awal
        catatan_terhapus = records.pop(index)
        saldo_awal += catatan_terhapus['jumlah']
        save_data_to_file()
        return redirect(url_for('index'))
    else:
        return "Indeks tidak valid"

# Endpoint for cron job with security check
@app.route('/api/cron', methods=['POST'])
def cron_job():
    # Check Authorization header for the correct CRON_SECRET
    if request.headers.get('Authorization') != f'Bearer {cron_secret}':
        return "Unauthorized", 401  # Return 401 Unauthorized if the secret is incorrect
    else:
        # Perform cron job logic here
        # For example, you can call the functions you want to execute periodically
        return "Cron Job Executed Successfully"

if __name__ == '__main__':
    app.run(debug=True)
