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

        # Tentukan artikel yang relevan berdasarkan kelas
        articles = {
            'severely_stunted': [
                {'id': 4, 'judul': 'Ketahui Masalah Stunting dan Cara Mengatasi Stunting',
                    'gambar': 'https://example.com/path/to/image1.jpg', 'penulis': 'dr. Yantosan'},
                {'id': 5, 'judul': 'Stunting pada Anak',
                    'gambar': 'https://example.com/path/to/image2.jpg', 'penulis': 'dr. Meva Nareza T'}
            ],
            'stunted': [
                {'id': 6, 'judul': 'Stunting pada Anak',
                    'gambar': 'https://example.com/path/to/image3.jpg', 'penulis': 'dr. Meva Nareza T'}
            ],
            'normal': [
                {'id': 1, 'judul': 'Panduan Pemenuhan Gizi Balita Usia 4–5 Tahun',
                    'gambar': 'https://example.com/path/to/image4.jpg', 'penulis': 'dr. Rizal Fadli'}
            ],
            'tinggi': [
                {'id': 2, 'judul': 'Pola Makan Sehat Balita',
                    'gambar': 'https://example.com/path/to/image5.jpg', 'penulis': 'dr. Fadhli Rizal Makarim'},
                {'id': 3, 'judul': 'Seberapa Banyak Porsi Makan yang Tepat untuk Anak Usia 5 Tahun?',
                    'gambar': 'https://example.com/path/to/image6.jpg', 'penulis': 'dr. Carla Pramudita Susanto'}
            ]
        }

        # Ambil artikel yang sesuai dengan prediksi
        predicted_class_label = classes[predicted_class]
        relevant_articles = articles.get(predicted_class_label, [])

        # Mengembalikan hasil prediksi dan artikel terkait
        return jsonify({
            'predicted_class': predicted_class_label,
            'prediction_probability': predictions[0].tolist(),
            'related_articles': relevant_articles
        })

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def status():
    try:
        return jsonify({'status': 'API is running', 'message': 'Flask app is live!'}), 200
    except Exception as e:
        logging.error(f"Error in status route: {e}")
        return jsonify({'error': f'Error in status route: {str(e)}'}), 500


