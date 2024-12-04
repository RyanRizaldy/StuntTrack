from flask import Flask, request, jsonify
import tensorflow as tf
import pandas as pd
import joblib  # Menggunakan joblib untuk memuat scaler
import numpy as np
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Muat model yang sudah dilatih
trained_model = tf.keras.models.load_model('model/mlp_model.h5')

# Muat scaler yang sudah dilatih sebelumnya (misalnya scaler.pkl yang disimpan sebelumnya)
scaler = joblib.load('model/scaler.pkl')


@app.route('/predict', methods=['POST'])
def predict():
    # Pastikan request content adalah JSON
    if request.is_json:
        data = request.get_json()  # Ambil data JSON dari body request

        # Ambil data fitur dari request JSON
        umur = data.get('umur')  # Umur dalam bulan
        # 1 = Laki-laki, 0 = Perempuan
        jenis_kelamin = data.get('jenis_kelamin')
        tinggi_badan = data.get('tinggi_badan')  # Tinggi badan dalam cm

        # Periksa apakah semua fitur ada
        if umur is None or jenis_kelamin is None or tinggi_badan is None:
            return jsonify({'error': 'Missing features in request'}), 400

        # Menyiapkan data input untuk prediksi (ubah menjadi DataFrame)
        new_data = pd.DataFrame({
            'Umur': [umur],  # Umur dalam bulan
            'Jenis_Kelamin': [jenis_kelamin],  # 1 = Laki-laki, 0 = Perempuan
            'Tinggi_Badan': [tinggi_badan]  # Tinggi badan dalam cm
        })

        # Normalisasi data yang baru menggunakan scaler yang sudah dilatih
        try:
            new_data_scaled = scaler.transform(new_data)
        except Exception as e:
            return jsonify({'error': f'Error in scaling data: {str(e)}'}), 500

        # Lakukan prediksi menggunakan model
        try:
            predictions = trained_model.predict(new_data_scaled)
        except Exception as e:
            return jsonify({'error': f'Error in prediction: {str(e)}'}), 500

        # Konversi prediksi ke label kelas (argmax untuk mendapatkan kelas dengan probabilitas tertinggi)
        predicted_class = predictions.argmax(axis=1)[0]

        # Definisikan kelas
        classes = ['severely_stunted', 'stunted', 'normal', 'tinggi']

        # Mengembalikan hasil prediksi
        return jsonify({
            'predicted_class': classes[predicted_class],
            # Mengembalikan probabilitas setiap kelas
            'prediction_probability': predictions[0].tolist()
        })

    else:
        return jsonify({'error': 'Request must be JSON'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
