package com.bangkit.stuntack.ui.result

import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.bangkit.stuntack.R
import com.bangkit.stuntack.data.remote.retrofit.ApiConfig
import com.bangkit.stuntack.databinding.ActivityResultBinding
import com.bangkit.stuntack.ui.news.NewsAdapter
import kotlinx.coroutines.launch
import retrofit2.Response
import java.util.Locale

class ResultActivity : AppCompatActivity() {
    private lateinit var binding: ActivityResultBinding
    private lateinit var newsAdapter: NewsAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportActionBar?.hide()
        binding = ActivityResultBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Ambil status prediksi dari intent
        val predictedClass = intent.getStringExtra("PREDICTED_CLASS") ?: ""

        // Tentukan teks tips berdasarkan prediksi
        val tipsMessage = getTipsMessage(predictedClass)
        binding.tips.text = tipsMessage

        // Peta status prediksi ke pesan khusus
        val predictionMessage = getCustomMessage(predictedClass)

        // Tentukan nilai untuk slider (misalnya, berdasarkan status prediksi)
        val sliderValue = when (predictedClass) {
            "severely_stunted" -> "sangat stunting"
            "stunted" -> "stunting"
            "normal" -> "normal"
            "tinggi" -> "baik"
            else -> "unknown"
        }

        // Atur RangeSlider dan tampilkan pesan hasil prediksi
        setRangeSliderResult(sliderValue)
        binding.stuntResult.text = getCustomMessage(predictedClass)

        // Inisialisasi RecyclerView
        setupRecyclerView()

        // Fetch dan filter berita berdasarkan hasil prediksi
        fetchAndFilterNews(predictedClass)

        // Button untuk kembali
        binding.btnBack.setOnClickListener {
            finish()
        }
    }

    private fun getTipsMessage(predictedClass: String): String {
        return when (predictedClass.lowercase()) {
            "severely_stunted" -> getString(R.string.sangat_stunting)
            "stunted" -> getString(R.string.stunting)
            "normal" -> getString(R.string.normal)
            "tinggi" -> getString(R.string.tinggi)
            else -> "No specific tips available for this prediction."
        }
    }

    private fun setupRecyclerView() {
        newsAdapter = NewsAdapter(this)
        binding.rvArticles.apply {
            layoutManager = LinearLayoutManager(this@ResultActivity)
            adapter = newsAdapter
        }
    }

    private fun mapPredictedClass(predictedClass: String): String {
        return when (predictedClass.lowercase()) {
            "severely_stunted" -> "several_stunted"
            else -> predictedClass
        }
    }

    private fun fetchAndFilterNews(predictedClass: String) {
        binding.progressBar.visibility = View.VISIBLE // Tampilkan loading
        binding.rvArticles.visibility = View.GONE

        lifecycleScope.launch {
            try {
                val newsList = ApiConfig.getApiService().getNews()
                val mappedClass = mapPredictedClass(predictedClass)
                val filteredNews = newsList.filter { news ->
                    news.predictedClass.equals(mappedClass, ignoreCase = true)
                }
                newsAdapter.submitList(filteredNews)

                binding.progressBar.visibility = View.GONE
                binding.rvArticles.visibility = View.VISIBLE

            } catch (e: Exception) {
                binding.progressBar.visibility = View.GONE
                Toast.makeText(this@ResultActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setRangeSliderResult(result: String) {
        // Mendeklarasikan minValue, maxValue, dan color untuk setiap status
        val minValue: Float
        val maxValue: Float
        val color: Int

        when (result) {
            "sangat stunting" -> {
                minValue = 0f
                maxValue = 1f
                color = Color.parseColor("#ba1a1a") // Merah untuk sangat stunting
            }
            "stunting" -> {
                minValue = 1f
                maxValue = 2f
                color = Color.parseColor("#F17600") // Oranye untuk stunting
            }
            "normal" -> {
                minValue = 2f
                maxValue = 3f
                color = Color.parseColor("#FED000") // Kuning untuk normal
            }
            "baik" -> {
                minValue = 3f
                maxValue = 4f
                color = Color.parseColor("#00A26A") // Hijau untuk baik
            }
            else -> {
                minValue = 0f
                maxValue = 4f
                color = Color.GRAY // Gray jika status tidak dikenal
            }
        }

        // Mengatur nilai pada RangeSlider dengan dua nilai
        binding.statusRangeSlider.setValues(minValue, maxValue)

        // Mengatur warna track aktif dan thumb secara programatis
        binding.statusRangeSlider.trackActiveTintList = ColorStateList.valueOf(color)
        binding.statusRangeSlider.trackInactiveTintList = ColorStateList.valueOf(Color.parseColor("#F3F3F3"))
        binding.statusRangeSlider.thumbTintList = ColorStateList.valueOf(color)
    }

    private fun getCustomMessage(predictedClass: String): String {
        return when (predictedClass) {
            "severely_stunted" -> "Your child is severely stunted and needs immediate medical attention."
            "stunted" -> "Your child is stunted and requires nutritional support and monitoring."
            "normal" -> "Your child's growth is normal, but continue to ensure proper nutrition."
            "tinggi" -> "Your child is in good nutritional health, continue maintaining a balanced diet."
            else -> "Unable to determine the prediction. Please consult a healthcare provider."
        }
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}