# Menambahkan endpoint untuk menampilkan seluruh artikel
@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        # Daftar lengkap artikel tanpa filter berdasarkan predicted_class
        all_articles = [
            {'id': 1, 'judul': 'Ibu Perlu Tahu, Ini 4 Cara Biar Anak Agar Tumbuh Tinggi',
                'gambar': 'https://images.app.goo.gl/NatbD9vnW6qQQhYE9', 'penulis': 'dr. Rizal Fadli', 'predicted_class': 'tinggi'},
            {'id': 2, 'judul': 'Berbagai Cara Menambah Tinggi Badan yang Alami dan Sehat', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1628569726/attached_image/cara-menambah-tinggi-ba',
                'penulis': 'dr. Robby Firmansyah Murzen', 'predicted_class': 'tinggi'},
            {'id': 3, 'judul': 'Panduan Pemenuhan Gizi Balita Usia 4–5 Tahun',
                'gambar': 'https://cdn1-production-images-kly.akamaized.net/GmGDtuKU7NuY2n8uVU28zLKiDlM=/0x91:5942x3440/640x360/filters:quality(75):strip_icc():format(webp)/kly-media-production/medias/2978946/original/091196100', 'penulis': 'dr. Rizal Fadli ', 'predicted_class': 'tinggi'},
            {'id': 4, 'judul': 'Panduan Makanan Seimbang untuk Balita',
                'gambar': 'https://mommiesdaily.com/_next/image?url=https%3A%2F%2Fmommiesdaily.com%2Fwp-content%2Fuploads%2F2019%2F03%2F01-learn-what-works-Heres-Why-Japanese-Children-Are-the-Healthiest-in-the-World_510693205-u', 'penulis': 'dr. Fadhli Rizal Makarim', 'predicted_class': 'tinggi'},
            {'id': 5, 'judul': 'Stunting pada Anak', 'gambar': 'https://example.com/path/to/image5.jpg',
                'penulis': 'dr. Meva Nareza T', 'predicted_class': 'tinggi'},
            {'id': 6, 'judul': 'Porsi Makan Anak 5 Tahun yang Tepat dan Tidak Berlebihan', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/03/porsi-makan-anak-5-tahun.jpg?w=1080&q=75',
                'penulis': 'dr. Damar Upahita', 'predicted_class': 'tinggi'},
            {'id': 7, 'judul': 'Hari Gizi Nasional, Inilah Pola Makan Bergizi untuk Si Kecil', 'gambar': 'https://parenting.co.id/img/images/BAYIMAKAN800.jpg',
                'penulis': 'Redaksi Halodoc ', 'predicted_class': 'tinggi'},
            {'id': 8, 'judul': 'Ini Peran Protein dalam Tumbuh Kembang Anak', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2017/05/anak-makan-sendiri.jpg?w=1080&q=75',
                'penulis': 'dr. Fadhli Rizal Makarim ', 'predicted_class': 'tinggi'},
            {'id': 9, 'judul': 'Jangan Sampai Telat Bun, Begini Tips Meninggikan Badan Anak Secara Alami', 'gambar': 'https://www.haibunda.com/parenting/20200330152358-60-87865/jangan-sampai-telat-bun-begini-tips-meninggikan-badan-anak-secara-alami#',
                'penulis': 'Jujuk Ernawati', 'predicted_class': 'normal'},
            {'id': 11, 'judul': '7 Makanan Bergizi untuk Mencegah Stunting pada Balita', 'gambar': 'https://sl.bing.net/b7MPt3WKtVs',
                'penulis': 'dr. Rizal Fadli', 'predicted_class': 'normal'},
            {'id': 12, 'judul': 'Resep Makanan Balita 1-2 Tahun yang Penuh Gizi dan Enak', 'gambar': 'https://o-cdn-cas.oramiland.com/parenting/images/6-resep-makanan-balita-1-2-tahun.width-800.format-webp.webp',
                'penulis': 'Orami Articles', 'predicted_class': 'normal'},
            {'id': 13, 'judul': 'Resep Masakan Rumahan untuk Anak yang Bergizi, Sederhana, Enak, dan Cocok Buat Bekal', 'gambar': 'https://cdn-brilio-net.akamaized.net/webp/news/2024/09/11/300754/1200xauto-11-resep-masakan-rumahan-untuk-anak-yang-bergizi-sederhana-enak-dan-cocok-buat-bekal-240911x.jpg',
                'penulis': 'Nadhifah', 'predicted_class': 'normal'},
            {'id': 14, 'judul': 'Mineral dan Vitamin Anak yang Penting bagi Pertumbuhan', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1599539674/attached_image/mineral-dan-vitamin-anak-yang-penting-bagi-pertumbuhan-mereka-0-alodokter.jpg',
                'penulis': 'dr. Meva Nareza T', 'predicted_class': 'normal'},
            {'id': 15, 'judul': 'Nutrisi Dukung Anak Tumbuh Tinggi', 'gambar': 'https://www.nestlehealthscience.co.id/sites/g/files/dnigna186/files/inline-images/nutrisi_anak_tinggi_1.jpg ',
                'penulis': 'nestlehealthscience', 'predicted_class': 'normal'},
            {'id': 16, 'judul': 'Langkah Mudah Meningkatkan Imunitas Anak', 'gambar': 'https://www.nutriclub.co.id/_default_upload_bucket/image-thumb__2636__default/5-Langkah-Mudah-Tingkatkan-Imunitas-si-Kecil-700x278.webp',
                'penulis': 'dr. Isman Jafar, Sp.A (K)', 'predicted_class': 'normal'},
            {'id': 17, 'judul': '8 Menu Makanan untuk Stunting: Pencegahan Melalui Gizi Seimbang', 'gambar': 'https://www.chubb.com/content/dam/chubb-sites/chubb-com/id-id/lei-new-assets/images/article/makanan-untuk-stunting.jpg/jcr:content/renditions/cq5dam.web.1280.1280.jpeg',
                'penulis': 'Chubb Life Indonesia', 'predicted_class': 'stunted'},
            {'id': 18, 'judul': 'Protein Hewani Penting Untuk Cegah Stunting', 'gambar': 'https://joss.co.id/data/uploads/2023/01/Protein-Hewani-Cegah-Stunting-678x381.jpg',
                'penulis': 'rumahsakit', 'predicted_class': 'stunted'},
            {'id': 19, 'judul': 'Panduan Memenuhi Kebutuhan Gizi Balita Usia 1-5 Tahun', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/02/gizi-balita.jpg?w=1080&q=75',
                'penulis': 'dr. Airindya Bella', 'predicted_class': 'stunted'},
            {'id': 21, 'judul': 'Tips Menjaga Asupan Gizi Anak', 'gambar': 'https://kanjabung.com/wp-content/uploads/2022/09/image-10.png',
                'penulis': 'lactoclub', 'predicted_class': 'stunted'},
            {'id': 22, 'judul': 'Ketahui Masalah Stunting dan Cara Mengatasi Stunting', 'gambar': 'https://live-69566-healthscience-corporate-id.pantheonsite.io/sites/default/files/1_1.jpg',
                'penulis': 'nestlehealthscience', 'predicted_class': 'several_stunted'},
            {'id': 23, 'judul': 'Stunting pada Anak', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1657531269/attached_image/stunting-0-alodokter.jpg',
                'penulis': 'dr. Meva Nareza T', 'predicted_class': 'several_stunted'},
            {'id': 24, 'judul': 'Ahli Gizi: Status gizi perlu dipantau agar anak stunting tak obesitas', 'gambar': 'https://img.antaranews.com/cache/1200x800/2023/10/06/20231005_175434.jpg.webp',
                'penulis': 'Atman Ahdiat', 'predicted_class': 'several_stunted'},
            {'id': 25, 'judul': 'RUTF, Makanan Khusus untuk Balita Gizi Buruk', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1684805402/attached_image/rutf-makanan-khusus-untuk-balita-gizi-buruk-0-alodokter.jpg',
                'penulis': 'dr. Airindya Bella', 'predicted_class': 'several_stunted'},
            {'id': 26, 'judul': 'Creating a Nutritious Emergency Food Supply', 'gambar': ' dr. Rizal Fadli',
                'penulis': ' dr. Rizal Fadli', 'predicted_class': 'several_stunted'},
        ]

        return jsonify(all_articles), 200

    except Exception as e:
        logging.error(f"Error in articles route: {e}")
        return jsonify({'error': f'Error in articles route: {str(e)}'}), 500


