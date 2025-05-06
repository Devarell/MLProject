import flask
from flask import Flask, request, render_template, jsonify # Tambahkan render_template
import joblib
import numpy as np
import pandas as pd
import traceback # Untuk logging error detail

app = Flask(__name__) # Nama folder 'templates' dan 'static' otomatis dikenali

# --- Konfigurasi ---
MODEL_FILE_PATH = 'rf_original.pkl' # Pastikan file ini ada di folder yang sama

# --- Muat Model (Hanya sekali saat aplikasi dimulai) ---
try:
    model = joblib.load(MODEL_FILE_PATH)
    print(f"* Model '{MODEL_FILE_PATH}' berhasil dimuat.")
    # Jika model Anda dilatih dengan nama fitur tertentu, simpan nama fiturnya
    # Coba dapatkan dari model jika memungkinkan (tergantung cara disimpan)
    # Atau definisikan manual berdasarkan training Anda
    # model_feature_names = model.feature_names_in_ # Contoh jika tersedia
    model_feature_names = [ # **GANTI DENGAN URUTAN FITUR SAAT TRAINING MODEL ANDA**
         'hoursStudied', 'previousScore', 'attendance', 'totalSessions',
         'tutoringSessions', 'internetAccess', 'extracurricular',
         'peerInfluence', 'resourceAccess', 'teacherQuality', 'distanceHome',
         'mataPelajaran_encoded' # Contoh jika mapel di-encode
         # ... tambahkan semua fitur sesuai urutan training ...
     ]
    print(f"* Diharapkan fitur model: {model_feature_names}")

except FileNotFoundError:
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"!! ERROR: File model '{MODEL_FILE_PATH}' tidak ditemukan.")
    print(f"!! Pastikan file tersebut ada di folder yang sama dengan app.py")
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    model = None
    model_feature_names = []
except Exception as e:
    print(f"!! ERROR saat memuat model: {e}")
    model = None
    model_feature_names = []


# --- Route untuk menampilkan halaman form prediksi ---
@app.route('/')
def halaman_prediksi():
    # Menyajikan file HTML dari folder 'templates'
    return render_template('prediction.html')

