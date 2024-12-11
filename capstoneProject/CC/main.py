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
            {'id': 1, 'judul': 'Melatih Keterampilan Motorik Anak dengan Permainan',
                'gambar': 'https://fahum.umsu.ac.id/blog/wp-content/uploads/2024/08/penyebab-stunting-pada-anak-dan-cara-mengatasinya-1140x570.jpg', 'penulis': 'dr.kevin Adrian', 'predicted_class': 'tinggi', },
            {'id': 2, 'judul': 'Pentingnya Serat untuk Pencernaan dan Perkembangan Anak', 'gambar': 'https://www.hilo-school.com/wp-content/uploads/2016/07/cara-menambah-tinggi-badan.jpg',
                'penulis': 'dr. Robby Firmansyah Murzen', 'predicted_class': 'tinggi', 'tanggal_dibuat': '2024-07-14'},
            {'id': 3, 'judul': 'Panduan Pemenuhan Gizi Balita Usia 4–5 Tahun',
                'gambar': 'https://akcdn.detik.net.id/visual/2017/09/04/55eb9830-ae53-4273-b626-615d5b0eb639_169.jpg?w=650', 'penulis': 'dr. Rizal Fadli ', 'predicted_class': 'tinggi', 'tanggal_dibuat': '2020-04-18'},
            {'id': 4, 'judul': 'Seberapa Banyak Porsi Makan yang Tepat untuk Anak Usia 5 Tahun?',
                'gambar': 'https://www.ibudanbalita.com/uploads/medias/yohWIfDP3rFp.jpg', 'penulis': 'dr. Damar Upahita', 'predicted_class': 'tinggi', 'tanggal_dibuat': '2024-03-01'},
            {'id': 5, 'judul': 'Hari Gizi Nasional, Inilah Pola Makan Bergizi untuk Si Kecil', 'gambar': 'https://parenting.co.id/img/images/BAYIMAKAN800.jpg',
                'penulis': 'Redaksi Halodoc ', 'predicted_class': 'tinggi', 'tanggal_dibuat': '2023-09-07'},
            {'id': 6, 'judul': 'https://parenting.co.id/img/images/BAYIMAKAN800.jpg', 'gambar': 'https://static.promediateknologi.id/crop/0x0:0x0/0x0/webp/photo/p3/23/2023/12/25/IMG_20231225_044505-2295083804.jpg',
                'penulis': 'Nadhifah', 'predicted_class': 'normal', 'tanggal_dibuat': '2024-03-14'},
            {'id': 7, 'judul': 'Resep Makanan Balita 1-2 Tahun yang Penuh Gizi dan Enak', 'gambar': 'https://i.pinimg.com/736x/c5/c2/ca/c5c2ca670604720df32910a184b52806.jpg',
                'penulis': 'Orami Articles', 'predicted_class': 'normal', 'tanggal_dibuat': '2024-09-11'},
            {'id': 8, 'judul': '5 Cara Mudah Memperkuat Daya Tahan Tubuh Anak', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/02/gizi-balita.jpg',
                'penulis': 'dr. Isman Jafar, Sp.A(K)', 'predicted_class': 'normal', 'tanggal_dibuat': '2024-09-30'},
            {'id': 9, 'judul': 'Rekomendasi Camilan Kreatif untuk Tingkatkan Daya Tahan Tubuh Anak', 'gambar': 'https://kanjabung.com/wp-content/uploads/2022/09/image-10.png',
                'penulis': 'dr. Carla Pramudita Susanto', 'predicted_class': 'normal', 'tanggal_dibuat': '2024-09-11'},
            {'id': 10, 'judul': 'Pertumbuhan Balita', 'gambar': 'https://i0.wp.com/rs.uns.ac.id/wp-content/uploads/2017/04/pertumbuhan-balita-versi-WHO.jpg',
                'penulis': 'dr. Rizal Fadli', 'predicted_class': 'normal', 'tanggal_dibuat': '2024-08-05'},
            {'id': 11, 'judul': 'Ibu Perlu Tahu, Ini 4 Cara Biar Anak Agar Tumbuh Tinggi', 'gambar': 'https://rsudmangusada.badungkab.go.id/uploads/promosi/STUNTING_530430.png',
                'penulis': 'dr. Rizal Fadli', 'predicted_class': 'stunted', 'tanggal_dibuat': '2020-05-06'},
            {'id': 12, 'judul': '7 Makanan Bergizi untuk Mencegah Stunting pada Balita', 'gambar': 'https://cdn-brilio-net.akamaized.net/webp/news/2024/09/11/300754/1200xauto-11-resep-masakan-rumahan-untuk-anak-yang-bergizi-sederhana-enak-dan-cocok-buat-bekal-240911x.jpg',
                'penulis': 'dr. Rizal Fadli', 'predicted_class': 'stunted', 'tanggal_dibuat': '2020-04-18'},
            {'id': 13, 'judul': 'Protein Hewani Penting Untuk Cegah Stunting', 'gambar': 'https://imgx.sonora.id/crop/0x0:0x0/x/photo/2023/06/29/mix-common-food-allergens-people-20230629080537.jpg',
                'penulis': 'rs-jih', 'predicted_class': 'stunted', 'tanggal_dibuat': '2020-05-30'},
            {'id': 14, 'judul': 'Jangan Sampai Telat Bun, Begini Tips Meninggikan Badan Anak Secara Alami', 'gambar': 'https://www.yesdok.com/visual/slideshow/growth-chart-box-stock-image_reduced-image-article-1654414558.jpg',
                'penulis': 'Jujuk Ernawati', 'predicted_class': 'stunted', 'tanggal_dibuat': '2023-07-09'},
            {'id': 15, 'judul': '8 Menu Makanan untuk Stunting: Pencegahan Melalui Gizi Seimbang', 'gambar': 'https://www.nutriclub.co.id/_default_upload_bucket/image-thumb__2636__default/5-Langkah-Mudah-Tingkatkan-Imunitas-si-Kecil-700x278.webp',
                'penulis': 'chubb', 'predicted_class': 'stunted', 'tanggal_dibuat': '2019-01-24'},
            {'id': 16, 'judul': '4 Cara Mengatasi Masalah Stunting pada Balita', 'gambar': 'https://unair.ac.id/wp-content/uploads/2022/11/Ilustrasi-by-Darya-Varia.jpg',
                'penulis': 'dr. Rizal Fadli', 'predicted_class': 'severly_stunted', 'tanggal_dibuat': '2020-09-22'},
            {'id': 17, 'judul': 'Protein Hewani Penting Untuk Cegah Stunting', 'gambar': 'https://joss.co.id/data/uploads/2023/01/Protein-Hewani-Cegah-Stunting-678x381.jpg',
                'penulis': 'rumahsakit', 'predicted_class': 'severly_stunted', 'tanggal_dibuat': '2021-03-04'},
            {'id': 18, 'judul': 'Panduan Memenuhi Kebutuhan Gizi Balita Usia 1-5 Tahun', 'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/02/gizi-balita.jpg?w=1080&q=75',
                'penulis': 'dr. Airindya Bella', 'predicted_class': 'severly_stunted', 'tanggal_dibuat': '2024-04-11'},
            {'id': 19, 'judul': 'Tips Menjaga Asupan Gizi Anak', 'gambar': 'https://kanjabung.com/wp-content/uploads/2022/09/image-10.png',
                'penulis': 'lactoclub', 'predicted_class': 'severly_stunted', 'tanggal_dibuat': '2023-10-06'},
            {'id': 20, 'judul': 'Ketahui Masalah Stunting dan Cara Mengatasi Stunting', 'gambar': 'https://live-69566-healthscience-corporate-id.pantheonsite.io/sites/default/files/1_1.jpg',
                'penulis': 'nestlehealthscience', 'predicted_class': 'several_stunted', 'tanggal_dibuat': '2023-03-12'}
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
            {
                'id': 1,
                'judul': 'Ibu Perlu Tahu, Ini 4 Cara Biar Anak Agar Tumbuh Tinggi',
                'gambar': 'https://fahum.umsu.ac.id/blog/wp-content/uploads/2024/08/penyebab-stunting-pada-anak-dan-cara-mengatasinya-1140x570.jpg',
                'penulis': 'dr. Rizal Fadli',
                'predicted_class': 'tinggi',
                'tanggal_dibuat': '2021-03-04',
                'isi': '''
                <section>
                    <h2>Cara Mengembangkan Keterampilan Motorik Anak</h2>
                    <p>Bayi umumnya mulai belajar keterampilan motorik sejak usia 5–6 bulan. Untuk mengoptimalkan keterampilan motorik Si Kecil, Bunda dan Ayah dapat merangsangnya dengan beberapa permainan berikut:</p>

                    <ol>
                        <li><strong>Menyusun Balok</strong>
                            <p>Permainan sederhana yang dapat melatih keterampilan motorik anak adalah menyusun balok atau mainan pop it. Ketika melakukan permainan tersebut, anak dapat melatih gerakan otot-otot jari tangannya agar bisa menggenggam dan meraih suatu benda dengan baik. Tak hanya itu, permainan ini juga dapat merangsang kemampuan koordinasi gerakan tubuh. Bayi umumnya bisa mulai diajak bermain menyusun balok sejak ia berusia 6 atau 8 bulan.</p>
                        </li>

                        <li><strong>Melukis atau Menggambar</strong>
                            <p>Melalui kegiatan melukis atau menggambar, anak dapat melatih kemampuan jemarinya untuk menggenggam dan menggerakkan kuas. Tak hanya itu, kegiatan ini juga bisa memupuk daya imajinasi dan tingkat kreativitas anak. Beberapa studi juga menunjukkan bahwa anak-anak yang sudah diajarkan untuk melukis atau menggambar sejak kecil memiliki kemampuan belajar dan mengingat yang lebih baik. Hal ini menjadikan kegiatan melukis atau menggambar dapat membuat anak menjadi lebih cerdas.</p>
                        </li>

                        <li><strong>Bermain dengan Adonan</strong>
                            <p>Bunda dan Ayah juga bisa melatih kemampuan motorik Si Kecil melalui permainan berbentuk adonan, seperti lilin atau tanah liat. Selain itu, Bunda juga bisa mengajak Si Kecil bermain dengan adonan kue, jika ia sudah bisa mengonsumsi makanan padat. Dengan menyentuh benda-benda tersebut, Si Kecil akan terlatih untuk menyentuh, mencubit, menekan, dan membentuk adonan sesuai bentuk yang ia sukai. Permainan tersebut bisa membantu Si Kecil mengenal tekstur benda-benda di sekitarnya.</p>
                        </li>

                        <li><strong>Bermain Bola</strong>
                            <p>Keterampilan motorik kasar anak dapat dilatih dengan mengajaknya bermain lempar tangkap bola. Pilihlah bola plastik berukuran sedang yang tidak terlalu berat, sehingga memudahkan anak untuk melempar, menangkap, atau menendangnya. Dengan demikian, anak berlatih menggerakkan tangan dan kakinya untuk mengikuti gerakan bola yang diberikan.</p>
                        </li>

                        <li><strong>Menarik dan Mendorong Mainan</strong>
                            <p>Ketika bayi Anda mulai belajar berjalan, berikan ia mainan yang dapat didorong atau ditarik. Mainan yang dapat digunakan untuk melatihnya menarik dan mendorong, misalnya mainan mobil dan truk besar. Selain itu, Bunda dan Ayah juga bisa mengajak Si Kecil bermain dengan boneka kesukaannya.</p>
                        </li>
                    </ol>

                    <p>Selain dengan beberapa permainan di atas, Bunda dan Ayah juga bisa merangsang keterampilan motorik Si Kecil dengan mengajaknya bermain di luar rumah, misalnya di halaman rumah. Saat bermain di luar rumah, Bunda dan Ayah bisa mengajak Si Kecil bermain bola, mobil-mobilan, atau bermain kejar-kejaran dengan Si Kecil. Bunda dan Ayah juga perlu selalu menemani dan menjaga Si Kecil saat ia bermain karena Si Kecil cenderung suka memasukkan benda asing ke dalam mulutnya. Hal ini berisiko membuatnya tersedak.</p>
                </section>

                <section>
                    <h2>Perkembangan Motorik yang Terhambat</h2>
                    <p>Tumbuh kembang anak satu dengan anak lainnya belum tentu sama. Ada anak yang tumbuh kembangnya normal, namun ada pula yang sedikit lebih lambat dari anak seusianya. Namun, Bunda dan Ayah tidak perlu khawatir dengan hal tersebut karena keterlambatan kemampuan motorik tidak selalu menandakan bahwa ia mengalami masalah tumbuh kembang.</p>
                    <p>Bunda dan Ayah bisa terus mendampingi Si Kecil setiap ia berusaha mencoba hal-hal baru, termasuk ketika kemampuan motoriknya dilatih. Apresiasi kegiatan yang ia lakukan dengan memberikan tepuk tangan atau semangat. Dengan demikian, Si Kecil akan terpacu untuk mencoba hal-hal baru.</p>
                    <p>Namun, jika tumbuh kembang Si Kecil tampak sangat terhambat atau jika Bunda dan Ayah khawatir terhadap kondisinya, cobalah untuk berkonsultasi ke dokter agar dokter dapat mengevaluasi kondisi Si Kecil dan mencari tahu penyebabnya.</p>
                </section>
            '''
            },
            {
                'id': 2,
                'judul': 'Berbagai Cara Menambah Tinggi Badan yang Alami dan Sehat',
                'gambar': 'https://www.hilo-school.com/wp-content/uploads/2016/07/cara-menambah-tinggi-badan.jpg',
                'penulis': 'dr. Robby Firmansyah Murzen',
                'predicted_class': 'tinggi',
                'tanggal_dibuat': '2024-07-14',
                'isi': '''
                    <section>
                        <h2>Berbagai Manfaat Serat untuk Pencernaan dan Perkembangan Anak</h2>
                        <p>Berikut ini adalah berbagai manfaat serat untuk pencernaan dan perkembangan anak:</p>

                        <ol>
                            <li><strong>Mencegah sembelit</strong>
                                <p>Sembelit termasuk salah satu masalah pencernaan yang umum dialami oleh anak-anak. Untuk mengatasi sekaligus mencegah sembelit pada anak, orang tua perlu memberikan asupan serat yang cukup untuk anak. Serat dapat melancarkan proses pencernaan dengan membantu meningkatkan jumlah air di usus. Dengan begitu, tinja yang dibentuk dalam usus akan bertekstur lebih lunak, sehingga buang air besar akan lancar. Selain mengonsumsi serat, mencukupi kebutuhan cairan anak setiap hari dengan konsumsi air putih juga perlu dilakukan untuk mencegah anak dari sembelit.</p>
                            </li>

                            <li><strong>Meningkatkan penyerapan nutrisi dari makanan</strong>
                                <p>Serat juga berperan penting untuk menyerap nutrisi dari makanan yang masuk ke dalam tubuh. Hal ini bukan hanya dapat menjaga kesehatan saluran cerna anak, tetapi juga bermanfaat untuk meningkatkan daya tahan tubuhnya, sehingga tumbuh kembang anak pun bisa optimal.</p>
                            </li>

                            <li><strong>Berperan sebagai prebiotik</strong>
                                <p>Serat juga berperan sebagai prebiotik dalam saluran cerna anak. Nutrisi ini merupakan sumber makanan bagi bakteri baik di usus, sehingga pertumbuhan dan fungsi bakteri tersebut akan selalu terjaga. Hasilnya, pencernaan anak menjadi lebih sehat dan terlindungi dari gangguan pencernaan.</p>
                            </li>

                            <li><strong>Mengontrol kadar gula darah</strong>
                                <p>Asupan serat yang cukup untuk anak dapat mengurangi risiko berbagai gangguan kesehatan di kemudian hari, termasuk diabetes. Seperti yang telah dijelaskan, tubuh tidak bisa menyerap serat sehingga tidak menyebabkan lonjakan gula darah setelah konsumsi makanan yang kaya serat. Oleh karena itu, makanan tinggi serat sangat baik untuk menjaga gula darah tetap normal dan mencegah penyakit diabetes.</p>
                            </li>
                        </ol>

                        <p>Selain manfaat di atas, pentingnya serat bagi anak adalah untuk mencegah ambeien atau wasir, yaitu penyakit yang bisa menimbulkan BAB berdarah. Kondisi ini sering kali disebabkan oleh asupan serat yang kurang.</p>

                        <h3>Sumber dan Jumlah Asupan Serat untuk Anak</h3>
                        <p>Meski serat memiliki manfaat yang baik untuk kesehatan, sering kali anak-anak tidak berselera untuk mengonsumsi makanan yang mengandung serat, baik karena bentuknya yang kurang menarik ataupun rasanya yang tidak familier seperti hidangan lain. Padahal, ada banyak pilihan makanan serat yang lezat. Nah, berikut ini adalah beberapa sumber serat yang bisa menjadi pilihan untuk anak:</p>

                        <ul>
                            <li>Buah-buahan, seperti apel, pisang, dan alpukat</li>
                            <li>Sayur-sayuran seperti wortel, bayam, brokoli, dan kentang</li>
                            <li>Kacang-kacangan seperti kacang polong, kacang hijau, dan kacang almond</li>
                            <li>Biji-bijian, seperti oatmeal, beras merah, dan biji chia</li>
                            <li>Susu formula pertumbuhan yang mengandung prebiotik FOS (frukto-oligosakarida) dan GOS (galakto-oligosakarida)</li>
                        </ul>

                        <p>Bila Si Kecil tidak mau mengonsumsi makanan berserat, Bunda bisa membuat menu makanan yang menarik sekaligus enak. Sebagai contoh, Bunda dapat memberikan es lilin dengan buah utuh di dalamnya, atau menyisipkan buah atau sayur dalam roti dengan saus kesukaan Si Kecil.</p>

                        <p>Selain itu, pastikan juga porsi asupan serat yang dibutuhkan anak-anak. Hal ini umumnya akan berbeda-beda sesuai usia. Anak berumur 1−3 tahun membutuhkan 19 gram serat per hari, yang umumnya bisa terpenuhi dengan konsumsi 1 cangkir buah segar atau sayuran matang. Sedangkan anak usia 4−9 tahun membutuhkan serat sebanyak 20−23 gram per hari. Angka tersebut biasanya dapat diperoleh dari konsumsi 3 cangkir buah atau sayur.</p>

                        <p>Pastikan Bunda memenuhi kebutuhan serat harian Si Kecil sesuai dengan usianya, ya. Selain itu, lengkapi pula asupan nutrisi lainnya, seperti protein, lemak baik, vitamin, dan mineral yang dibutuhkan Si Kecil untuk mendukung tumbuh kembang dan daya tahan tubuhnya.</p>

                        <p>Bila Si Kecil mengonsumsi susu formula pertumbuhan, pilihlah susu dengan kandungan prebiotik FOS dan GOS untuk membantu memenuhi kebutuhan serat harian. Prebiotik ini telah teruji klinis dapat meningkatkan jumlah bakteri baik di usus, yang mana merupakan kunci penting dari pencernaan yang sehat. Kalau pencernaannya sehat, tumbuh kembangnya juga akan lebih optimal.</p>

                        <p>Sebagai pilihan yang lebih sehat untuk Si Kecil, Bunda bisa memilih susu formula pertumbuhan dengan perbandingan FOS dan GOS 1:9, karena ini merupakan kombinasi terbaik serta paling banyak teruji klinis di negara di Asia & Eropa untuk optimalkan kesehatan pencernaan anak.</p>
                    </section>
                '''},
            {
                'id': 3,
                'judul': 'Panduan Pemenuhan Gizi Balita Usia 4–5 Tahun',
                'gambar': 'https://akcdn.detik.net.id/visual/2017/09/04/55eb9830-ae53-4273-b626-615d5b0eb639_169.jpg?w=650',
                'penulis': 'dr. Rizal Fadli ',
                'predicted_class': 'tinggi',
                'tanggal_dibuat': '2020-04-18',
                'isi': '''
                    <section>
                        <h2>Makanan yang Dibutuhkan Anak Usia 4–5 Tahun</h2>
                        <p>Anak yang berusia 4–5 tahun umumnya membutuhkan asupan gizi setidaknya 1.600 kalori (sesuai dengan AKG dari Kementerian Kesehatan RI). Sebenarnya, jenis asupan nutrisi yang dibutuhkan anak pada usia ini tidak berubah, tetapi takarannya harus disesuaikan. Berikut ini rinciannya:</p>

                        <ul>
                            <li><strong>Karbohidrat</strong>
                                <p>Pada usia ini, anak membutuhkan asupan karbohidrat untuk diubah menjadi energi. Sebisa mungkin, pastikan dalam satu hari Si Kecil mendapat asupan karbohidrat sebanyak 220 gram. Ada dua jenis karbohidrat yang perlu diketahui, yaitu karbohidrat sederhana dan kompleks. Karbohidrat sederhana adalah jenis karbohidrat yang paling mudah diserap, hingga kemudian diubah menjadi gula darah. Sementara karbohidrat kompleks adalah jenis karbohidrat yang terbuat dari rantai molekul gula panjang, sehingga perlu waktu lama untuk dicerna. Jenis karbohidrat ini bisa menyediakan tingkat energi yang stabil untuk anak beraktivitas sepanjang hari.</p>
                            </li>

                            <li><strong>Protein</strong>
                                <p>Selain karbohidrat, pastikan juga untuk memenuhi kebutuhan protein anak. Pada usia ini, anak setidaknya membutuhkan sebanyak 35 gram asupan protein setiap hari. Supaya terpenuhi dengan baik, ada dua jenis protein yang bisa orangtua berikan pada si kecil, yaitu protein hewani dan protein nabati.</p>
                            </li>

                            <li><strong>Lemak</strong>
                                <p>Sementara untuk asupan lemak, anak usia 4–5 tahun membutuhkan setidaknya 62 gram setiap hari. Namun hati-hati, tidak sembarang lemak bisa diberikan begitu saja pada anak. Ada beberapa jenis lemak, yaitu lemak baik dan lemak jahat. Anak membutuhkan asupan lemak baik, yaitu lemak tak jenuh tunggal dan asam lemak tak jenuh ganda. Jenis lemak ini bisa didapatkan dari buah alpukat, kacang almond, minyak zaitun, ikan salmon, tofu, dan lainnya.</p>
                            </li>

                            <li><strong>Serat</strong>
                                <p>Anak usia 4–5 tahun membutuhkan asupan serat sebanyak 22 gram dalam satu hari. Untuk memenuhinya, ibu bisa membiasakan agar Si Kecil mengonsumsi setidaknya 2–3 porsi sayuran dan buah setiap harinya. Satu porsi buah adalah satu buah yang berukuran sedang atau dua buah ukuran kecil.</p>
                            </li>

                            <li><strong>Vitamin dan Mineral</strong>
                                <p>Memasuki usia sekolah, asupan vitamin dan mineral pun menjadi lebih penting pada anak. Maka dari itu, pastikan untuk memenuhi kebutuhan vitamin dan mineral anak dalam sehari dengan memberikannya sumber makanan bergizi. Ibu bisa membantu memenuhi kebutuhan vitamin dan mineral anak, di antaranya zat besi, seng, kalsium, natrium, tembaga, vitamin A, vitamin B, serta segudang vitamin dan mineral lainnya.</p>
                            </li>
                        </ul>
                    </section>
                '''
            },
            {
                'id': 4,
                'judul': 'Panduan Makanan Seimbang untuk Balita',
                'gambar': 'https://www.ibudanbalita.com/uploads/medias/yohWIfDP3rFp.jpg',
                'penulis': 'dr. Damar Upahita',
                'predicted_class': 'tinggi',
                'tanggal_dibuat': '2024-03-01',
                'isi': '''
                <section>
                    <h2>Porsi Makan Utama Anak Usia 5 Tahun</h2>
                    <p>Waktu makan utama diberikan tiga kali dalam sehari, saat sarapan, makan siang, dan makan malam. Anda bisa membuat jadwal sarapan pukul 6 pagi, makan siang 11.30, dan makan malam pukul 17.30. Bila sudah memiliki jadwal makan sendiri, lakukan secara teratur dan terencana.</p>
                    <p>Jam makan yang teratur membantu anak mengetahui rasa lapar dan kenyang. Selain itu, hal ini juga membentuk kebiasaan makan anak sampai ia dewasa nanti.</p>

                    <h3>Porsi Makan Selingan Anak Usia 5 Tahun</h3>
                    <p>Camilan atau makan selingan penting untuk memenuhi rasa lapar sebelum jadwal makan berikutnya. Meski sifatnya sebagai makanan selingan, camilan juga harus menyumbang kebutuhan gizi anak. Pemberian porsi camilan pada anak usia 5 tahun setidaknya 2 jam sebelum makan utama. Bila diberikan satu jam lebih cepat, camilan ini bisa merusak nafsu makan si kecil pada makanan utama.</p>
                    <p>Jenis camilan yang bergizi untuk si kecil seperti biskuit, buah, jus, atau kacang-kacangan yang memiliki kepadatan gizi, tidak hanya soal kalori yang tinggi. Ketika Anda memberikan camilan tinggi gula pada si kecil, perhatikan angka kecukupan gizi yang tertera di kemasan.</p>

                    <h3>Porsi Makan Anak Usia 5 Tahun yang Ideal</h3>
                    <p>Berdasarkan Angka Kecukupan Gizi (AKG) 2013 yang dikeluarkan Kementerian Kesehatan RI, kebutuhan kalori anak usia 4-6 tahun adalah 1600 kkal per hari. Berikut contoh pembagian porsi makan anak usia 5 tahun:</p>
                    <ul>
                        <li><strong>Karbohidrat:</strong> Nasi merupakan makanan pokok sebagian besar masyarakat Indonesia. Berdasarkan Data Komposisi Pangan Indonesia, 100 gram nasi putih atau setara dengan satu centong nasi, mengandung 180 kal energi dan 38,9 gram karbohidrat. Bila balita Anda sedang tidak ingin makan nasi, Anda bisa memilih makanan pokok atau sumber karbohidrat lain seperti kentang (100 gram mengandung 62 kal energi dan 13,5 gram karbohidrat) atau roti (100 gram mengandung 248 kal energi).</li>
                    </ul>

                    <h3>Tips Mengatasi Anak Usia 5 Tahun yang Tidak Menghabiskan Porsi Makannya</h3>
                    <ul>
                        <li><strong>Kurangi Konsumsi Makanan Manis:</strong> Memberi camilan memang penting untuk memberi energi tambahan pada anak, tapi makanan manis bisa membuat anak lebih cepat kenyang dan memberi rasa ‘kenyang palsu’. Hindari makanan manis seperti cokelat, permen, dan minuman mengandung gula berlebih untuk menjaga nutrisi tubuh si kecil.</li>
                        <li><strong>Matikan Televisi dan Layar Gadget Lain:</strong> Makan sambil menatap layar atau asyik bermain bisa membuat anak tidak fokus dengan menu makanannya. Berikan aturan bahwa tontonan tidak boleh diberikan saat makan. Ciptakan suasana makan yang menyenangkan agar anak tidak merasa terintimidasi saat melahap makanannya.</li>
                    </ul>
                </section>
                '''
            },
            {
                'id': 5,
                'judul': 'Stunting pada Anak',
                'gambar': 'https://parenting.co.id/img/images/BAYIMAKAN800.jpg',
                'penulis': 'Redaksi Halodoc',
                'predicted_class': 'tinggi',
                'tanggal_dibuat': '2023-09-07',
                'isi': '''
        <section>
            <h2>Peringatan Hari Gizi Nasional</h2>
            <p>Tanggal 25 Januari diperingati sebagai Hari Gizi Nasional yang dibuat untuk sebagai peringatan pengkaderan tenaga gizi Indonesia. Ini diawali dengan berdirinya Sekolah Juru Penerang Makanan pada 26 Januari 1951. Selain itu, Hari Gizi Nasional juga dilakukan sebagai acuan bahwa sangat penting untuk menjaga pola makan bergizi buat Si Kecil yang tak lain adalah masa depan bangsa.</p>

            <h3>Pola Makanan yang Pas untuk Anak</h3>
            <p>Berbicara mengenai makanan yang sesuai dengan kebutuhan anak, pada dasarnya yang paling pas untuk dikonsumsi anak adalah makanan segar, sehat, bukan junk food agar tetap bugar. Tapi, terkadang tidak seperti yang kita harapkan, sebab Si Kecil tidak suka makan makanan sehat dan bergizi. Di sinilah peran orangtua untuk memastikan bahwa Si Kecil makan dengan benar dan mendapatkan semua nutrisi yang diperlukan.</p>

            <h4>Kelompok Makanan yang Disarankan</h4>
            <p>Sejatinya, ada 5 kelompok utama makanan dan minuman yang disarankan untuk dikonsumsi oleh anak, yaitu:</p>
            <ul>
                <li>Buah dan sayur-sayuran</li>
                <li>Kentang, roti, nasi, pasta, dan karbohidrat bertepung lainnya</li>
                <li>Kacang-kacangan, ikan, telur, daging, dan protein lainnya</li>
                <li>Susu dan alternatif</li>
                <li>Minyak</li>
            </ul>

            <h4>Pengaturan Pola Makan untuk Anak</h4>
            <p>Selain memerhatikan jenis makanan, ada pengaturan pola makan dan penyediaan asupan makanan yang sejatinya diperlukan supaya anak dapat terpenuhi kebutuhan gizinya. Hal tersebut meliputi:</p>
            <ul>
                <li>Merencanakan apa yang harus dimakan</li>
                <li>Memasak atau menyiapkan makanan di rumah</li>
                <li>Belanja makanan secara teratur untuk memasok kebutuhan pangan di rumah</li>
                <li>Seleksi terhadap pilihan makanan di luar, di mana sebagian besar adalah kombinasi dari kelompok makanan</li>
            </ul>

            <h4>Perhatian pada Kombinasi Makanan</h4>
            <p>Kombinasi makanan yang tidak cocok dapat membahayakan kesehatan Si Kecil. Konsumsi makanan tertentu mulai mempengaruhi sistem pencernaan Si Kecil. Sistem pencernaan yang tidak dapat berfungsi dengan baik dapat menyebabkan penumpukan zat beracun di dalam tubuh.</p>
        </section>
    '''
            },
            {
                'id': 6,
                'judul': 'Porsi Makan Anak 5 Tahun yang Tepat dan Tidak Berlebihan',
                'gambar': 'https://static.promediateknologi.id/crop/0x0:0x0/0x0/webp/photo/p3/23/2023/12/25/IMG_20231225_044505-2295083804.jpg',
                'penulis': 'Nadhifah',
                'predicted_class': 'normal',
                'tanggal_dibuat': '2024-03-14',
                'isi': '''
        <section>
            <h2>Kunci Sukses Membuat Makanan untuk Anak</h2>
            <p>Salah satu kunci sukses dalam membuat makanan untuk anak adalah dengan menggunakan bahan-bahan yang segar dan tidak terlalu banyak menggunakan bumbu yang tajam. Rasa yang ringan serta tampilan yang menarik juga bisa membuat anak-anak lebih bersemangat untuk makan. Hidangan yang bertekstur lembut dan mudah dikunyah juga lebih disukai oleh anak-anak, terutama mereka yang masih kecil.</p>

            <h3>Resep Makanan untuk Anak</h3>
            <ol>
                <li>
                    <h4>Nasi Goreng Telur</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>2 piring nasi putih</li>
                        <li>1 butir telur</li>
                        <li>1 siung bawang putih, cincang halus</li>
                        <li>1 sdm kecap manis</li>
                        <li>Garam secukupnya</li>
                        <li>Minyak untuk menumis</li>
                    </ul>
                    <p><strong>Cara Memasak:</strong></p>
                    <ol>
                        <li>Panaskan minyak, tumis bawang putih hingga harum.</li>
                        <li>Masukkan telur, orak-arik hingga matang.</li>
                        <li>Tambahkan nasi dan kecap manis, aduk rata.</li>
                        <li>Bumbui dengan garam, aduk hingga semua bahan tercampur rata. Sajikan hangat.</li>
                    </ol>
                </li>

                <li>
                    <h4>Sup Ayam Sayur</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>100 gr daging ayam, potong kecil</li>
                        <li>1 buah wortel, potong dadu</li>
                        <li>50 gr brokoli</li>
                        <li>1 buah kentang, potong dadu</li>
                        <li>2 siung bawang putih, cincang halus</li>
                        <li>500 ml air</li>
                        <li>Garam dan lada secukupnya</li>
                    </ul>
                    <p><strong>Cara Memasak:</strong></p>
                    <ol>
                        <li>Rebus ayam bersama bawang putih hingga matang.</li>
                        <li>Masukkan wortel, kentang, dan brokoli.</li>
                        <li>Tambahkan garam dan lada secukupnya. Masak hingga sayuran empuk.</li>
                    </ol>
                </li>

                <li>
                    <h4>Bubur Ayam Sederhana</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>200 gr beras</li>
                        <li>100 gr daging ayam, suwir</li>
                        <li>2 siung bawang putih, cincang</li>
                        <li>500 ml kaldu ayam</li>
                        <li>Garam dan merica secukupnya</li>
                    </ul>
                    <p><strong>Cara Memasak:</strong></p>
                    <ol>
                        <li>Rebus beras dengan kaldu ayam hingga menjadi bubur.</li>
                        <li>Tumis bawang putih hingga harum, tambahkan ayam suwir.</li>
                        <li>Sajikan bubur dengan ayam suwir di atasnya, taburi garam dan merica secukupnya.</li>
                    </ol>
                </li>

                <li>
                    <h4>Nugget Ayam Sayur</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>200 gr daging ayam, cincang</li>
                        <li>50 gr wortel, parut halus</li>
                        <li>1 butir telur</li>
                        <li>2 sdm tepung terigu</li>
                        <li>Garam dan merica secukupnya</li>
                        <li>Tepung panir untuk pelapis</li>
                    </ul>
                    <p><strong>Cara Memasak:</strong></p>
                    <ol>
                        <li>Campurkan ayam cincang, wortel, telur, dan tepung terigu.</li>
                        <li>Bumbui dengan garam dan merica, aduk hingga rata.</li>
                        <li>Bentuk adonan, balur dengan tepung panir.</li>
                        <li>Goreng hingga keemasan.</li>
                    </ol>
                </li>

                <li>
                    <h4>Omelet Sayur</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>2 butir telur</li>
                        <li>50 gr wortel, parut halus</li>
                        <li>50 gr bayam, cincang halus</li>
                        <li>Garam dan lada secukupnya</li>
                    </ul>
                    <p><strong>Cara Memasak:</strong></p>
                    <ol>
                        <li>Kocok telur, tambahkan wortel dan bayam.</li>
                        <li>Bumbui dengan garam dan lada.</li>
                        <li>Goreng adonan di wajan datar hingga matang sempurna.</li>
                    </ol>
                </li>

                <li>
                    <h4>Bakso Tahu</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>10 buah tahu putih, haluskan</li>
                        <li>100 gr daging ayam, cincang</li>
                        <li>1 butir telur</li>
                        <li>1 sdm tepung terigu</li>
                        <li>Garam dan lada secukupnya</li>
                    </ul>
                    <p><strong>Cara Membuat:</strong></p>
                    <ol>
                        <li>Campurkan tahu, ayam cincang, dan telur.</li>
                        <li>Bumbui dengan garam dan lada, tambahkan tepung terigu.</li>
                        <li>Bentuk bulat-bulat, goreng hingga kecokelatan.</li>
                    </ol>
                </li>
            </ol>
        </section>
    '''
            },
            {
                'id': 7,
                'judul': 'Hari Gizi Nasional, Inilah Pola Makan Bergizi untuk Si Kecil',
                'gambar': 'https://i.pinimg.com/736x/c5/c2/ca/c5c2ca670604720df32910a184b52806.jpg',
                'penulis': 'Orami Articles',
                'predicted_class': 'normal',
                'tanggal_dibuat': '2024-09-11',
                'isi': '''
        <section>
            <h2>Hari Gizi Nasional, Inilah Pola Makan Bergizi untuk Si Kecil</h2>
            <p>Artikel ini menyediakan beberapa resep makanan bergizi dan lezat untuk balita usia 1-2 tahun. Makanan ini dirancang untuk memenuhi kebutuhan nutrisi anak-anak pada usia tersebut.</p>

            <h3>Contoh Resep:</h3>
            <ol>
                <li>
                    <h4>Nugget Bayam</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>Bayam</li>
                        <li>Kacang almond</li>
                        <li>Tepung roti</li>
                        <li>Telur</li>
                        <li>Oregano</li>
                        <li>Garam</li>
                        <li>Keju parut</li>
                    </ul>
                    <p><strong>Cara Membuat:</strong></p>
                    <ol>
                        <li>Bayam dicacah dan dicampur dengan kacang almond, oregano, garam, dan keju parut.</li>
                        <li>Adonan dibentuk nugget, digoreng hingga matang, dan disajikan.</li>
                    </ol>
                </li>

                <li>
                    <h4>Sup Krim Brokoli</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>Brokoli</li>
                        <li>Krim</li>
                        <li>Bawang putih</li>
                        <li>Bawang merah</li>
                        <li>Garam</li>
                        <li>Kaldu bubuk</li>
                    </ul>
                    <p><strong>Cara Membuat:</strong></p>
                    <ol>
                        <li>Brokoli dan bawang putih diolah dalam sup krim.</li>
                        <li>Masak hingga matang, kemudian disajikan hangat.</li>
                    </ol>
                </li>

                <li>
                    <h4>Puff Ubi Jalar</h4>
                    <p><strong>Bahan:</strong></p>
                    <ul>
                        <li>Ubi jalar</li>
                        <li>Minyak sayur</li>
                        <li>Yoghurt</li>
                        <li>Sereal bayi</li>
                        <li>Tepung</li>
                    </ul>
                    <p><strong>Cara Membuat:</strong></p>
                    <ol>
                        <li>Ubi jalar dicampur dengan yoghurt dan minyak sayur.</li>
                        <li>Adonan dibentuk dan dipanggang.</li>
                    </ol>
                </li>
            </ol>
        </section>
    '''
            },
            {
                'id': 8,
                'judul': 'Ini Peran Protein dalam Tumbuh Kembang Anak',
                'gambar': 'https://cdn.hellosehat.com/wp-content/uploads/2020/02/gizi-balita.jpg',
                'penulis': 'dr. Fadhli Rizal Makarim',
                'predicted_class': 'normal',
                'tanggal_dibuat': '2024-09-30',
                'isi': '''
        <section>
            <h2>Peran Protein dalam Tumbuh Kembang Anak</h2>
            <p>Protein memiliki peran yang sangat penting dalam tumbuh kembang anak. Sebagai salah satu makronutrisi utama, protein berfungsi untuk membangun dan memperbaiki jaringan tubuh, memproduksi enzim dan hormon, serta mendukung pertumbuhan otot, kulit, rambut, dan organ tubuh lainnya.</p>

            <h3>Peran Penting Protein dalam Tumbuh Kembang Anak:</h3>
            <ol>
                <li><strong>Pertumbuhan dan Perkembangan:</strong> Protein sangat dibutuhkan untuk pertumbuhan sel dan jaringan tubuh yang sehat. Anak-anak yang mendapatkan cukup protein akan memiliki perkembangan fisik yang optimal, termasuk tinggi badan dan berat badan yang sehat.</li>
                <li><strong>Perbaikan Jaringan Tubuh:</strong> Protein membantu dalam perbaikan jaringan tubuh yang rusak akibat aktivitas sehari-hari atau cedera. Ini sangat penting untuk mendukung pemulihan tubuh anak setelah sakit atau cedera.</li>
                <li><strong>Meningkatkan Imunitas:</strong> Protein juga berperan dalam meningkatkan sistem kekebalan tubuh anak. Antibodi yang melawan infeksi tubuh terbuat dari protein, sehingga konsumsi protein yang cukup dapat membantu anak terhindar dari penyakit.</li>
                <li><strong>Memperbaiki Fungsi Otak:</strong> Protein juga mendukung fungsi otak dengan meningkatkan konsentrasi dan daya ingat anak. Asam amino yang terkandung dalam protein berperan dalam sintesis neurotransmiter yang diperlukan untuk komunikasi antar sel saraf di otak.</li>
            </ol>

            <h3>Sumber Protein yang Baik untuk Anak:</h3>
            <p>Berikut adalah beberapa sumber protein yang baik untuk anak:</p>
            <ul>
                <li>Protein hewani seperti daging ayam, ikan, telur, dan susu.</li>
                <li>Protein nabati seperti tahu, tempe, kacang-kacangan, dan biji-bijian.</li>
                <li>Sumber protein lainnya seperti produk susu dan yogurt yang mengandung kalsium dan vitamin D yang juga penting bagi kesehatan tulang anak.</li>
            </ul>

            <p>Penting untuk memastikan bahwa anak mendapatkan asupan protein yang cukup dalam makanan sehari-hari, dengan variasi yang seimbang antara protein hewani dan nabati untuk mendukung tumbuh kembangnya secara optimal.</p>
        </section>
    '''
            },
            {
                'id': 9,
                'judul': 'Jangan Sampai Telat Bun, Begini Tips Meninggikan Badan Anak Secara Alami',
                'gambar': 'https://kanjabung.com/wp-content/uploads/2022/09/image-10.png',
                'penulis': 'Jujuk Ernawati',
                'predicted_class': 'normal',
                'tanggal_dibuat': '2024-09-11',
                'isi': '''
        <section>
            <h2>Tips Meninggikan Badan Anak Secara Alami</h2>
            <p>Meninggikan badan anak merupakan salah satu perhatian banyak orang tua. Salah satu faktor kunci dalam pertumbuhan tinggi badan anak adalah asupan nutrisi yang tepat. Berikut adalah beberapa nutrisi penting yang harus ada dalam makanan anak Anda untuk mendukung tumbuh kembang yang optimal:</p>

            <h3>Nutrisi Penambah Daya Tahan Tubuh Anak:</h3>
            <ul>
                <li><strong>Vitamin C:</strong> Berperan sebagai antioksidan yang menjaga kesehatan secara keseluruhan dan meningkatkan sistem imunitas tubuh.</li>
                <li><strong>Vitamin E:</strong> Melindungi jaringan dan sel-sel tubuh dari kerusakan serta menjaga kesehatan sel darah merah.</li>
                <li><strong>Zinc:</strong> Membantu pertumbuhan sel, metabolisme, serta mencegah stunting.</li>
                <li><strong>Vitamin D:</strong> Menguatkan tulang dan gigi, serta menyerap kalsium yang dibutuhkan tubuh.</li>
                <li><strong>Selenium:</strong> Menjaga kesehatan pembuluh darah, jantung, otot, dan jaringan kulit, serta mencegah kanker.</li>
                <li><strong>Betakaroten:</strong> Sebagai sumber vitamin A yang penting untuk fungsi kekebalan tubuh, kesehatan kulit, dan penglihatan.</li>
                <li><strong>Protein:</strong> Berfungsi untuk membentuk dan memelihara jaringan tubuh, seperti otot, organ, hingga sistem kekebalan tubuh.</li>
                <li><strong>Prebiotik:</strong> Berperan sebagai makanan untuk bakteri baik (probiotik) di saluran cerna dan meningkatkan jumlah bakteri baik sehingga tubuh menjadi lebih sehat.</li>
            </ul>

            <h3>Camilan Penambah Daya Tahan Tubuh Anak:</h3>
            <p>Berikut adalah beberapa rekomendasi camilan lezat yang bisa Anda buat di rumah sebagai penambah daya tahan tubuh anak:</p>
            <ol>
                <li><strong>Ubi Panggang dengan Ghee:</strong> Iris ubi jalar, olesi dengan ghee, lalu panggang hingga matang. Ghee kaya lemak sehat dan ubi jalar mengandung serat tinggi yang baik untuk tubuh.</li>
                <li><strong>Pisang dengan Mentega Almon:</strong> Potong pisang dan oleskan mentega almon di atasnya. Ini adalah camilan prebiotik yang lezat dan mudah dibawa ke mana saja.</li>
                <li><strong>Kimchi:</strong> Kudapan fermentasi dari sawi putih dan kol yang kaya vitamin A, B, C, serta bakteri baik yang dapat mencegah infeksi jamur dan kanker.</li>
                <li><strong>Smoothie Yoghurt:</strong> Campurkan yoghurt rendah lemak dengan buah segar dan madu untuk membuat smoothie. Bekukan untuk membuat es loli yang disukai anak-anak.</li>
                <li><strong>Popcorn:</strong> Popcorn tinggi serat dan biji-bijian. Masak biji jagung popcorn dengan sedikit minyak zaitun dan taburi dengan keju parmesan.</li>
                <li><strong>Camilan Protein:</strong> Sajikan keju rendah lemak dalam tusuk gigi atau buat tortilla gandum yang digulung dengan keju dan sayuran seperti selada dan tomat.</li>
            </ol>

            <p>Dengan memperhatikan konsumsi makanan bergizi dan camilan sehat, anak Anda bisa mendapatkan daya tahan tubuh yang lebih baik dan mendukung proses tumbuh kembangnya secara alami.</p>
        </section>
    '''
            },
            {
                'id': 10,
                'judul': '7 Makanan Bergizi untuk Mencegah Stunting pada Balita',
                'gambar': 'https://i0.wp.com/rs.uns.ac.id/wp-content/uploads/2017/04/pertumbuhan-balita-versi-WHO.jpg',
                'penulis': 'dr. Rizal Fadli',
                'predicted_class': 'normal',
                'tanggal_dibuat': '2024-08-05',
                'isi': '''
        <section>
            <h2>7 Makanan Bergizi untuk Mencegah Stunting pada Balita</h2>

            <h3>Tahap Tumbuh Kembang Balita yang Ideal</h3>
            <p>Tumbuh kembang anak dapat diperhatikan dari dua aspek, yaitu:</p>
            <ul>
                <li><strong>Pertumbuhan:</strong> Perubahan fisik pada anak.</li>
                <li><strong>Perkembangan:</strong> Kemampuan struktur dan fungsi tubuh yang lebih kompleks.</li>
            </ul>
            <p>Memasuki masa balita, anak akan mulai mampu mengasimilasi informasi dari lingkungan sekitarnya melalui indera seperti penglihatan, pendengaran, perabaan, dan aktivitas motorik. Proses ini merupakan bagian penting dalam perkembangan anak untuk memahami dan berinteraksi dengan dunia di sekitarnya.</p>

            <h3>Faktor yang Menyebabkan Balita Terlihat Lebih Besar atau Lebih Kecil</h3>
            <ul>
                <li><strong>Genetik:</strong> Faktor genetik dari orang tua dapat mempengaruhi ukuran tubuh anak.</li>
                <li><strong>Nutrisi yang Tidak Tepat:</strong> Kekurangan gizi dapat menyebabkan pertumbuhan yang terhambat.</li>
                <li><strong>Masalah pada Hormon Pertumbuhan:</strong> Kelebihan atau kekurangan hormon pertumbuhan dapat mempengaruhi pertumbuhan anak.</li>
                <li><strong>Gangguan Tiroid:</strong> Penyakit tiroid seperti hipotiroidisme dapat mempengaruhi pertumbuhan.</li>
                <li><strong>Penyakit Sistemik:</strong> Penyakit kronis dapat menghambat proses pertumbuhan karena tubuh "terbakar" melawan penyakit.</li>
                <li><strong>Gagal untuk Berkembang:</strong> Penyebab kegagalan tumbuh bervariasi dan dapat berasal dari kondisi medis tertentu.</li>
                <li><strong>Kesehatan Ibu Selama Kehamilan:</strong> Kondisi ibu selama kehamilan, seperti merokok atau kurangnya pola makan yang baik, dapat mempengaruhi pertumbuhan anak.</li>
                <li><strong>Jenis Kelamin Bayi:</strong> Bayi perempuan cenderung sedikit lebih kecil daripada bayi laki-laki saat lahir.</li>
                <li><strong>Diberi ASI atau Susu Formula:</strong> Bayi yang diberi ASI dan susu formula memiliki pola pertumbuhan yang berbeda pada tahun pertama.</li>
                <li><strong>Pola Tidur:</strong> Tidur yang cukup dapat meningkatkan percepatan pertumbuhan anak.</li>
            </ul>

            <h3>Bagaimana Agar Balita Memiliki Tubuh Sehat?</h3>
            <p>Agar kesehatan tubuhnya senantiasa terjaga, berikut beberapa cara yang bisa orangtua lakukan:</p>
            <ul>
                <li>Berikan air putih dan susu biasa, hindari minuman manis.</li>
                <li>Pastikan anak makan makanan sehat dan terus coba makanan baru untuk memperkenalkan variasi gizi.</li>
                <li>Batasi waktu penggunaan gadget atau menonton TV.</li>
                <li>Biarkan balita aktif bergerak dan bermain untuk mengembangkan koordinasi tubuh.</li>
                <li>Pastikan anak mendapatkan tidur yang cukup, sesuai usia.</li>
            </ul>

            <h3>Pola Asuh Anak yang Positif</h3>
            <p>Berikut adalah beberapa hal yang orang tua dapat lakukan untuk mendukung tumbuh kembang anak:</p>
            <ul>
                <li>Bacakan buku cerita setiap hari.</li>
                <li>Latih kemampuan bahasa anak dengan berbicara dan mengenalkan kata-kata baru.</li>
                <li>Dorong kemandirian anak dengan membiarkannya berpakaian atau menyuap makanan sendiri.</li>
                <li>Ajarkan rasa ingin tahu dan eksplorasi melalui kegiatan luar ruangan atau kunjungan lapangan.</li>
            </ul>
        </section>
    '''
            },
            {
                'id': 11,
                'judul': 'Resep Makanan Balita 1-2 Tahun yang Penuh Gizi dan Enak',
                'gambar': 'https://rsudmangusada.badungkab.go.id/uploads/promosi/STUNTING_530430.png',
                'penulis': 'Orami Articles',
                'predicted_class': 'stunted',
                'tanggal_dibuat': '2020-05-06',
                'isi': '''
        <section>
            <h2>Resep Makanan Balita 1-2 Tahun yang Penuh Gizi dan Enak</h2>

            <p>Ibu mana sih yang enggak kepingin anaknya tumbuh sehat dengan tinggi badan yang ideal? Sayangnya, tak semua anak beruntung mendapatkannya. Sebab, ada beragam hal yang bisa membuat pertumbuhan tinggi badan anak jadi tertunda.</p>
            <p>Lantas, bagaimana sih menambah tinggi badan anak? Nah, berikut ini beberapa upaya yang bisa ibu lakukan untuk mengoptimalkan tinggi badan anak:</p>

            <h3>1. Harus Makanan Bergizi Seimbang</h3>
            <p>Makanan bergizi seimbang merupakan syarat utama untuk mengoptimalkan tinggi badan anak. Gizi seimbang adalah susunan pangan yang mengandung zat gizi sesuai dengan kebutuhan tubuh. Makanan yang membantu memenuhi kebutuhan ini antara lain: kacang, daging ayam, sayuran hijau, yoghurt, telur, buah-buahan, dan ikan salmon.</p>
            <p>Selain makanan, nutrisi juga bisa didapatkan dari suplemen yang tepat. Kini, ibu bisa mendapatkan suplemen dan vitamin anak dari rumah melalui layanan seperti Halodoc.</p>

            <h3>2. Berikan Susu</h3>
            <p>Susu mengandung protein, magnesium, zink, lemak, dan berbagai mineral penting lainnya yang mendukung pertumbuhan tinggi badan anak. Pilih susu yang mengandung protein berkualitas dan asam amino esensial. Untuk informasi lebih lanjut, konsultasikan pada dokter anak melalui layanan seperti Halodoc.</p>

            <h3>3. Ajak untuk Berolahraga</h3>
            <p>Olahraga membantu memperkuat otot, tulang, dan meningkatkan produksi hormon pertumbuhan (HGH). Anak-anak sebaiknya berolahraga setidaknya 60 menit sehari, sedangkan usia prasekolah 120 menit per hari.</p>
            <p>Olahraga yang efektif termasuk berenang, bermain basket, dan lompat tali. Aktivitas ini mempercepat pertumbuhan anak.</p>

            <h3>4. Perhatikan Jadwal Tidurnya</h3>
            <p>Tidur sangat penting karena tubuh menghasilkan hormon pertumbuhan (HGH) selama tidur. Berikut durasi tidur yang disarankan untuk anak berdasarkan National Sleep Foundation:</p>
            <ul>
                <li>Bayi baru lahir (0–3 bulan): 14–17 jam</li>
                <li>Bayi (4–11 bulan): 12–15 jam</li>
                <li>Balita (1–2 tahun): 11–14 jam</li>
                <li>Balita prasekolah (3–5 tahun): 10–13 jam</li>
                <li>Anak usia sekolah (6–13 tahun): 9–11 jam</li>
                <li>Remaja (14–17 tahun): 8–10 jam</li>
            </ul>
            <p>Tidur yang cukup sangat mendukung pertumbuhan optimal anak.</p>
        </section>
    '''
            },
            {
                'id': 12,
                'judul': 'Resep Masakan Rumahan untuk Anak yang Bergizi, Sederhana, Enak, dan Cocok Buat Bekal',
                'gambar': 'https://i.pinimg.com/originals/bb/bc/31/bbbc31e28e1de49deef1f8be9968ca99.jpg',
                'penulis': 'Nadhifah',
                'predicted_class': 'stunted',
                'tanggal_dibuat': '2020-04-18',
                'isi': '''
        <section>
            <h2>Resep Masakan Rumahan untuk Anak yang Bergizi, Sederhana, Enak, dan Cocok Buat Bekal</h2>

            <p>Makanan bergizi seringkali digambarkan sebagai makanan mahal dari luar negeri. Namun, orang tua bisa memanfaatkan makanan lokal seperti tempe, ati ayam, dan telur yang kaya protein dan gizi lainnya yang dibutuhkan anak-anak untuk tumbuh sehat.</p>

            <h3>1. Tempe dan Tahu</h3>
            <p>Tempe dan tahu adalah sumber protein nabati yang murah dan kaya akan zat besi yang penting untuk tubuh anak. Tempe mengandung 14 gram protein per 100 gram, dan tahu mengandung 10,9 gram protein. Keduanya mendukung energi tubuh, meningkatkan sistem imun, dan menjaga kesehatan tulang.</p>

            <h3>2. Kacang-kacangan</h3>
            <p>Kacang-kacangan seperti kacang hijau dan kacang tanah kaya akan protein dan nutrisi lainnya. Kacang hijau mengandung 8,7 gram protein per 100 gram, sedangkan kacang tanah mengandung 9 gram protein per seperempat cangkir.</p>

            <h3>3. Telur</h3>
            <p>Telur adalah sumber protein yang baik untuk ibu dan anak. Telur mengandung asam amino yang penting bagi perkembangan otak dan tubuh. Pastikan telur dimasak dengan baik untuk menghindari risiko kontaminasi bakteri.</p>

            <h3>4. Hati Ayam</h3>
            <p>Hati ayam mengandung lebih banyak protein (27,4 gram per 100 gram) dibandingkan daging ayam. Hati ayam juga kaya vitamin B12 dan B6, yang baik untuk perkembangan anak-anak dan ibu hamil.</p>

            <h3>5. Ikan</h3>
            <p>Ikan kembung adalah pilihan yang terjangkau untuk mencegah stunting pada anak. Ikan ini kaya akan vitamin B dan D yang penting untuk kesehatan jantung, otak, dan tulang anak.</p>

            <h3>6. Buah</h3>
            <p>Buah seperti pisang dan jeruk adalah sumber vitamin dan mineral yang penting. Kemenkes RI menyarankan buah-buahan sebagai bagian dari menu gizi seimbang untuk mencegah stunting.</p>

            <h3>7. Sayuran</h3>
            <p>Sayuran seperti bayam dan kacang panjang mengandung nutrisi yang baik untuk pencernaan, kesehatan tulang, dan mencegah obesitas pada anak.</p>
        </section>
    '''
            },
            {
                "id": 13,
                "judul": "Mineral dan Vitamin Anak yang Penting bagi Pertumbuhan",
                "gambar": "https://imgx.sonora.id/crop/0x0:0x0/x/photo/2023/06/29/mix-common-food-allergens-people-20230629080537.jpg",
                "penulis": "dr. Meva Nareza T",
                "predicted_class": "stunted",
                'tanggal_dibuat': '2020-05-30',
                "isi": "<p>Stunting masih menjadi masalah kesehatan serius yang di hadapi Indonesia. Upaya yang dilakukan oleh Kementerian Kesehatan, salah satunya adalah dengan mengangkat tema “Protein Hewani Cegah Stunting”.</p>\n\n<p>Gangguan pertumbuhan janin dalam kandungan menjadi salah satu penyebab utama anak lahir stunting, salah satunya karena komponen gizi. Protein hewani adalah gizi yang dibutuhkan oleh ibu hamil guna mencegah stunting pada anak, hal ini dikarenakan pangan hewani mempunyai kandungan zat gizi yang lengkap, kaya protein hewani dan vitamin yang sangat penting dalam mendukung pertumbuhan dan perkembangan.</p>\n\n<p>Berikut ini beberapa sumber protein hewani yang bisa SahabatJIH olah untuk MPASI anak untuk mencegah stunting.</p>\n\n<ul>\n    <li><strong>Daging ayam</strong>. Kandungan protein, zat besi, magnesium, vitamin, dan fosfor pada daging ayam sangat penting untuk mendukung tumbuh kembang si kecil. Tak hanya itu, kandungan kolin dan vitamin C-nya dapat meningkatkan perkembangan otak anak.</li>\n    <li><strong>Ikan</strong>. Ikan merupakan makanan tinggi protein yang kaya manfaat dengan harga yang biasanya lebih terjangkau dibandingkan daging sapi atau ayam. Ikan juga mengandung asam lemak omega 3 yang mampu mengoptimalkan perkembangan otak anak pada periode emas pertumbuhannya.</li>\n    <li><strong>Telur</strong>. Selain mudah didapatkan, telur merupakan makanan yang mengandung nutrisi komplet untuk bayi hingga orang dewasa. Dalam satu butir telur, mengandung 75 kalori, 7 gram protein tinggi, zat besi, lemak, dan vitamin.</li>\n    <li><strong>Daging sapi</strong>. Daging sapi adalah makanan kaya protein, zat besi, dan asam folat yang dapat mengoptimalkan tumbuh kembang anak. Adanya kandungan zat besi pada daging sapi juga bisa membantu mencegah anemia yang berisiko menyebabkan stunting.</li>\n</ul>\n\n<p>Tak hanya memberikan protein hewani pada anak, berat dan tinggi badan anak juga harus dipantau secara berkala oleh Dokter Spesialis Anak Rumah Sakit “JIH”. Ini penting untuk melihat keberhasilan intervensi sekaligus upaya deteksi dini masalah kesehatan gizi sehingga tidak terlambat ditangani.</p>"
            },
            {
                "id": 14,
                "judul": "Nutrisi Dukung Anak Tumbuh Tinggi",
                "gambar": "https://www.yesdok.com/visual/slideshow/growth-chart-box-stock-image_reduced-image-article-1654414558.jpg",
                "penulis": "nestlehealthscience",
                "predicted_class": "stunted",
                'tanggal_dibuat': '2023-07-09',
                "isi": "<p>Meski faktor genetika menjadi penentu tinggi badan anak, namun ada faktor lain yang bisa diusahakan untuk bisa membantu pertumbuhan tubuh buah hati Bunda. Biasanya sih, remaja dalam masa pubertas yang cenderung khawatir tentang tinggi badannya, lho Bun.</p>\n\n<p>Sepanjang sejarah hingga sekarang, dokter, perusahaan dan peneliti telah menawarkan sejumlah perawatan untuk menambah tinggi seseorang. Jadi sebenarnya adakah metode yang bisa membantu menambah tinggi badan?</p>\n\n<p>Dikutip dari Flo Health, ada banyak faktor yang menentukan tinggi badan. Selain genetika, lingkungan dan gaya hidup ikut berperan dalam pertumbuhan masa kanak-kanak hingga remaja.</p>\n\n<p>Misalnya, nutrisi yang juga punya peran dalam menentukan tinggi badan. Para ilmuwan berteori bahwa nutrisi yang baik bisa menjadi alasan utama rata-rata tinggi seseorang meningkat signifikan selama beberapa abad terakhir ini. Itu mengapa penting untuk memberikan anak-anak makanan yang baik mulai dari bayi hingga dewasa.</p>\n\n<p>Tulang tumbuh aktif saat kanak-kanak, namun mulai pubertas, perubahan hormon akan membuat pelat pertumbuhan (lempeng epifis atau area tulang rawan khusus di dekat ujung tulang) mengeras dan menutup, sehingga pertumbuhan tulang berhenti. Area itu biasanya berhenti berkembang sepenuhnya sekitar usia 16 tahun pada anak perempuan, dan pada anak laki-laki antara usia 14-19 tahun.</p>\n\n<p>Ketika dewasa, anak masih bisa mengalami variasi pertumbuhan tinggi badan tapi sangat sedikit. Lalu bagaimana cara alami untuk menambah tinggi badan?</p>\n\n<p>Ada banyak situs yang menjelaskan bahwa peregangan dan olahraga tertentu menjadi kunci menambah tinggi badan. Bahkan ada pakar yang menyarankan untuk melakukan olahraga memanjat dan menggantung, berenang dan lainnya. Namun, tak ada metode ilmiah yang mendukung metode tersebut.</p>\n\n<p>Beberapa aktivitas tersebut bisa menyebabkan cakram intervertebralis terkompresi, sehingga bisa menambah tinggi badan sedikit. Apalagi ditambah dengan peregangan otot membuat mereka yakin bahwa tubuh akan semakin tinggi. Namun kenyataannya tak ada cara ajaib untuk membuat tubuh menjadi lebih tinggi dengan cara cepat.</p>\n\n<p><strong>Prosedur medis</strong></p>\n\n<p>Prosedur pembedahan yang disebut disraksi osteogenesis bisa membuat pasien tumbuh lebih tinggi, bahkan ketika sudah dewasa. Prosedur ini awalnya untuk mengobati dwarfisme atau tubuh kerdil.</p>\n\n<p>Selama prosedur dilakukan, dokter bedah akan mematahkan tulang kaki pasien. Setelah itu, ujung-ujung tulang yang patah dipisahkan, dengan menggunakan alat yang disebut dengan Ilizarov. Ilizarov yang dikembangkan oleh Gabriel Abramovic Ilizarov merupakan alat eksternal fiksasi yang berfungsi untuk menjaga agar tidak terjadi pergeseran dan membantu dalam proses pemanjangan tulang.</p>\n\n<p>Proses pemanjangan tulang ini setidaknya membutuhkan satu bulan perawatan untuk setiap 1 centimeter (cm) pertumbuhan. Namun, prosedur ini menyakitkan dan bisa menimbulkan trauma kepada pasiennya.</p>\n\n<p>Pasien yang menjalani prosedur ini juga harus belajar berjalan lagi setelah tulangnya sembuh. Operasi ini pun berisiko menimbulkan komplikasi tingkat tinggi, termasuk infeksi, penyakit sendi hingga masalah psikologis.</p>\n\n<p><strong>Cara Alami</strong></p>\n\n<p>Tak perlu lewat medis, Bunda bisa melakukan hal lain yang lebih alami jika ingin memastikan buah hati bisa mencapai potensi pertumbuhan tinggi badan maksimal mereka. Beberapa hal yang bisa dilakukan dikutip dari WikiHow, yakni:</p>\n\n<ul>\n    <li><strong>Makan seimbang</strong>\n    <p>Nutrisi adalah hal yang penting. Dari anak lahir, Bunda bisa meningkatkan asupan gizi yang cukup. Misalnya, dengan memberikan air susu ibu (ASI) sejak dini.</p>\n    <p>Ketika bayi sudah semakin besar, Bunda harus mempertahankan pola makan seimbang. Contohnya, memberikan protein tanpa lemak, seperti kacang-kacangan, yang membantu meningkatkan pertumbuhan tulang dan otot yang sehat. Sementara karbohidrat seperti pizza, kue, makanan manis dan soda harus dihindari.</p>\n    <p>Konsumsi banyak kalsium dalam sayuran hijau dan cukup zinc. Selain itu, cukup mendapatkan vitamin D yang dapat meningkatkan pertumbuhan tulang dan otot anak. Vitamin D bisa didapatkan dengan cara berjemur diri di bawah sinar matahari pada pagi hari selama 15 menit.</p>\n    </li>\n    <li><strong>Olahraga</strong>\n    <p>Bunda bisa memberikan latihan yang sesuai dengan usia anak demi memastikan mereka mencapai potensi fisiknya. Melakukan olahraga teratur sekitar 60 menit bisa membantu tubuh lebih tingi selama masa remaja.</p>\n    <p>Untuk membuatnya termotivasi olahraga, ikutkan pada kegiatan ekstrakulikuler olahraga di sekolah atau melatihnya di tempat gym. Namun, anak juga bisa dilatih untuk lebih banyak berjalan dibanding menggunakan alat transportasi bila jarak tempuh tidak begitu jauh.</p>\n    </li>\n    <li><strong>Tidur cukup</strong>\n    <p>Pastikan anak-anak cukup tidur sehingga tubuh mereka cukup istirahat dan tetap menjaga energinya. Anak remaja atau belum dewasa bisa tidur 9-11 jam setiap malam. Hormon pertumbuhan manusia (HGH) diproduksi secara alami dalam tubuh, terutama ketika sedang tidur nyenyak.</p>\n    </li>\n    <li><strong>Jangan hambat pertumbuhan</strong>\n    <p>Berusaha untuk tidak menghambat pertumbuhan anak. Misalnya, kekurangan gizi, minum obat-obatan dan alkohol yang bisa menghambat pertumbuhan jika dikonsumsi saat masih anak-anak.</p>\n    <p>Selain itu, hindari anak dari rokok atau paparan asap"
            },
            {
                "id": 15,
                "judul": "Langkah Mudah Meningkatkan Imunitas Anak",
                "gambar": "https://res.cloudinary.com/dk0z4ums3/image/upload/v1594622096/attached_image/ini-makanan-sehat-yang-perlu-dikonsumsi-setiap-hari.jpg",
                "penulis": "dr. Isman Jafar, Sp.A (K)",
                "predicted_class": "stunted",
                'tanggal_dibuat': '2019-01-24',
                "isi": "<p>Stunting adalah masalah pertumbuhan yang sering terjadi pada anak-anak di bawah lima tahun, yang memiliki dampak signifikan terhadap perkembangan fisik dan kognitif mereka. Di Indonesia, stunting masih menjadi isu kesehatan yang serius. Bahkan, data Kementerian Kesehatan pada tahun 2021 menunjukkan bahwa 24,4% balita mengalami stunting. Tentu ini merupakan angka yang cukup tinggi dan memerlukan perhatian khusus.</p>\n\n<p>Berbagai macam upaya pun terus dilakukan oleh pemerintah, salah satunya mengenai menu makanan untuk stunting.</p>\n\n<h3>Menu Makanan Bergizi untuk Mencegah Stunting pada Anak</h3>\n\n<p>Dalam mencegah stunting, penting untuk memilih makanan yang mengandung nutrisi penting bagi pertumbuhan dan perkembangan anak. Berikut adalah penjelasan lebih rinci mengenai nutrisi yang terkandung dalam beberapa jenis makanan untuk stunting yang direkomendasikan:</p>\n\n<ul>\n    <li><strong>Kacang-kacangan</strong><p>Kacang-kacangan seperti kacang hijau dan kacang merah mengandung protein nabati yang penting untuk pembentukan jaringan tubuh. Selain itu, kacang-kacangan juga mengandung zat besi dan serat yang dapat membantu meningkatkan penyerapan nutrisi dan memperbaiki pencernaan anak.</p></li>\n\n    <li><strong>Daging Ayam</strong><p>Daging ayam merupakan sumber protein hewani yang mudah dicerna oleh tubuh anak-anak. Protein diperlukan untuk pertumbuhan otot, kulit, rambut, dan jaringan tubuh lainnya. Selain itu, daging ayam juga mengandung zat besi dan vitamin B kompleks yang penting untuk kesehatan darah dan sistem saraf.</p></li>\n\n    <li><strong>Telur</strong><p>Telur mengandung protein lengkap yang mengandung semua asam amino esensial yang dibutuhkan tubuh manusia. Selain itu, telur juga mengandung kolin, vitamin B12, zat besi, dan seng yang penting untuk perkembangan otak dan fungsi kognitif anak.</p></li>\n\n    <li><strong>Ikan</strong><p>Ikan menjadi makanan untuk stunting karena merupakan sumber asam lemak omega-3 yang esensial untuk perkembangan otak dan sistem saraf. Asam lemak omega-3 juga memiliki sifat antiinflamasi yang dapat membantu mengurangi risiko peradangan dan penyakit kronis pada anak.</p></li>\n\n    <li><strong>Tempe dan Tahu</strong><p>Tempe dan tahu adalah sumber protein nabati yang rendah lemak dan kaya akan serat. Keduanya mengandung zat besi, kalsium, dan magnesium yang penting untuk pertumbuhan dan perkembangan tulang anak.</p></li>\n\n    <li><strong>Hati Ayam</strong><p>Hati ayam adalah salah satu sumber zat besi heme terbaik yang dapat membantu mencegah anemia pada anak-anak. Zat besi heme lebih mudah diserap oleh tubuh dibandingkan dengan zat besi non-heme yang terdapat dalam makanan nabati.</p></li>\n\n    <li><strong>Buah Beri</strong><p>Buah beri seperti blueberry, raspberry, dan strawberry mengandung antioksidan tinggi yang dapat membantu melawan radikal bebas dan mencegah kerusakan sel. Selain itu, buah beri juga mengandung vitamin C dan serat yang baik untuk sistem kekebalan tubuh dan pencernaan anak.</p></li>\n\n    <li><strong>Sayuran</strong><p>Sayuran hijau seperti bayam, brokoli, dan kangkung mengandung banyak zat besi, kalsium, dan magnesium yang penting untuk pertumbuhan dan perkembangan tulang anak. Selain itu, sayuran juga mengandung vitamin A, C, dan K yang penting untuk kesehatan mata, kulit, dan sistem kekebalan tubuh.</p></li>\n</ul>"
            },
            {
                "id": 16,
                "judul": "8 Menu Makanan untuk Stunting: Pencegahan Melalui Gizi Seimbang",
                "gambar": "https://unair.ac.id/wp-content/uploads/2022/11/Ilustrasi-by-Darya-Varia.jpg",
                "penulis": "Chubb Life Indonesia",
                "predicted_class": "several_stunted",
                'tanggal_dibuat': '2020-09-22',
                "isi": "<p>Stunting merupakan kondisi kekurangan gizi kronis yang terjadi karena defisiensi gizi dalam waktu lama. Kondisi ini bisa menyebabkan terjadinya gangguan tumbuh kembang anak, yaitu tinggi badan anak yang menjadi lebih pendek atau bisa dibilang kerdil dibandingkan dengan anak seusianya.</p>\n\n<h3>Bagaimana Mengetahui Stunting pada Anak?</h3>\n\n<p>Sayangnya, masih banyak orangtua yang belum mengetahui bagaimana mengenali ciri stunting pada balita. Ciri yang paling mudah dikenali adalah anak tidak memiliki tinggi badan yang sesuai dengan usianya.</p>\n\n<p>Namun, anak yang pendek tidak selalu dikategorikan stunting, meski anak yang mengalami stunting sudah pasti pendek. Ibu bisa mengamati hal ini dengan mengukur tinggi badan anak dan melihat pada kurva.</p>\n\n<p>Anak yang mengalami stunting memiliki tinggi badan yang berada kurang dari -2 standar deviasi. Dugaan ini semakin kuat jika anak masih berusia 2 tahun, sehingga penanganan harus segera dilakukan.</p>\n\n<h3>Cara Mencegah Stunting pada Anak</h3>\n\n<p>Perlu diketahui bahwa stunting pada balita bisa berlanjut hingga usia dewasa. Jadi, sebelum berdampak pada pertumbuhan dan perkembangan anak secara menyeluruh, kondisi stunting harus dicegah. Adapun upaya pencegahan yang bisa dilakukan yaitu:</p>\n\n<ol>\n    <li><strong>Pemberian pola asuh yang tepat</strong><p>Langkah pertama adalah memberikan pola asuh yang tepat untuk anak. Ini meliputi Inisiasi Menyusui Dini atau IMD dan memberikan ASI eksklusif untuk bayi hingga usianya genap 6 bulan, dan lanjutkan hingga usianya 2 tahun.</p></li>\n\n    <li><strong>Memberikan MPASI yang optimal</strong><p>United Nations Children’s Fund (UNICEF) bersama dengan World Health Organization (WHO) merekomendasikan, bayi yang berusia 6 sampai 23 bulan memperoleh asupan makanan pendamping ASI atau MPASI yang tepat dan optimal.</p>\n\n<p>Aturan pemberian makanan pendamping ASI mengandung setidaknya 4 atau lebih dari 7 macam makanan. Ini termasuk umbi atau serealia, produk olahan susu, kacang-kacangan, sumber protein, dan makanan dengan kandungan vitamin A.</p>\n\n<p>Selain itu, ibu juga perlu memperhatikan batas frekuensi pemberian makan minimal untuk bayi mulai dari 6-23 bulan yang mendapat atau tidak mendapat ASI. Aturannya yaitu 2 kali sehari atau lebih untuk usia 6-8 bulan bayi dengan ASI, dan 3 kali sehari atau lebih untuk bayi usia 9-23 bulan dengan ASI.</p>\n\n<p>Sementara itu, bayi usia 6-23 bulan yang tidak mendapatkan ASI setidaknya harus makan minimal 4 kali dalam sehari dengan porsi yang sesuai.</p></li>\n\n    <li><strong>Mengobati penyakit yang dialami anak</strong><p>Berbagai kondisi medis yang dialami anak bisa membuatnya mengalami penurunan nafsu makan. Misalnya, anak mengalami demam, batuk, pilek, flu, sembelit, hingga masalah pencernaan dan kondisi lain seperti TBC. Jika demikian, sebaiknya berikan penanganan utama pada kondisi medis tersebut. Lalu, ibu bisa melanjutkan dengan kembali memperbaiki asupan gizi sang buah hati.</p></li>\n\n    <li><strong>Perbaikan kebersihan lingkungan dan penerapan hidup bersih keluarga</strong><p>Pencegahan terakhir berupa menerapkan pola hidup bersih dan sehat, baik di lingkungan rumah maupun luar rumah. Membersihkan rumah bisa membantu menunjang kesehatan tubuh anak dan keluarga secara menyeluruh.</p></li>\n</ol>\n\n<p>Itu tadi beberapa upaya mencegah stunting pada balita yang dapat ibu dan ayah lakukan di rumah. Jangan lupa untuk rutin melakukan pengukuran berat badan dan tinggi badan anak.</p>\n\n<p>Ibu juga bisa langsung bertanya pada dokter spesialis anak terkait masalah gizi dan upaya pencegahan stunting lainnya.</p>"
            },
            {
                "id": 17,
                "judul": "Protein Hewani Penting Untuk Cegah Stunting",
                "gambar": "https://live-69566-healthscience-corporate-id.pantheonsite.io/sites/default/files/1_1.jpg",
                "penulis": "rumahsakit",
                "predicted_class": "several_stunted",
                'tanggal_dibuat': '2021-03-04',
                "isi": "<p>Stunting menjadi salah satu problem kesehatan yang masih menggejala di Indonesia. Masalah stunting bahkan menjadi perhatian khusus Kementerian Kesehatan lewat sejumlah kampanyenya.</p>\n\n<p>Hal ini karena stunting bisa mengakibatkan anak gagal tumbuh karena kekurangan nutrisi kronis, terutama pada 1.000 hari pertama kehidupan. Lalu apa sebenarnya stunting itu? Bagaimana cara mencegahnya? Simak penjelasan lengkapnya di artikel berikut.</p>\n\n<h3>Apa Itu Stunting?</h3>\n\n<p>Merujuk Organisasi Kesehatan Dunia atau World Health Organization (WHO), stunting adalah gangguan tumbuh kembang pada anak lantaran gizi buruk, infeksi berulang, serta stimulasi psikososial yang tidak memadai.</p>\n\n<p>Seorang anak dikategorikan stunting apabila tinggi badan menurut usianya lebih dari dua standar deviasi, di bawah ketetapan Standar Pertumbuhan Anak WHO. Stunting wajib diwaspadai karena dapat mempengaruhi pertumbuhan dan perkembangan otak buah hati Anda.</p>\n\n<p>Anak pengidap stunting cenderung memiliki IQ rendah serta sistem imun lemah. Secara jangka panjang, kondisi ini memberikan risiko lebih tinggi untuk anak menderita penyakit degeneratif, seperti diabetes dan kanker.</p>\n\n<p>Sebagai orang tua, Anda dapat membedakan tanda anak stunting dari tinggi badan di bawah rata-rata teman sebayanya. Kekurangan gizi kronis juga membuat berat badan mereka sulit naik, bahkan terus menurun. Anak stunting cenderung mudah lelah dan tidak aktif jika dibandingkan dengan anak-anak seusianya.</p>\n\n<h3>Cara Mencegah Masalah Stunting pada Anak</h3>\n\n<p>Ada tiga elemen yang perlu diperhatikan dalam mencegah masalah stunting yakni perbaikan pola makan, pola asuh serta pembenahan sanitasi dan air bersih. Berikut penjelasan lengkapnya:</p>\n\n<ul>\n    <li><strong>Pola Makan</strong><p>Jumlah dan kualitas gizi makanan yang kurang menjadi salah satu penyebab stunting pada anak. Anda perlu membiasakan gizi seimbang dalam makanan anak sehari-hari.</p>\n\n<p>Ada beberapa cara untuk mencapai gizi seimbang yakni perbanyak sumber protein serta konsumsi sayuran dan buah. Dalam satu piring, setengahnya dapat diisi sumber protein baik hewani maupun nabati. Buat proporsinya lebih banyak dibanding karbohidrat. Sisanya Anda dapat mengisinya dengan sayur dan buah.</p></li>\n\n    <li><strong>Pola Asuh</strong><p>Perilaku orangtua juga andil dalam mencegah stunting. Pola asuh yang baik, termasuk dalam pemberian makanan, menjadi penting.</p>\n\n<p>Edukasi tentang kesehatan reproduksi dan gizi bagi remaja dalam hal ini dibutuhkan karena mereka adalah calon ibu dan calon keluarga. Dengan pemahaman yang baik, masalah stunting dapat dicegah sejak ini.</p>\n\n<p>Jangan lupakan juga imunisasi agar anak mendapatkan kekebalan dari penyakit berbahaya. Anda dapat mengaksesnya secara gratis di posyandu atau puskesmas terdekat.</p></li>\n\n    <li><strong>Sanitasi dan Akses Air Bersih</strong><p>Risiko infeksi pada anak dapat meningkat apabila akses air bersih dan sanitasi di lingkungan rumah buruk. Riset Harvard Chan School menyebut diare adalah faktor ketiga yang memicu gangguan kesehatan tersebut.</p>\n\n<p>Adapun salah satu pemicu diare berasal dari kotoran yang masuk ke dalam tubuh manusia. Oleh karena itu, Anda perlu membiasakan cuci tangan serta tidak buang air besar sembarangan pada keluarga. Di sini, peran orangtua, terutama ibu sangat penting dalam mengelola kesehatan di keluarga.</p></li>\n</ul>\n\n<h3>Nutrisi yang Wajib Dipenuhi untuk Mencegah Stunting</h3>\n\n<p>Risiko stunting dapat dikurangi dengan asupan nutrisi yang cukup. Dilansir dari halaman resmi UNICEF, anak membutuhkan sekitar 40 jenis nutrisi berbeda untuk pertumbuhan optimal.</p>\n\n<p>Pencegahan stunting terbaik sebaiknya dilakukan pada masa awal kehamilan. Orang tua disarankan untuk mulai menerapkan pola makan seimbang dan gaya hidup sehat sedini mungkin.</p>\n\n<p>Dari awal masa kehamilan, pencegahan stunting dapat dilakukan dengan meningkatkan asupan zat besi dan asam folat untuk ibu.</p>\n\n<p>Zat besi penting sebagai pencegah anemia yang menimbulkan risiko bayi lahir dengan berat badan rendah. Ibu bisa mendapatkan asupan zat besi dari kacang-kacangan, sayuran, dan biji-bijian.</p>\n\n<p>Sementara itu, asam folat dibutuhkan untuk perkembangan otak dan sumsum tulang belakang bayi, serta meminimalisir timbulnya penyakit bawaan lahir. Zat ini juga dapat menekan risiko gangguan kehamilan hingga 72%. Kegagalan perkembangan organ bayi selama masa kehamilan juga bisa dicegah dengan asam folat. Asupan asam folat bisa ditemukan pada daging unggas, kuning telur, sayuran hijau, dan masih banyak lagi.</p>\n\n<p>Beberapa nutrisi yang sebaiknya selalu Anda berikan untuk si kecil setiap hari adalah vitamin A, Zinc, kombinasi mikronutrien dan omega 3, serta protein whey.</p>\n\n<p>Vitamin A berperan penting dalam pertumbuhan anak. Kekurangan vitamin ini dapat menyebabkan gangguan pada pertumbuhan. Manfaat lain dari vitamin A adalah perannya dalam mendukung daya tahan tubuh dalam mencegah berbagai infeksi penyakit.</p>\n\n<p>Menambah asupan vitamin A pada anak antara usia enam bulan hingga lima tahun dapat mengurangi risiko kematian, diare, dan secara bertahap mengurangi kemungkinan anak mengalami stunting. Vitamin A bisa bersumber dari ikan, daging, dan sumber nabati seperti sayuran berdaun hijau, wortel, ubi, serta mangga.</p>\n\n<p>Kinerja vitamin A dalam tubuh didukung pula oleh zinc. Mineral ini berperan penting untuk sintesis RNA dan DNA yang mendukung aktivitas sel dalam tubuh. WHO menganalisis fungsi zinc dalam pertumbuhan anak sebagai penunjang pertumbuhan tinggi badan anak.</p>\n\n<p>Anak yang mendapatkan asupan zinc sebanyak 10 mg per hari selama 24 minggu membantu mendorong pertumbuhan tinggi anak hingga 0.37 (±0.25) cm dibandingkan dengan yang tidak. Orang tua bisa memberikan asupan zinc lewat olahan telur, daging, ayam, dan kacang merah.</p>\n\n<p>Selain itu, risiko stunting juga dapat diminimalisir dengan memberikan kombinasi mikronutrien dan omega 3 pada buah hati Anda. Mikronutrien yang dimaksud adalah Docosahexaenoic acid atau biasa dikenal dengan DHA dan Arachidonic acid (AA) yang esensial bagi tumbuh kembang anak.</p>\n\n<p>Selain memenuhi nutrisi anak dengan makanan bergizi seimbang, berikan juga si Kecil minuman sehat berupa susu penambah berat badan. Susu jenis ini mengandung protein dan berbagai jenis nutrisi untuk mendukung anak mencapai tinggi badan dan berat badan ideal, serta meningkatkan kecerdasan anak.</p>\n\n<p>Susu penggemuk badan untuk anak seperti Nutren Junior direkomendasikan karena mengandung 50% Protein Whey, omega 3, 6, & DHA, probiotik, lemak nabati, nutrisi lengkap, dan juga bebas laktosa.</p>\n\n<p>Dalam susu pertumbuhan seperti Nutren Junior, anak akan terpapar pula asupan protein whey. Jenis protein ini dikenal unggul dalam membantu perkembangan fisik dengan meningkatkan massa otot si kecil.</p>\n\n<p>Susu yang bikin berat badan naik ini otomatis akan dapat membantu mengejar kurva pertumbuhan anak (tinggi dan berat badan).</p>\n\n<p>Protein whey mengandung asam amino esensial yang dapat membentuk hormon antibodi pada tubuh untuk menunjang kekuatan imun anak agar tidak mudah terserang penyakit. Asam amino turut meningkatkan pertumbuhan sel darah dan melindungi sel saraf. Karena sifat protein whey yang mudah diserap, manfaat ini dapat cepat diproses dalam tubuh.</p>\n\n<p>Nutren Junior adalah susu penambah berat badan yang diformulasikan untuk melengkapi kebutuhan nutrisi anak. Dengan berbagai keunggulan tersebut, orang tua bisa menjadikan Nutren Junior sebagai salah satu sumber asupan nutrisi pendukung pertumbuhan anak.</p>\n\n<p>Karena, pada akhirnya, orang tua merupakan ujung tombak terkait konsistensi memberikan nutrisi lengkap dan perawatan terbaik bagi anak. Dengan asupan nutrisi yang konsisten, maka anak bisa terhindar dari masalah stunting atau gangguan tumbuh kembang lainnya. Dukung tumbuh kembang anak dengan nutrisi lengkap dan terbaik.</p>"
            },
            {
                "id": 18,
                "judul": "Panduan Memenuhi Kebutuhan Gizi Balita Usia 1-5 Tahun",
                "gambar": "https://res.cloudinary.com/dk0z4ums3/image/upload/v1657531269/attached_image/stunting-0-alodokter.jpg",
                "penulis": "dr. Airindya Bella",
                "predicted_class": "several_stunted",
                'tanggal_dibuat': '2024-04-11',
                "isi": "<p>Stunting adalah gangguan pertumbuhan dan perkembangan anak akibat kekurangan gizi dalam jangka panjang. Stunting bisa disebabkan oleh malnutrisi yang dialami ibu saat hamil, atau anak pada masa pertumbuhannya.</p>\n\n<p>Stunting ditandai dengan tinggi anak yang lebih pendek daripada standar usianya. Jumlah kasus stunting di Indonesia masih tergolong tinggi, yaitu sekitar 3 dari 10 anak. Oleh karena itu, stunting masih menjadi masalah yang harus segera ditangani dan dicegah.</p>\n\n<p>Meski begitu, perlu diketahui bahwa anak yang tinggi badannya di bawah rata-rata belum tentu mengalami kekurangan gizi. Hal ini karena tinggi badan dapat dipengaruhi oleh faktor genetik. Jadi bila kedua orang tua berpostur tubuh pendek, anak juga bisa memiliki kondisi yang sama.</p>\n\n<p>Selain itu, perkembangan anak yang stunting biasanya terlambat secara signifikan. Sementara di sisi lain, anak yang sehat umumnya tidak mengalami keterlambatan perkembangan meski perawakannya pendek.</p>\n\n<h3>Penyebab Stunting</h3>\n\n<p>Penyebab utama stunting adalah malnutrisi dalam jangka panjang (kronis). Beberapa kondisi yang bisa menyebabkan anak kekurangan nutrisi adalah:</p>\n\n<ul>\n    <li>Ibu mengalami malnutrisi atau terserang infeksi selama hamil</li>\n    <li>Anak tidak mendapatkan ASI eksklusif</li>\n    <li>Kualitas gizi MPASI yang kurang</li>\n    <li>Anak menderita penyakit yang menghalangi penyerapan nutrisi, seperti alergi susu sapi atau sindrom malabsorbsi</li>\n    <li>Anak menderita infeksi kronis, seperti tuberkulosis atau cacingan</li>\n    <li>Anak memiliki penyakit bawaan, seperti penyakit jantung bawaan atau thalasemia</li>\n</ul>\n\n<h3>Faktor Risiko Stunting</h3>\n\n<p>Ada faktor-faktor yang bisa meningkatkan risiko anak mengalami stunting, antara lain:</p>\n\n<ul>\n    <li>Terlahir prematur</li>\n    <li>Terlahir dengan berat badan rendah</li>\n    <li>Mengalami intrauterine growth restriction (IUGR)</li>\n    <li>Tidak mendapatkan vaksin yang lengkap</li>\n    <li>Hidup di tengah kemiskinan</li>\n    <li>Tinggal di lingkungan dengan sanitasi buruk dan tidak mendapatkan akses untuk air bersih</li>\n</ul>\n\n<h3>Gejala Stunting</h3>\n\n<p>Gejala atau ciri-ciri stunting umumnya bisa terlihat saat anak berusia 2 tahun. Namun, hal ini sering tidak disadari, atau malah disalahartikan sebagai perawakan pendek yang normal.</p>\n\n<p>Gejala dan tanda-tanda yang bisa menunjukkan anak mengalami stunting adalah:</p>\n\n<ul>\n    <li>Tinggi badan anak lebih pendek daripada tinggi badan anak seusianya</li>\n    <li>Berat badan tidak meningkat secara konsisten</li>\n    <li>Tahap perkembangan yang terlambat dibandingkan anak seusianya</li>\n    <li>Tidak aktif bermain</li>\n    <li>Sering lemas</li>\n    <li>Mudah terserang penyakit, terutama infeksi</li>\n</ul>\n\n<h3>Kapan Harus ke Dokter</h3>\n\n<p>Pastikan untuk rutin mengukur berat badan, tinggi badan, dan indeks massa tubuh anak ke posyandu atau fasilitas kesehatan terdekat. Jika hasil skrining menunjukkan pertumbuhan anak tertinggal dibandingkan anak seusianya, lakukan pemeriksaan lanjutan ke dokter.</p>\n\n<p>Segera periksakan anak ke dokter jika ia mengalami gejala penyakit yang dapat meningkatkan risiko terjadinya stunting, seperti:</p>\n\n<ul>\n    <li>Batuk lebih dari 2 minggu</li>\n    <li>Demam atau diare berulang</li>\n    <li>Sulit menyusu</li>\n    <li>Sesak napas</li>\n</ul>\n\n<h3>Diagnosis Stunting</h3>\n\n<p>Dokter akan mengawali diagnosis stunting dengan tanya jawab bersama orang tua. Pertanyaan yang diajukan meliputi:</p>\n\n<ul>\n    <li>Pemberian ASI dan asupan makan anak</li>\n    <li>Kondisi kehamilan dan persalinan</li>\n    <li>Lingkungan tempat tinggal</li>\n    <li>Vaksinasi yang pernah dilakukan</li>\n</ul>\n\n<p>Setelah itu, dokter akan melakukan pemeriksaan fisik lengkap untuk melihat tanda-tanda stunting pada anak. Dokter juga akan mengukur:</p>\n\n<ul>\n    <li>Panjang atau tinggi badan</li>\n    <li>Berat badan</li>\n    <li>Lingkar kepala</li>\n    <li>Lingkar lengan anak</li>\n</ul>\n\n<p>Anak dapat diduga mengalami stunting apabila perbandingan tinggi badan dengan umurnya berada di bawah garis merah (-2 SD) berdasarkan buku KIA (kesehatan ibu dan anak).</p>\n\n<p>Jika anak berisiko tinggi mengalami stunting, dokter juga akan melakukan beberapa tes penunjang untuk memastikan penyebabnya. Pemeriksaan tersebut antara lain:</p>\n\n<ul>\n    <li>Tes darah, untuk mendeteksi gangguan kesehatan, seperti tuberkulosis, infeksi kronis, atau anemia</li>\n    <li>Tes urine, untuk mendeteksi sel darah putih di dalam urine yang bisa menjadi tanda infeksi</li>\n    <li>Pemeriksaan feses, untuk memeriksa infeksi parasit atau intoleransi laktosa</li>\n    <li>Ekokardiografi atau USG jantung, untuk mendeteksi penyakit jantung bawaan</li>\n    <li>Foto Rontgen dada, untuk melihat kondisi jantung dan paru-paru</li>\n    <li>Tes Mantoux, untuk mendiagnosis penyakit TBC</li>\n</ul>\n\n<h3>Pengobatan Stunting</h3>\n\n<p>Pengobatan stunting adalah dengan mengatasi penyakit penyebabnya, memperbaiki asupan nutrisi, memberikan suplemen, serta menerapkan pola hidup bersih dan sehat. Berikut adalah tindakan yang dapat dilakukan oleh dokter:</p>\n\n<ul>\n    <li>Mengobati penyakit yang mendasarinya, misalnya memberikan obat-obatan antituberkulosis bila anak menderita TBC</li>\n    <li>Memberikan suplemen vitamin A, zinc, zat besi, kalsium, dan yodium</li>\n    <li>Memberikan penyuluhan kepada orang tua agar memenuhi kebutuhan nutrisi anak</li>\n</ul>\n\n<p>Keberhasilan pengobatan stunting pada anak juga sangat bergantung pada upaya orang tua dan keluarga. Upaya yang dapat dilakukan adalah:</p>\n\n<ul>\n    <li>Memberikan nutrisi yang tepat dan lengkap lewat MPASI atau makanan pokok, berupa makanan yang kaya protein hewani, lemak, dan kalori</li>\n    <li>Membawa anak untuk kontrol rutin ke dokter jika ia menderita penyakit kronis</li>\n    <li>Memeriksakan tinggi dan berat badan anak secara berkala</li>\n    <li>Memperbaiki sanitasi di rumah dan menerapkan perilaku hidup bersih dan sehat (PHBS) guna mencapai keluarga yang sehat</li>\n</ul>\n\n<h3>Komplikasi Stunting</h3>\n\n<p>Jika tidak ditangani dengan tepat, stunting bisa menimbulkan dampak jangka panjang pada kesehatan anak. Komplikasi yang dapat terjadi meliputi:</p>\n\n<ul>\n    <li>Gangguan perkembangan otak yang mengganggu proses belajar dan menurunkan prestasi anak ke depannya</li>\n    <li>Penyakit metabolik ketika dewasa, seperti obesitas dan diabetes</li>\n    <li>Sering sakit dan mudah terkena infeksi</li>\n</ul>\n\n<h3>Pencegahan Stunting</h3>\n\n<p>Pencegahan stunting adalah dengan menghindari faktor yang dapat meningkatkan risiko terjadinya kondisi ini. Upaya yang bisa dilakukan antara lain:</p>\n\n<ul>\n    <li>Memenuhi asupan gizi yang cukup sebelum merencanakan kehamilan dan selama kehamilan</li>\n    <li>Mencukupi asupan gizi, terutama selama 1000 hari pertama kehidupan, yaitu sejak pembuahan sel telur hingga anak berusia 2 tahun</li>\n    <li>Memberikan ASI eksklusif hingga bayi berusia 6 bulan</li>\n    <li>Membaca buku KIA agar mengetahui panduan menyiapkan asupan makanan yang tepat untuk anak</li>\n    <li>Melakukan pemeriksaan rutin ke posyandu untuk memantau tahapan tumbuh kembang anak</li>\n    <li>Memastikan anak mendapatkan imunisasi lengkap</li>\n</ul>"
            },
            {
                "id": 19,
                "judul": "Tips Menjaga Asupan Gizi Anak",
                "gambar": "https://res.cloudinary.com/dk0z4ums3/image/upload/v1684805402/attached_image/rutf-makanan-khusus-untuk-balita-gizi-buruk-0-alodokter.jpg",
                "penulis": "lactoclub",
                "predicted_class": "several_stunted",
                'tanggal_dibuat': '2023-10-06',
                "isi": "<p>RUTF (ready to use therapeutic food) adalah makanan yang kaya energi dan tinggi nutrisi, seperti lemak, vitamin, dan mineral. Makanan ini dibuat khusus untuk mengatasi kekurangan nutrisi yang parah pada anak di bawah usia 5 tahun.</p>\n\n<p>RUTF, atau disebut juga makanan terapi siap saji, berbentuk seperti pasta sehingga teksturnya lembut dan bisa langsung dikonsumsi dengan mudah oleh anak usia 6 bulan ke atas. Makanan ini tersedia dalam bentuk kemasan berukuran sekitar 100 gram.</p>\n\n<p>Pemberian RUTF telah membantu jutaan anak di dunia yang mengalami wasting parah, yaitu salah satu bentuk malnutrisi atau gizi buruk. Anak dengan kondisi ini memiliki berat badan sangat rendah bila dibandingkan dengan tinggi badannya, sehingga tampak sangat kurus.</p>\n\n<p>Wasting terjadi akibat asupan nutrisi yang tidak tercukupi dan kurang berkualitas. Kondisi ini membuat anak rentan mengalami infeksi, bahkan bisa mengancam nyawa. Meski begitu, gizi buruk yang berat pada anak dapat ditangani dengan perawatan khusus, misalnya pemberian RUTF.</p>\n\n<h3>Berbagai Keunggulan RUTF</h3>\n\n<p>RUTF memiliki komposisi nutrisi yang mirip dengan susu F-100, yaitu susu yang diformulasikan khusus untuk mengatasi kekurangan nutrisi. Karena berbentuk susu, F-100 perlu diseduh terlebih dahulu dengan air sehingga dinilai kurang higienis, sedangkan RUTF bisa langsung dimakan.</p>\n\n<p>Berikut ini adalah beberapa keunggulan RUTF:</p>\n\n<ul>\n    <li>Nilai gizi tinggi sehingga memungkinkan balita dengan gizi buruk mengalami kenaikan berat badan dengan cepat</li>\n    <li>Praktis dan bisa dimakan langsung dari bungkusnya</li>\n    <li>Penyimpanan mudah tanpa lemari es meski kemasan sudah dibuka</li>\n    <li>Tahan lama dan dapat disimpan hingga 2 tahun</li>\n    <li>Rasa dan tekstur cocok untuk balita</li>\n</ul>\n\n<h3>Komposisi Nutrisi dan Bahan Makanan dalam RUTF</h3>\n\n<p>Sebagai makanan untuk mengatasi gizi buruk, RUTF berasal dari berbagai jenis makanan bergizi, yaitu:</p>\n\n<ul>\n    <li>Kacang tanah</li>\n    <li>Kacang hijau</li>\n    <li>Kacang merah</li>\n    <li>Kacang kedelai</li>\n    <li>Tempe</li>\n    <li>Suplemen vitamin dan mineral</li>\n    <li>Gula</li>\n    <li>Susu skim</li>\n    <li>Minyak sayur</li>\n</ul>\n\n<p>Bahan dasar RUTF di atas telah diteliti secara mendalam terkait formulasi dan efektivitasnya dalam memperbaiki nilai gizi pada anak yang mengalami wasting. Di dalam 1 bungkus RUTF mengandung kalori dan berbagai nutrisi sebagai berikut:</p>\n\n<ul>\n    <li>Protein</li>\n    <li>Lemak</li>\n    <li>Mineral, termasuk kalium, kalsium, fosfor, magnesium, zat besi, zinc, dan selenium</li>\n    <li>Vitamin</li>\n    <li>Asam folat</li>\n</ul>\n\n<p>Perlu ditekankan bahwa wasting pada anak adalah bentuk dari kekurangan gizi yang bisa mengancam nyawa. Anak dengan wasting terlihat sangat kurus dan rentan terkena penyakit. Oleh karena itu, penanganan wasting diperlukan sedini mungkin, salah satunya dengan pemberian RUTF.</p>\n\n<p>Makanan yang kaya nutrisi, seperti RUTF, dapat segera dikonsumsi oleh anak yang didiagnosis gizi buruk, apabila ia masih memiliki nafsu makan dan tingkat kesadarannya baik.</p>\n\n<p>Sementara itu, anak yang mengalami gizi buruk disertai nafsu makan yang kurang atau tanda-tanda komplikasi, seperti wajah dan perut bengkak, batuk berdarah, dan sangat lemas, memerlukan perawatan khusus di rumah sakit.</p>\n\n<p>Nantinya, dokter akan memberikan pengobatan khusus sesuai kondisi anak, seperti pemberian nutrisi melalui infus dan pemberian susu formula khusus.</p>"
            },
            {
                "id": 20,
                "judul": "Ketahui Masalah Stunting dan Cara Mengatasi Stunting",
                "gambar": "https://www.emro.who.int/images/stories/nutrition/balanced-diet.jpg",
                "penulis": "nestlehealthscience",
                "predicted_class": "several_stunted",
                'tanggal_dibuat': '2023-03-12',
                "isi": "<p>Stunting menurut definisi WHO adalah gangguan tumbuh kembang anak yang disebabkan kekurangan asupan gizi, terserang infeksi, maupun stimulasi yang tak memadai.</p>\n\n<p>Jumlah penderita stunting di Indonesia sendiri terus mengalami peningkatan. Setidaknya, setiap satu dari tiga anak berisiko mengalami gangguan tersebut. Lantas, adakah pencegahan yang bisa dilakukan? Berikut adalah langkah pencegahan stunting pada anak.</p>\n\n<h3>Memenuhi kebutuhan gizi sejak hamil</h3>\n\n<p>Tindakan yang relatif ampuh dilakukan untuk mencegah stunting pada anak adalah selalu memenuhi gizi sejak masa kehamilan. Lembaga kesehatan Millenium Challenge Account Indonesia menyarankan agar ibu yang sedang mengandung selalu mengonsumsi makanan sehat nan bergizi maupun suplemen atas anjuran dokter. Selain itu, perempuan yang sedang menjalani proses kehamilan juga sebaiknya rutin memeriksakan kesehatannya ke dokter atau bidan.</p>\n\n<h3>Beri ASI Eksklusif sampai bayi berusia 6 bulan</h3>\n\n<p>Veronika Scherbaum, ahli nutrisi dari Universitas Hohenheim, Jerman, menyatakan ASI ternyata berpotensi mengurangi peluang stunting pada anak berkat kandungan gizi mikro dan makro. Oleh karena itu, ibu disarankan untuk tetap memberikan ASI selama enam bulan kepada sang buah hati. Protein whey dan kolostrum yang terdapat pada susu ibu pun dinilai mampu meningkatkan sistem kekebalan tubuh bayi yang terbilang rentan.</p>\n\n<h3>Dampingi ASI dengan MPASI sehat</h3>\n\n<p>Ketika bayi menginjak usia 6 bulan ke atas, maka ibu sudah bisa memberikan makanan pendamping atau MPASI. Dalam hal ini pastikan makanan-makanan yang dipilih bisa memenuhi gizi mikro dan makro yang sebelumnya selalu berasal dari ASI untuk mencegah stunting. WHO pun merekomendasikan fortifikasi atau penambahan nutrisi ke dalam makanan. Di sisi lain, sebaiknya ibu berhati-hati saat akan menentukan produk tambahan tersebut. Konsultasikan dulu dengan dokter.</p>\n\n<h3>Terus memantau tumbuh kembang anak</h3>\n\n<p>Tidak sulit mengenali anak yang mengalami stunting. Dari segi fisik, mereka biasanya mempunyai postur tubuh lebih pendek dibandingkan anak-anak seusianya. Jadi, penting bagi ibu untuk terus memantau tumbuh kembang mereka, terutama dari tinggi dan berat badan anak. Bawa si Kecil secara berkala ke Posyandu maupun klinik khusus anak. Dengan begitu, akan lebih mudah bagi ibu untuk mengetahui gejala awal gangguan dan penanganannya.</p>\n\n<h3>Selalu jaga kebersihan lingkungan</h3>\n\n<p>Seperti yang diketahui, anak-anak sangat rentan akan serangan penyakit, terutama kalau lingkungan sekitar mereka kotor. Faktor ini pula yang secara tak langsung meningkatkan peluang stunting. Studi yang dilakukan di Harvard Chan School menyebutkan diare adalah faktor ketiga yang menyebabkan gangguan kesehatan tersebut. Sementara salah satu pemicu diare datang dari paparan kotoran yang masuk ke dalam tubuh manusia.</p>"
            }
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