# Menambahkan endpoint untuk menampilkan detail artikel berdasarkan ID
@app.route('/articles/<int:id>', methods=['GET'])
def get_article_detail(id):
    try:
        # Daftar artikel
        all_articles = [
            {'id': 1, 'judul': 'Ibu Perlu Tahu, Ini 4 Cara Biar Anak Agar Tumbuh Tinggi',
                'gambar': 'https://images.app.goo.gl/NatbD9vnW6qQQhYE9', 'penulis': 'dr. Rizal Fadli', 'predicted_class': 'tinggi', 'isi': '1.	Makanan Bergizi Seimbang: Penting untuk memberikan gizi seimbang yang mencakup protein, lemak, serat, karbohidrat, vitamin, dan mineral. Contoh makanan yang baik termasuk kacang, daging ayam, sayuran hijau, yoghurt, telur, buah-buahan, dan ikan salmon.2.	Berikan Susu: Susu mengandung protein berkualitas, magnesium, zink, lemak, dan berbagai mineral penting lainnya yang mendukung pertumbuhan anak.3.	Ajak untuk Berolahraga: Olahraga rutin membantu memperkuat otot, tulang, dan meningkatkan produksi hormon pertumbuhan(HGH). Anak disarankan bermain aktif selama 60 menit tiap hari untuk balita dan 120 menit tiap hari untuk anak prasekolah.4.	Suplemen: Jika diperlukan, suplemen dapat membantu memenuhi kebutuhan nutrisi yang kurang dari makanan sehari-hari.'},
            {'id': 2, 'judul': 'Berbagai Cara Menambah Tinggi Badan yang Alami dan Sehat', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1628569726/attached_image/cara-menambah-tinggi-ba',
                'penulis': 'dr. Robby Firmansyah Murzen', 'predicted_class': 'tinggi', 'isi': '1.	Olahraga Secara Rutin: Aktivitas fisik seperti bersepeda, lompat tali, berenang, dan basket dapat memperkuat jaringan otot dan tulang serta meningkatkan produksi hormon pertumbuhan.2.	Perbaiki Postur Tubuh: Kebiasaan berdiri, duduk, dan tidur dengan postur yang benar dapat membuat tubuh terlihat lebih tinggi dan proporsional. Yoga dapat membantu memperbaiki postur tubuh.3.	Istirahat yang Cukup: Tidur yang cukup sangat penting untuk produksi hormon pertumbuhan dan perkembangan tulang. Anak-anak dan remaja membutuhkan waktu tidur yang lebih banyak dibandingkan orang dewasa.4.	Konsumsi Makanan Bergizi: Makanan sehat dan bergizi, terutama yang tinggi kandungan vitamin D, sangat penting untuk kesehatan tulang dan pertumbuhan.'},
            {'id': 3, 'judul': 'Panduan Pemenuhan Gizi Balita Usia 4–5 Tahun',
                'gambar': 'https://cdn1-production-images-kly.akamaized.net/GmGDtuKU7NuY2n8uVU28zLKiDlM=/0x91:5942x3440/640x360/filters:quality(75):strip_icc():format(webp)/kly-media-production/medias/2978946/original/091196100', 'penulis': 'dr. Rizal Fadli ', 'predicted_class': 'tinggi', 'isi': 'Kebutuhan Gizi:1.	Kalori: Setidaknya 1.600 kalori per hari.2.	Karbohidrat: Sebanyak 220 gram per hari, dengan fokus pada karbohidrat kompleks untuk energi yang stabil. 3.	Protein: Setidaknya 35 gram per hari dari sumber protein hewani dan nabati.4.	Lemak: Setidaknya 62 gram per hari, dengan fokus pada lemak baik seperti minyak zaitun dan alpukat.5.	Serat: Setidaknya 22 gram per hari dari sayuran dan buah.6.	Vitamin dan Mineral: Memastikan asupan vitamin dan mineral yang penting untuk pertumbuhan dan perkembangan anak. Catatan Cepat:•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dari berbagai jenis makanan.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.•	Peran gizi seimbang dalam mendukung pertumbuhan dan perkembangan anak yang optimal.'},
            {'id': 4, 'judul': 'Panduan Makanan Seimbang untuk Balita',
                'gambar': 'https://mommiesdaily.com/_next/image?url=https%3A%2F%2Fmommiesdaily.com%2Fwp-content%2Fuploads%2F2019%2F03%2F01-learn-what-works-Heres-Why-Japanese-Children-Are-the-Healthiest-in-the-World_510693205-u', 'penulis': 'dr. Fadhli Rizal Makarim', 'predicted_class': 'tinggi', 'isi': 'Langkah-langkah untuk Membentuk Pola Makan Sehat:1.	Pola Makan Teratur: Pastikan anak makan pada waktu yang teratur, seperti sarapan, makan siang, dan makan malam.2.	Makanan Bergizi: Berikan makanan yang mengandung pati, protein, serat, vitamin, dan mineral. Contohnya, roti, nasi, pasta, sereal, kentang, buah-buahan, sayuran, produk susu, dan daging rendah lemak.3.	Variasi Makanan: Sertakan berbagai jenis makanan dari kelompok makanan utama, seperti pati, buah-buahan, sayuran, produk susu, dan protein.4.	Porsi yang Tepat: Berikan porsi makanan yang sesuai dengan usia dan tingkat aktivitas anak.5.	Aktivitas Fisik: Dorong anak untuk melakukan aktivitas fisik sehari-hari untuk mendukung pola makan sehat.Catatan Cepat:•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dari berbagai jenis makanan.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.•	Peran gizi seimbang dalam mendukung pertumbuhan dan perkembangan anak yang optimal.'},
            {'id': 5, 'judul': 'Stunting pada Anak', 'gambar': 'https://example.com/path/to/image5.jpg',
                'penulis': 'dr. Meva Nareza T', 'predicted_class': 'tinggi', 'isi': 'Panduan Porsi Makan:1.	Pola Makan Teratur: Pastikan anak makan pada waktu yang teratur, seperti sarapan, makan siang, dan makan malam.2.	Porsi Makan Utama: Berikan porsi makan utama tiga kali dalam sehari, dengan waktu makan maksimal 30 menit.3.	Camilan: Berikan camilan yang bergizi sekitar 2 jam sebelum makan utama untuk memenuhi rasa lapar anak tanpa mengganggu nafsu makan utama.4.	Variasi Makanan: Sertakan berbagai jenis makanan dari kelompok makanan utama, seperti karbohidrat, protein, sayuran, buah, dan produk susu.5.	Porsi yang Tepat: Berdasarkan Angka Kecukupan Gizi (AKG) 2013 dari Kementerian Kesehatan RI, usia 4-6 tahun membutuhkan sekitar 1.600 kalori per hari.Catatan Cepat:•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dari berbagai jenis makanan.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.'},
            {'id': 6, 'judul': 'Porsi Makan Anak 5 Tahun yang Tepat dan Tidak Berlebihan', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/03/porsi-makan-anak-5-tahun.jpg?w=1080&q=75',
                'penulis': 'dr. Damar Upahita', 'predicted_class': 'tinggi', 'isi': 'Langkah-langkah Pola Makan Bergizi:1.	Buah dan Sayur-sayuran: Sumber vitamin, mineral, dan serat yang penting untuk kesehatan.2.	Kentang, Roti, Nasi, Pasta: Sumber karbohidrat yang memberikan energi.3.	Kacang-kacangan, Ikan, Telur, Daging: Sumber protein penting untuk pertumbuhan dan pemeliharaan jaringan tubuh.4.	Susu dan Alternatif: Sumber kalsium dan vitamin D untuk tulang dan gigi yang kuat.5.	Minyak: Memilih minyak sehat seperti minyak zaitun dan alpukat. Catatan Cepat:•	Penting untuk menghindari makanan olahan dan ringan yang mengandung gula halus berlebihan.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.'},
            {'id': 7, 'judul': 'Hari Gizi Nasional, Inilah Pola Makan Bergizi untuk Si Kecil', 'gambar': 'https://parenting.co.id/img/images/BAYIMAKAN800.jpg',
                'penulis': 'Redaksi Halodoc ', 'predicted_class': 'tinggi', 'isi': ''},
            {'id': 8, 'judul': 'Ini Peran Protein dalam Tumbuh Kembang Anak', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2017/05/anak-makan-sendiri.jpg?w=1080&q=75',
                'penulis': 'dr. Fadhli Rizal Makarim ', 'predicted_class': 'tinggi', 'isi': 'Nutrisi Penting: 1.	Protein Hewani: Dapat ditemukan pada daging, ikan, telur, dan susu.2.	Protein Nabati: Dapat ditemukan pada tahu, tempe, dan kacang-kacangan.•	Keduanya penting untuk mendukung metabolisme, meningkatkan massa otot, kepadatan tulang, serta mendukung kinerja sistem kekebalan tubuh.Catatan Cepat: •	Penting untuk memastikan anak mendapatkan asupan protein yang cukup dari berbagai sumber.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.•	Peran gizi seimbang dalam mendukung pertumbuhan dan perkembangan anak yang optimal.'},
            {'id': 9, 'judul': 'Jangan Sampai Telat Bun, Begini Tips Meninggikan Badan Anak Secara Alami', 'gambar': 'https://www.haibunda.com/parenting/20200330152358-60-87865/jangan-sampai-telat-bun-begini-tips-meninggikan-badan-anak-secara-alami#',
                'penulis': 'Jujuk Ernawati', 'predicted_class': 'normal', 'isi': '1.	Olahraga Rutin: Aktivitas fisik seperti bersepeda, lompat tali, berenang, dan basket dapat memperkuat jaringan otot dan tulang serta meningkatkan produksi hormon pertumbuhan.2.	Peregangan dan Yoga: Melakukan peregangan dan yoga dapat membantu memperbaiki postur tubuh dan meningkatkan tinggi badan.3.	Makanan Bergizi: Konsumsi makanan sehat dan bergizi, terutama yang tinggi kandungan vitamin D, sangat penting untuk kesehatan tulang dan pertumbuhan.4.	Tidur yang Cukup: Tidur yang cukup sangat penting untuk produksi hormon pertumbuhan dan perkembangan tulang.'},
            {'id': 11, 'judul': '7 Makanan Bergizi untuk Mencegah Stunting pada Balita', 'gambar': 'https://sl.bing.net/b7MPt3WKtVs',
                'penulis': 'dr. Rizal Fadli', 'predicted_class': 'normal', 'isi': '1.	Tempe dan Tahu: Sumber protein nabati yang kaya akan zat besi, magnesium, dan serat.2.	Kacang-kacangan: Kacang hijau dan merah mengandung protein nabati, zat besi, dan serat yang penting untuk pertumbuhan.3.	Daging Ayam: Sumber protein hewani yang mudah dicerna dan mengandung zat besi serta vitamin B kompleks.4.	Telur: Mengandung protein lengkap dan vitamin B12 yang penting untuk perkembangan otak dan fungsi kognitif.5.	Ikan: Sumber asam lemak omega-3 yang esensial untuk perkembangan otak dan sistem saraf.6.	Hati Ayam: Sumber zat besi heme yang lebih mudah diserap oleh tubuh.7.	Buah Beri: Mengandung antioksidan tinggi, vitamin C, dan serat yang baik untuk sistem kekebalan tubuh dan pencernaan.'},
            {'id': 12, 'judul': 'Resep Makanan Balita 1-2 Tahun yang Penuh Gizi dan Enak', 'gambar': 'https://o-cdn-cas.oramiland.com/parenting/images/6-resep-makanan-balita-1-2-tahun.width-800.format-webp.webp',
                'penulis': 'Orami Articles', 'predicted_class': 'normal', 'isi': '1.	Nugget Bayam:o	Bahan: Bayam, kacang almond, tepung roti, telur, oregano, garam, keju parut.o	Cara Membuat: Bayam dicacah dan dicampur dengan kacang almond, oregano, garam, dan keju parutAdonan dibentuk nugget, digoreng hingga matang, dan disajikan.2.	Sup Krim Brokoli:o	Bahan: Brokoli, krim, bawang putih, bawang merah, garam, kaldu bubuk.o	Cara Membuat: Brokoli dan bawang putih diolah dalam sup krim, kemudian disajikan hangat.3.	Puff Ubi Jalar:o	Bahan: Ubi jalar, minyak sayur, yoghurt, sereal bayi, tepung.o	Cara Membuat: Ubi jalar dicampur dengan yoghurt dan minyak sayur, kemudian dibentuk dan dipanggang. Catatan Cepat:•	Resep-resep ini dirancang untuk memenuhi kebutuhan gizi anak-anak usia 1-2 tahun.•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dan bergizi.•	Kreativitas dalam penyajian makanan dapat membantu anak menerima makanan dengan lebih baik.'},
            {'id': 13, 'judul': 'Resep Masakan Rumahan untuk Anak yang Bergizi, Sederhana, Enak, dan Cocok Buat Bekal', 'gambar': 'https://cdn-brilio-net.akamaized.net/webp/news/2024/09/11/300754/1200xauto-11-resep-masakan-rumahan-untuk-anak-yang-bergizi-sederhana-enak-dan-cocok-buat-bekal-240911x.jpg',
                'penulis': 'Nadhifah', 'predicted_class': 'normal', 'isi': '1.	Nasi Goreng Telur:o	Bahan: Nasi putih, telur, bawang putih, kecap manis, garam, minyak.o	Cara Membuat: Tumis bawang putih, masukkan telur, lalu tambahkan nasi dan kecap manis. Aduk rata dan sajikan hangat.2.	Sup Ayam Sayuran:o	Bahan: Daging ayam, wortel, kentang, brokoli, bawang putih, kaldu bubuk, garam, lada.o	Cara Membuat: Rebus ayam dengan bawang putih, lalu masukkan wortel, kentang, dan brokoli. Tambahkan garam dan lada, masak hingga sayuran empuk.3.	Sate Ayam Tusuk Keju:o	Bahan: Dada ayam, keju cheddar, kecap manis, minyak goreng.o	Cara Membuat: Tusuk ayam dan keju secara bergantian pada tusuk sate, oleskan kecap manis dan minyak, lalu panggang hingga matang.4.	Bubur Ayam Sederhana:o	Bahan: Beras, daging ayam, bawang putih, kaldu ayam, garam, merica.o	Cara Membuat: Rebus beras dengan kaldu ayam, tumis bawang putih, lalu tambahkan ayam suwir. Sajikan bubur dengan ayam di atasnya.5.	Makaroni Keju Panggang:o	Bahan: Makaroni, susu, keju cheddar parut.o	Cara Membuat: Rebus makaroni, tambahkan susu dan keju parut, lalu panggang hingga keju matang.Catatan Cepat:•	Resep-resep ini dirancang untuk memenuhi kebutuhan gizi anak-anak dengan rasa yang ringan dan tampilan menarik.•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dan bergizi.•	Kreativitas dalam penyajian makanan dapat membantu anak menerima makanan dengan lebih baik.'},
            {'id': 14, 'judul': 'Mineral dan Vitamin Anak yang Penting bagi Pertumbuhan', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1599539674/attached_image/mineral-dan-vitamin-anak-yang-penting-bagi-pertumbuhan-mereka-0-alodokter.jpg',
                'penulis': 'dr. Meva Nareza T', 'predicted_class': 'normal', 'isi': 'Vitamin Penting:1.	Vitamin A: Membantu kesehatan mata, kulit, dan sistem kekebalan tubuh.2.	Vitamin B kompleks: Termasuk tiamin(B1), riboflavin(B2), niasin(B3), asam folat(B9), dan kobalamin(B12). Membantu mengolah energi, menjaga fungsi organ, dan pembentukan sel darah merah1. 3.	Vitamin C: Meningkatkan daya tahan tubuh dan membantu penyerapan zat besi.4.	Vitamin D: Membantu penyerapan kalsium dan fosfor untuk tulang dan gigi sehat.5.	Vitamin E: Fungsi sebagai antioksidan untuk melindungi sel-sel tubuh.6.	Vitamin K: Penting untuk proses pembekuan darah. Mineral Penting: 1.	Kalsium: Penting untuk tulang dan gigi yang kuat.2.	Zat Besi: Membantu pembentukan sel darah merah dan menghindari anemia.3.	Magnesium: Berperan dalam fungsi saraf dan otot.4.	Fosfat: Penting untuk energi dan struktur sel.5.	Zinc: Membantu pertumbuhan dan perkembangan tubuh.6.	Iodin: Penting untuk fungsi tiroid dan perkembangan otak.Catatan Cepat:•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dari berbagai jenis makanan.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.•	Peran gizi seimbang dalam mendukung pertumbuhan dan perkembangan anak yang optimal.'},
            {'id': 15, 'judul': 'Nutrisi Dukung Anak Tumbuh Tinggi', 'gambar': 'https://www.nestlehealthscience.co.id/sites/g/files/dnigna186/files/inline-images/nutrisi_anak_tinggi_1.jpg ',
                'penulis': 'nestlehealthscience', 'predicted_class': 'normal', 'isi': 'Nutrisi Penting:1.	Protein: Penting untuk pembentukan dan pemeliharaan jaringan tubuh. Sumber: daging, ikan, telur, dan produk susu.2.	Kalsium: Membantu pembentukan tulang dan gigi yang kuat. Sumber: susu dan produk olahan susu, sayuran hijau.3.	Vitamin D: Membantu penyerapan kalsium dan fosfor. Sumber: sinar matahari, makanan yang diberi vitamin D.4.	Zat Besi: Membantu pembentukan sel darah merah dan menghindari anemia. Sumber: daging, ikan, biji-bijian utuh, sayuran hijau.5.	Magnesium: Berperan dalam fungsi saraf dan otot. Sumber: biji-bijian utuh, kacang-kacangan, sayuran hijau.6.	Fosfor: Penting untuk energi dan struktur sel. Sumber: daging, ikan, biji-bijian utuh, susu.7.	Zink: Membantu pertumbuhan dan perkembangan tubuh. Sumber: daging, kacang-kacangan, biji-bijian utuh.8.	Iodin: Penting untuk fungsi tiroid dan perkembangan otak. Sumber: garam iodin, ikan, produk susu.Catatan Cepat:•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dari berbagai jenis makanan.•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.•	Peran gizi seimbang dalam mendukung pertumbuhan dan perkembangan anak yang optimal.'},
            {'id': 16, 'judul': 'Langkah Mudah Meningkatkan Imunitas Anak', 'gambar': 'https://www.nutriclub.co.id/_default_upload_bucket/image-thumb__2636__default/5-Langkah-Mudah-Tingkatkan-Imunitas-si-Kecil-700x278.webp',
                'penulis': 'dr. Isman Jafar, Sp.A (K)', 'predicted_class': 'normal', 'isi': 'Langkah-langkah:1.	Makan Makanan yang Bergizi Seimbang: Mengonsumsi makanan yang bergizi dan bervariasi sangat penting untuk menjaga kesehatan dan fungsi sel-sel imun.2.	Berjemur Matahari: Sinar matahari memiliki banyak manfaat untuk memperkuat daya tahan tubuh anak bila dilakukan dengan tepat.3.	Cukup Tidur: Anak harus mendapatkan tidur yang cukup untuk memaksimalkan kekebalan tubuh.4.	Imunisasi: Ikuti jadwal vaksinasi yang direkomendasikan oleh dokter untuk melindungi anak dari berbagai penyakit.5.	Cuci Tangan Rutin: Mengajarkan anak untuk mencuci tangan secara rutin dapat membantu mengurangi risiko infeksi.Catatan Cepat:•	Penting untuk memastikan anak mendapatkan asupan nutrisi yang seimbang dari berbagai jenis makanan•	Edukasi tentang pentingnya gizi seimbang sangat penting untuk orang tua.•	Peran gizi seimbang dalam mendukung pertumbuhan dan perkembangan anak yang optimal.'},
            {'id': 17, 'judul': '8 Menu Makanan untuk Stunting: Pencegahan Melalui Gizi Seimbang', 'gambar': 'https://www.chubb.com/content/dam/chubb-sites/chubb-com/id-id/lei-new-assets/images/article/makanan-untuk-stunting.jpg/jcr:content/renditions/cq5dam.web.1280.1280.jpeg',
                'penulis': 'Chubb Life Indonesia', 'predicted_class': 'stunted', 'isi': '1.	Kacang-kacangan: Kacang hijau dan merah mengandung protein nabati, zat besi, dan serat yang penting untuk pertumbuhan.2.	Daging Ayam: Sumber protein hewani yang mudah dicerna dan mengandung zat besi serta vitamin B kompleks.3.	Telur: Mengandung protein lengkap dan vitamin B12 yang penting untuk perkembangan otak dan fungsi kognitif.4.	Ikan: Sumber asam lemak omega-3 yang esensial untuk perkembangan otak dan sistem saraf.5.	Tempe dan Tahu: Protein nabati yang rendah lemak dan kaya akan serat, serta zat besi, kalsium, dan magnesium.6.	Hati Ayam: Sumber zat besi heme yang lebih mudah diserap oleh tubuh.7.	Buah Beri: Mengandung antioksidan tinggi, vitamin C, dan serat yang baik untuk sistem kekebalan tubuh dan pencernaan.8.	Sayuran Hijau: Kaya akan zat besi, kalsium, dan magnesium yang penting untuk pertumbuhan dan perkembangan tulang.'},
            {'id': 18, 'judul': 'Protein Hewani Penting Untuk Cegah Stunting', 'gambar': 'https://joss.co.id/data/uploads/2023/01/Protein-Hewani-Cegah-Stunting-678x381.jpg',
                'penulis': 'rumahsakit', 'predicted_class': 'stunted', 'isi': 'peran protein hewani dalam pencegahan stunting pada anak balita, dengan fokus pada beberapa poin utama:1.	Kandungan Protein: Protein hewani seperti daging, ikan, telur, dan produk susu mengandung asam amino esensial yang penting untuk pertumbuhan dan perkembangan anak.2.	Vitamin dan Mineral: Protein hewani juga mengandung vitamin dan mineral penting seperti vitamin B12, vitamin D, zat besi, dan magnesium yang mendukung kesehatan tulang dan pertumbuhan.3.	Kualitas Protein: Protein hewani memiliki kualitas yang lebih baik dibandingkan protein nabati karena lebih mudah diserap oleh tubuh dan mengandung asam amino esensial yang lengkap.4.	Hubungan dengan Stunting: Konsumsi protein hewani secara teratur dapat membantu mencegah stunting pada anak balita dengan meningkatkan tinggi badan dan kesehatan secara keseluruhan.'},
            {'id': 19, 'judul': 'Panduan Memenuhi Kebutuhan Gizi Balita Usia 1-5 Tahun', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/02/gizi-balita.jpg?w=1080&q=75',
                'penulis': 'dr. Airindya Bella', 'predicted_class': 'stunted', 'isi': 'tips untuk menjaga asupan gizi anak, termasuk:1.	Makanan Bergizi: Pastikan anak mendapatkan makanan bergizi yang mencakup protein, lemak, serat, vitamin, dan mineral. Contohnya adalah buah-buahan, sayuran, daging, dan produk susu.2.	Pola Makan Teratur: Buat jadwal makan yang teratur dan konsisten agar anak mendapatkan nutrisi yang dibutuhkan setiap hari.3.	Aktivitas Fisik: Ajak anak berolahraga secara rutin untuk mendukung pertumbuhan dan kesehatan secara keseluruhan4.	Konsultasi dengan Dokter: Berkonsultasilah dengan dokter anak untuk memastikan kebutuhan gizi anak terpenuhi dan mendapatkan saran terkait suplemen jika diperlukan.'},
            {'id': 21, 'judul': 'Tips Menjaga Asupan Gizi Anak', 'gambar': 'https://kanjabung.com/wp-content/uploads/2022/09/image-10.png',
                'penulis': 'lactoclub', 'predicted_class': 'stunted', 'isi': 'empat cara untuk mengatasi masalah stunting pada balita, yaitu:1.	Pemberian Pola Asuh yang Tepat: Ini termasuk Inisiasi Menyusui Dini (IMD) dan memberikan ASI eksklusif hingga anak berusia 2 tahun.2.	Memberikan MPASI yang Optimal: Bayi yang berusia 6-23 bulan harus mendapatkan makanan pendamping ASI yang tepat dan optimal, setidaknya 4 kali sehari.3.	Mengobati Penyakit yang Dialami Anak: Penanganan penyakit yang dapat menghambat pertumbuhan anak harus segera dilakukan.4.	Pantau Perkembangan Anak: Memantau perkembangan anak secara berkala dan membawa ke posyandu untuk pemeriksaan rutin.'},
            {'id': 22, 'judul': 'Ketahui Masalah Stunting dan Cara Mengatasi Stunting', 'gambar': 'https://live-69566-healthscience-corporate-id.pantheonsite.io/sites/default/files/1_1.jpg',
                'penulis': 'nestlehealthscience', 'predicted_class': 'several_stunted', 'isi': 'Stunting adalah gangguan pertumbuhan dan perkembangan anak yang disebabkan oleh kekurangan gizi dalam jangka panjang. Anak yang mengalami stunting memiliki tinggi badan yang lebih pendek dari standar usianya1. Masalah ini sering kali terjadi karena malnutrisi pada ibu selama hamil atau pada anak selama masa pertumbuhannya.Penyebab utama stunting meliputi:•	Malnutrisi kronis pada ibu selama kehamilan.•	Anak tidak mendapatkan ASI eksklusif.•	Kualitas gizi MPASI yang kurang.•	Anak menderita penyakit yang menghalangi penyerapan nutrisi.•	Infeksi kronis pada anak.Dampak stunting mencakup gangguan fisik dan perkembangan mental, kekebalan tubuh rendah, gangguan nutrisi, dan prestasi akademik yang rendah. Anak-anak yang stunting juga lebih rentan terhadap penyakit dan memiliki risiko kesehatan yang lebih tinggi di masa dewasa2.Upaya pencegahan dan pengobatan meliputi:•	Peningkatan akses ke pelayanan kesehatan.•	Edukasi dan bimbingan orang tua tentang gizi seimbang.•	Promosi diversifikasi •	Penanggulangan kemiskinan dan peningkatan sanitasi.'},
            {'id': 23, 'judul': 'Stunting pada Anak', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1657531269/attached_image/stunting-0-alodokter.jpg',
                'penulis': 'dr. Meva Nareza T', 'predicted_class': 'several_stunted', 'isi': 'Stunting adalah gangguan pertumbuhan dan perkembangan anak akibat kekurangan gizi dalam jangka panjang, yang membuat anak memiliki tinggi badan lebih pendek dari standar usianya.Penyebab Utama:•	Malnutrisi kronis pada ibu selama kehamilan.•	Anak tidak mendapatkan ASI eksklusif.•	Kualitas gizi MPASI yang kurang.•	Anak menderita penyakit yang menghalangi penyerapan nutrisi.•	Infeksi kronis pada anak.Dampak:•	Gangguan fisik dan perkembangan mental.•	Kekebalan tubuh rendah.•	Prestasi akademik yang rendah.•	Risiko kesehatan lebih tinggi di masa dewasa.Upaya Pencegahan dan Pengobatan:•	Peningkatan akses ke pelayanan kesehatan.•	Edukasi dan bimbingan orang tua tentang gizi seimbang.•	Promosi diversifikasi pangan.•	Penanggulangan kemiskinan dan peningkatan sanitasi.'},
            {'id': 24, 'judul': 'Ahli Gizi: Status gizi perlu dipantau agar anak stunting tak obesitas', 'gambar': 'https://img.antaranews.com/cache/1200x800/2023/10/06/20231005_175434.jpg.webp',
                'penulis': 'Atman Ahdiat', 'predicted_class': 'several_stunted', 'isi': 'Stunting adalah gangguan pertumbuhan dan perkembangan anak akibat kekurangan gizi dalam jangka panjang.Pentingnya Pemantauan Status Gizi: •	Ahli Gizi Masyarakat, dr. Tan Shot Yen, menekankan bahwa status gizi anak perlu terus dipantau agar anak yang terlanjur stunting tidak menjadi obesitas saat bertumbuh dewasa.•	Anak-anak yang stunting harus diperhatikan dengan baik untuk mencegah peningkatan berat badan yang berlebihan.Dampak dari Tidak Pemantauan: •	Anak-anak yang stunting dan diberi pola makan berkalori tinggi dapat mengalami peningkatan berat badan yang tidak sehat, yang dapat berdampak negatif pada perkembangannya.Rekomendasi: •	Status gizi anak harus diperiksa oleh dokter, bukan hanya oleh kader atau bidan.•	Penting untuk memahami bahwa stunting adalah kondisi kompleks yang memerlukan pemantauan dan penanganan yang tepat.'},
            {'id': 25, 'judul': 'RUTF, Makanan Khusus untuk Balita Gizi Buruk', 'gambar': 'https://res.cloudinary.com/dk0z4ums3/image/upload/v1684805402/attached_image/rutf-makanan-khusus-untuk-balita-gizi-buruk-0-alodokter.jpg',
                'penulis': 'dr. Airindya Bella', 'predicted_class': 'several_stunted', 'isi': 'RUTF (Ready-to-Use Therapeutic Food) adalah makanan khusus yang kaya energi dan nutrisi, seperti lemak, vitamin, dan mineral. Makanan ini dibuat untuk mengatasi kekurangan nutrisi yang parah pada anak di bawah usia 5 tahun, terutama balita yang mengalami wasting (gizi buruk)1.Keunggulan RUTF:•	Nilai gizi tinggi: Memungkinkan balita dengan gizi buruk mengalami kenaikan berat badan dengan cepat.•	Praktis: Bisa langsung dikonsumsi dari kemasan tanpa perlu diseduh.•	Penyimpanan mudah: Tahan lama dan tidak memerlukan lemari es.•	Rasa dan tekstur cocok: Lebih disukai anak-anak dibandingkan makanan lain.Komposisi Nutrisi:•	Kacang tanah, kacang hijau, kacang merah, kacang kedelai, tempe.•	Suplemen vitamin dan mineral.•	Gula, susu skim, minyak sayur.Dampak dan Manfaat:•	Meningkatkan kesehatan dan pertumbuhan anak-anak yang mengalami wasting.•	Mengurangi risiko infeksi dan meningkatkan kekebalan tubuh.'},
            {'id': 26, 'judul': 'Creating a Nutritious Emergency Food Supply', 'gambar': ' dr. Rizal Fadli',
                'penulis': ' dr. Rizal Fadli', 'predicted_class': 'several_stunted', 'isi': 'Tips Utama:•	Pilih Makanan Tahan Lama: Gunakan makanan yang tidak mudah rusak dan tidak memerlukan penyimpanan es.•	Beli dengan Bijak: Pertimbangkan kebutuhan gizi keluarga dan ketersediaan air.•	Buat Daftar Gizi: Pahami label makanan untuk memastikan kandungan nutrisi yang baik.•	Tambahkan Buah dan Sayuran: Pilih buah dan sayuran kalengan atau tahan lama.•	Pilih Makanan dengan Sodium Rendah: Sodium tinggi dapat meningkatkan kebutuhan air.'},
        ]

        # Cari artikel berdasarkan ID
        article = next(
            (item for item in all_articles if item["id"] == id), None)

        if article:
            return jsonify(article), 200
        else:
            return jsonify({'error': 'Article not found'}), 404

    except Exception as e:
        logging.error(f"Error in article detail route: {e}")
        return jsonify({'error': f'Error in article detail route: {str(e)}'}), 500


if __name__ == '__main__':
    # Gunakan variabel lingkungan PORT dari Cloud Run
    port = int(os.environ.get("PORT", 9898))
    app.run(debug=False, host='0.0.0.0', port=port)
