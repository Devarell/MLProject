import flask
from flask import Flask, request, render_template, jsonify
import joblib
import numpy as np
import pandas as pd
import traceback # Untuk logging error detail

app = Flask(__name__)

# --- Konfigurasi ---
MODEL_FILE_PATH = 'linear_regression_model.pkl' # Pastikan ini nama file model Anda
# MODEL_FILE_PATH = 'rf_original.pkl' # Uncomment jika model Anda yang ini

# --- Muat Model ---
model = None
model_feature_names = []
try:
    model = joblib.load(MODEL_FILE_PATH)
    print(f"* Model '{MODEL_FILE_PATH}' berhasil dimuat.")

    # === PENTING: Sesuaikan Nama dan Urutan Fitur ===
    # Daftar ini HARUS cocok dengan urutan dan nama kolom fitur
    # yang digunakan saat melatih model Anda (linear_regression_model.pkl).
    # Contoh ini berdasarkan file PredictionPage.html dan asumsi mapping preprocessing.
    model_feature_names = [
        'Internet_Access',             # Hasil mapping 'internetAccess' (yes/no)
        'Extracurricular_Activities',  # Hasil mapping 'extracurricular' (yes/no)
        'Peer_Influence',              # Hasil mapping 'peerInfluence' (low/medium/high)
        'Access_to_Resources',         # Hasil mapping 'resourceAccess' (low/medium/high)
        'Teacher_Quality',             # Hasil mapping 'teacherQuality' (low/medium/high)
        'Distance_from_Home',          # Hasil mapping 'distanceHome' (near/moderate/far)
        'Hours_Studied',               # Input 'hoursStudied' (numerik)
        'Previous_Scores',             # Input 'previousScore' (numerik)
        'Attendance',                  # Input 'attendance' (numerik)
        'Tutoring_Sessions',           # Input 'tutoringSessions' (numerik)
        # 'mataPelajaran' & 'totalSessions' dihapus karena tidak ada di daftar fitur model (asumsi dari file Anda)
    ]
    print(f"* Fitur yang diharapkan model (sesuai urutan training): {model_feature_names}")

except FileNotFoundError:
    print(f"!! ERROR: File model tidak ditemukan di '{MODEL_FILE_PATH}'.")
    print("!! Pastikan file model berada di direktori yang sama dengan app.py atau sesuaikan path-nya.")
    model = None
    model_feature_names = [] # Pastikan kosong jika model gagal dimuat
except Exception as e:
    print(f"!! ERROR: Gagal memuat model dari '{MODEL_FILE_PATH}'.")
    print(f"!! Detail Error: {e}")
    traceback.print_exc()
    model = None
    model_feature_names = [] # Pastikan kosong jika model gagal dimuat