# --- Route untuk memproses data dan menampilkan hasil ---
@app.route('/proses-prediksi', methods=['POST'])
def proses_prediksi():
    if model is None:
        # Jika model gagal dimuat, tampilkan pesan error di halaman hasil
        return render_template('hasil_prediksi.html', error="Model prediksi tidak tersedia. Hubungi administrator.")

    if request.method == 'POST':
        try:
            # 1. Ambil data dari form
            form_data = request.form
            print("* Menerima data form:", form_data.to_dict())

            # 2. Preprocessing Input - **SESUAIKAN BAGIAN INI DENGAN SANGAT HATI-HATI**
            #    Harus sama persis dengan preprocessing saat training rf_original.pkl

            input_features = {} # Dictionary untuk menampung fitur yang sudah diproses

            # Contoh mapping (sesuaikan nilai 0, 1, 2 dengan training Anda)
            internet_map = {'yes': 1, 'no': 0}
            extracurricular_map = {'yes': 1, 'no': 0}
            peer_influence_map = {'low': 0, 'medium': 1, 'high': 2}
            resource_access_map = {'low': 0, 'medium': 1, 'high': 2}
            teacher_quality_map = {'low': 0, 'medium': 1, 'high': 2}
            distance_map = {'near': 0, 'moderate': 1, 'far': 2}
            # Contoh mapping mapel (ANDA PERLU MENYESUAIKAN INI!)
            # Mungkin Anda menggunakan One-Hot Encoding atau Label Encoding saat training?
            # Jika Label Encoding:
            mapel_map = {'matematika': 0, 'fisika': 1, 'kimia': 2, 'biologi': 3} # Contoh! Ganti!

            # Konversi dan Mapping
            input_features['internetAccess'] = internet_map.get(form_data.get('internetAccess', 'no'))
            input_features['extracurricular'] = extracurricular_map.get(form_data.get('extracurricular', 'no'))
            input_features['peerInfluence'] = peer_influence_map.get(form_data.get('peerInfluence', 'medium'))
            input_features['resourceAccess'] = resource_access_map.get(form_data.get('resourceAccess', 'medium'))
            input_features['teacherQuality'] = teacher_quality_map.get(form_data.get('teacherQuality', 'medium'))
            input_features['distanceHome'] = distance_map.get(form_data.get('distanceHome', 'moderate'))

            # Fitur Numerik
            input_features['hoursStudied'] = float(form_data.get('hoursStudied', 0))
            input_features['previousScore'] = float(form_data.get('previousScore', 50))
            input_features['attendance'] = float(form_data.get('attendance', 0))
            # Hindari pembagian dengan nol
            total_sessions = float(form_data.get('totalSessions', 1))
            input_features['totalSessions'] = total_sessions if total_sessions > 0 else 1
            input_features['tutoringSessions'] = float(form_data.get('tutoringSessions', 0))

            # Preprocessing Mata Pelajaran (Contoh Label Encoding)
            mapel_input = form_data.get('mataPelajaran', '').lower().strip()
            # Gunakan nilai default jika mapel tidak dikenal (misal -1 atau nilai 'lainnya')
            input_features['mataPelajaran_encoded'] = mapel_map.get(mapel_input, -1) # Contoh!

            # Jika Anda membuat fitur baru seperti persentase kehadiran saat training:
            # if input_features['totalSessions'] > 0:
            #    input_features['attendance_percentage'] = (input_features['attendance'] / input_features['totalSessions']) * 100
            # else:
            #    input_features['attendance_percentage'] = 0
            # (Jangan lupa hapus fitur asli jika perlu dan sesuaikan model_feature_names)


            # 3. Siapkan data untuk model (pastikan urutan SAMA dengan training)
            # Buat DataFrame untuk memastikan urutan kolom
            input_df = pd.DataFrame([input_features])
             # Riindex sesuai urutan fitur model, isi nilai default jika ada yg hilang
            input_df = input_df.reindex(columns=model_feature_names, fill_value=0) # Hati-hati dengan fill_value=0

            print("* Data siap untuk model:\n", input_df)
            input_array = input_df.to_numpy() # Konversi ke NumPy array

            # (OPSIONAL) Jika Anda menggunakan Scaler saat training
            # scaler = joblib.load('scaler.pkl') # Muat scaler jika perlu
            # input_array = scaler.transform(input_array)
            # print("* Data setelah scaling:", input_array)


            # 4. Lakukan Prediksi
            prediction = model.predict(input_array)
            predicted_score = round(float(prediction[0]), 1) # Ambil hasil & bulatkan
            predicted_score = max(0, min(100, predicted_score)) # Batasi 0-100
            print(f"* Prediksi Skor: {predicted_score}")


            # 5. Tentukan Assessment dan Saran
            assessment = ''
            suggestion = ''
            if predicted_score >= 90: assessment = "Sangat Baik"; suggestion = "Luar biasa! Pertahankan..."
            elif predicted_score >= 80: assessment = "Baik"; suggestion = "Hasil yang solid! Identifikasi..."
            elif predicted_score >= 70: assessment = "Cukup Baik"; suggestion = "Sudah di jalur yang benar..."
            elif predicted_score >= 60: assessment = "Cukup"; suggestion = "Masih ada ruang..."
            else: assessment = "Perlu Peningkatan"; suggestion = "Jangan khawatir! Ini kesempatan..."


            # 6. Render Template Hasil dengan Data Prediksi
            return render_template(
                'hasil_prediksi.html',
                prediksi_skor=predicted_score,
                penilaian=assessment,
                saran=suggestion
            )

        except ValueError as ve:
            print(f"!! Value Error: {ve}")
            traceback.print_exc() # Cetak traceback untuk debug
            return render_template('hasil_prediksi.html', error=f"Data input tidak valid: {ve}. Pastikan semua angka diisi dengan benar.")
        except KeyError as ke:
            print(f"!! Key Error: {ke}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html', error=f"Kesalahan pada data input: Field '{ke}' mungkin hilang atau salah nama.")
        except Exception as e:
            print(f"!! Terjadi Error: {e}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html', error=f"Terjadi kesalahan saat memproses prediksi: {e}")

    else:
        # Jika bukan POST, redirect ke halaman form
        return flask.redirect(flask.url_for('halaman_prediksi'))


# --- Jalankan Aplikasi Flask ---
if __name__ == '__main__':
    # host='0.0.0.0' agar bisa diakses dari device lain di jaringan yang sama
    app.run(debug=True, host='0.0.0.0', port=5000)