from flask import Flask, request, jsonify
import tensorflow as tf
import pandas as pd
import joblib  # Untuk memuat scaler
import os
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Muat model yang sudah dilatih
model_path = 'model/mlp_model.h5'
scaler_path = 'model/scaler.pkl'

try:
    if os.path.exists(model_path):
        trained_model = tf.keras.models.load_model(model_path)
        logging.info("Model loaded successfully.")
    else:
        raise FileNotFoundError(f"Model file not found at {model_path}")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    raise

# Muat scaler yang sudah dilatih sebelumnya
try:
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        logging.info("Scaler loaded successfully.")
    else:
        raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
except Exception as e:
    logging.error(f"Error loading scaler: {e}")
    raise


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Pastikan request content adalah JSON
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()  # Ambil data JSON dari body request

        # Ambil data fitur dari request JSON
        umur = data.get('umur')  # Umur dalam bulan
        jenis_kelamin = data.get('jenis_kelamin')
        tinggi_badan = data.get('tinggi_badan')  # Tinggi badan dalam cm

        # Periksa apakah semua fitur ada dan tipe data benar
        if None in (umur, jenis_kelamin, tinggi_badan):
            return jsonify({'error': 'Missing features in request'}), 400

        if not isinstance(umur, (int, float)) or not isinstance(tinggi_badan, (int, float)):
            return jsonify({'error': 'Umur and Tinggi_Badan must be numeric values'}), 400

        # Menyiapkan data input untuk prediksi
        new_data = pd.DataFrame({
            'Umur': [umur],
            'Jenis_Kelamin': [jenis_kelamin],
            'Tinggi_Badan': [tinggi_badan]
        })

        # Normalisasi data menggunakan scaler yang sudah dilatih
        try:
            new_data_scaled = scaler.transform(new_data)
        except Exception as e:
            logging.error(f"Error scaling data: {e}")
            return jsonify({'error': f'Error scaling data: {str(e)}'}), 500

        # Lakukan prediksi menggunakan model
        try:
            predictions = trained_model.predict(new_data_scaled)
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            return jsonify({'error': f'Error during prediction: {str(e)}'}), 500

        # Konversi prediksi ke label kelas
        predicted_class = predictions.argmax(axis=1)[0]
        classes = ['severely_stunted', 'stunted', 'normal', 'tinggi']

        # Mengembalikan hasil prediksi
        return jsonify({
            'predicted_class': classes[predicted_class],
            'prediction_probability': predictions[0].tolist()
        })

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


if __name__ == '__main__':
    # Gunakan variabel lingkungan PORT dari Cloud Run
    port = int(os.environ.get("PORT", 9898))
    app.run(debug=False, host='0.0.0.0', port=port)