# --- Fungsi Bantuan Preprocessing ---
def preprocess_input(form_data):
    """
    Mengambil data dari form Flask, melakukan preprocessing, dan
    mengembalikan dictionary fitur dengan KUNCI yang cocok dengan
    NAMA FITUR yang diharapkan model (dari model_feature_names).
    """
    processed = {}

    # Mapping nilai kategori ke numerik (SESUAIKAN DENGAN PREPROCESSING MODEL ANDA)
    # Asumsi: low=0, medium=1, high=2; yes=1, no=0; near=0, moderate=1, far=2
    internet_map = {'yes': 1, 'no': 0}
    extracurricular_map = {'yes': 1, 'no': 0}
    peer_influence_map = {'low': 0, 'medium': 1, 'high': 2}
    resource_access_map = {'low': 0, 'medium': 1, 'high': 2}
    teacher_quality_map = {'low': 0, 'medium': 1, 'high': 2}
    distance_map = {'near': 0, 'moderate': 1, 'far': 2}

    try:
        # --- Konversi & Mapping Input ---
        # Gunakan NAMA FITUR MODEL sebagai KUNCI dictionary
        # Gunakan .get() untuk menghindari error jika input tidak ada (meskipun form wajib diisi)

        # Kategori
        processed['Internet_Access'] = internet_map.get(form_data.get('internetAccess'), 0)
        processed['Extracurricular_Activities'] = extracurricular_map.get(form_data.get('extracurricular'), 0)
        processed['Peer_Influence'] = peer_influence_map.get(form_data.get('peerInfluence'), 1)
        processed['Access_to_Resources'] = resource_access_map.get(form_data.get('resourceAccess'), 1)
        processed['Teacher_Quality'] = teacher_quality_map.get(form_data.get('teacherQuality'), 1)
        processed['Distance_from_Home'] = distance_map.get(form_data.get('distanceHome'), 1)

        # Numerik (Pastikan konversi ke float)
        # Gunakan 0 sebagai default jika input kosong atau tidak valid (meskipun required)
        processed['Hours_Studied'] = float(form_data.get('hoursStudied', 0) or 0) # Tambahan 'or 0' untuk handle string kosong
        processed['Previous_Scores'] = float(form_data.get('previousScore', 0) or 0)
        processed['Attendance'] = float(form_data.get('attendance', 0) or 0)
        processed['Tutoring_Sessions'] = float(form_data.get('tutoringSessions', 0) or 0)

        # --- PENTING: Validasi tambahan untuk mencegah nilai aneh setelah konversi ---
        # Contoh: Pastikan Attendance tidak lebih besar dari Total Sessions jika Total Sessions digunakan
        # Saat ini Total Sessions tidak digunakan di model_feature_names, jadi validasi ini tidak perlu
        # Tapi kalau Attendance adalah RASIO, Anda perlu input Total Sessions dan hitung rasionya di sini.

    except ValueError as e:
        # Jika konversi ke float gagal, lempar error
        print(f"!! Value error saat konversi di preprocess_input: {e}")
        raise ValueError(f"Input tidak valid: {e}")
    except Exception as e:
        print(f"!! Error tak terduga saat preprocessing: {e}")
        traceback.print_exc()
        raise e # Lempar kembali error agar ditangkap di route

    # Pastikan processed memiliki SEMUA KUNCI yang ada di model_feature_names
    # Jika ada yang hilang, tambahkan dengan nilai default (misal 0)
    for feature in model_feature_names:
        if feature not in processed:
            processed[feature] = 0 # Atau nilai default lain yang sesuai

    return processed


# --- Route Halaman ---

@app.route('/') # Menangani alamat akar
@app.route('/home') # Juga bisa diakses via /home
def halaman_utama():
    return render_template('HomePage.html')

@app.route('/prediksi') # Route untuk halaman prediksi
def halaman_prediksi():
    # Periksa apakah model berhasil dimuat sebelum menampilkan form
    if model is None:
         # Atau tampilkan halaman error ramah pengguna
         return "<html><body><h1>Error: Model Prediksi Tidak Tersedia</h1><p>Maaf, terjadi masalah saat memuat model prediksi. Silakan coba lagi nanti atau hubungi administrator.</p></body></html>", 500
    return render_template('PredictionPage.html')

@app.route('/tentang') # Route untuk halaman tentang
def halaman_tentang():
    return render_template('AboutUs.html')

# Route Kontak (Placeholder jika belum ada halamannya)
@app.route('/kontak')
def halaman_kontak():
     # Anda bisa membuat halaman HTML terpisah untuk kontak atau menampilkan pesan placeholder
     return "<html><body><h1>Kontak Kami</h1><p>Halaman kontak belum tersedia.</p><p><a href='/'>Kembali ke Home</a></p></body></html>"


# --- Route untuk Memproses Prediksi ---
@app.route('/proses-prediksi', methods=['POST'])
def proses_prediksi():
    # Periksa kembali apakah model ada sebelum mencoba prediksi
    if model is None:
        # Redirect ke halaman hasil prediksi dengan pesan error
        return render_template('hasil_prediksi.html', error="Model prediksi tidak dapat dimuat. Silakan coba lagi nanti.")

    if request.method == 'POST':
        try:
            form_data = request.form
            print("* Menerima data form mentah:", form_data.to_dict())

            # Preprocessing data input
            processed_features = preprocess_input(form_data)
            print("* Data setelah preprocessing:", processed_features)

            # --- Buat DataFrame dengan urutan kolom yang BENAR ---
            # Pastikan kolom DataFrame SAMA PERSIS dengan model_feature_names
            # Menggunakan list model_feature_names memastikan urutan kolom yang benar
            input_df = pd.DataFrame([processed_features])[model_feature_names]

            # Periksa apakah ada kolom NaN setelah reindex
            if input_df.isnull().values.any():
                 print("!! WARNING: Terdapat nilai NaN setelah reindex. Periksa preprocessing atau model_feature_names.")
                 print(input_df)
                 # Opsional: kembalikan error jika ada NaN
                 # return render_template('hasil_prediksi.html', error="Kesalahan internal: Data tidak lengkap setelah preprocessing.")


            print("* DataFrame siap untuk model (sesuai urutan fitur):\n", input_df)

            input_array = input_df.to_numpy()

            # (Opsional) Scaling jika perlu (hanya jika scaler_file.pkl ada dan digunakan saat training)
            # try:
            #     scaler = joblib.load('scaler_file.pkl') # Ganti nama file scaler Anda
            #     input_array_scaled = scaler.transform(input_array)
            # except FileNotFoundError:
            #     print("!! WARNING: Scaler file tidak ditemukan. Melanjutkan tanpa scaling.")
            #     input_array_scaled = input_array
            # except Exception as e:
            #     print(f"!! WARNING: Gagal memuat atau menerapkan scaler: {e}. Melanjutkan tanpa scaling.")
            #     input_array_scaled = input_array

            # Lakukan prediksi
            prediction = model.predict(input_array)
            predicted_score = round(float(prediction[0]), 1)
            # Batasi nilai prediksi antara 0 hingga 100
            predicted_score = max(0, min(100, predicted_score))

            print(f"* Prediksi Skor Akhir: {predicted_score}")

            # Tentukan Saran (logika saran sama)
            saran = ''
            if predicted_score >= 90:
                saran = "Luar biasa! Pertahankan fokus dan terus eksplorasi materi lebih dalam. Anda di jalur yang sangat tepat!"
            elif predicted_score >= 80:
                saran = "Hasil yang bagus! Identifikasi area yang masih bisa ditingkatkan sedikit lagi dan pertahankan kebiasaan belajar positif Anda."
            elif predicted_score >= 70:
                saran = "Cukup baik! Terus tingkatkan pemahaman konsep dasar dan latihan soal secara rutin untuk hasil yang lebih optimal."
            elif predicted_score >= 60:
                saran = "Sudah cukup, tapi masih banyak ruang untuk peningkatan. Coba evaluasi metode belajar Anda, mungkin perlu strategi baru atau tambahan waktu belajar."
            else:
                saran = "Jangan berkecil hati! Ini adalah kesempatan untuk mengidentifikasi tantangan utama. Fokus pada pemahaman fundamental, jangan ragu bertanya, dan cari sumber belajar tambahan."


            # Render halaman hasil prediksi dengan skor dan saran
            return render_template(
                'hasil_prediksi.html',
                prediksi_skor=predicted_score,
                saran=saran
            )

        except ValueError as ve:
            # Tangani error terkait nilai input (misal konversi gagal)
            print(f"!! Value Error saat proses prediksi: {ve}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html', error=f"Input Data Tidak Valid: {ve}. Mohon periksa kembali isian Anda.")
        except KeyError as ke:
            # Tangani error jika ada kunci (nama input form) yang tidak sesuai
            print(f"!! Key Error saat proses prediksi: {ke}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html', error=f"Kesalahan pada Data Input: Kolom '{ke}' tidak ditemukan atau salah nama di form.")
        except Exception as e:
            # Tangani error tak terduga lainnya
            print(f"!! Terjadi Error Tak Terduga saat prediksi: {e}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html', error=f"Terjadi kesalahan internal saat memproses prediksi.")

    else:
        # Jika ada yang mengakses /proses-prediksi bukan dengan POST, redirect ke halaman prediksi
        return flask.redirect(flask.url_for('halaman_prediksi'))


# --- Jalankan Aplikasi Flask ---
if __name__ == '__main__':
    # app.run(debug=True) # Mode debug ON, host default 127.0.0.1, port 5000
    # Menggunakan host='0.0.0.0' agar bisa diakses dari IP lokal lain (jika ada)
    app.run(debug=True, host='0.0.0.0', port=5000)