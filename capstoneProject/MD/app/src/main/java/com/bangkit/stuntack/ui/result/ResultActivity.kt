package com.bangkit.stuntack.ui.result

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.bangkit.stuntack.R
import com.bangkit.stuntack.data.remote.retrofit.ApiConfig
import com.bangkit.stuntack.databinding.ActivityResultBinding
import com.bangkit.stuntack.ui.news.NewsAdapter
import kotlinx.coroutines.launch


class ResultActivity : AppCompatActivity() {
    private lateinit var binding: ActivityResultBinding
    private lateinit var newsAdapter: NewsAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportActionBar?.hide()
        binding = ActivityResultBinding.inflate(layoutInflater)
        setContentView(binding.root)

        showLottieAnimation()

        // Tetapkan handler untuk mengatur logika setelah animasi selesai
        Handler(Looper.getMainLooper()).postDelayed({
            hideLottieAnimation()
            initializeContent()
        }, 3000) // 3 detik
    }

    private fun showLottieAnimation() {
        binding.progressBar.visibility = View.VISIBLE
        binding.stuntBar.visibility = View.GONE
        binding.stuntResult.visibility = View.GONE
        binding.stuntDisclaimer.visibility = View.GONE
        binding.tipsTitle.visibility = View.GONE
        binding.tipsCard.visibility = View.GONE
        binding.articleTitle.visibility = View.GONE
        binding.rvArticles.visibility = View.GONE
        binding.btnBack.visibility = View.GONE
        binding.result.visibility = View.GONE
    }

    private fun hideLottieAnimation() {
        binding.progressBar.visibility = View.GONE
        binding.stuntBar.visibility = View.VISIBLE
        binding.stuntResult.visibility = View.VISIBLE
        binding.stuntDisclaimer.visibility = View.VISIBLE
        binding.tipsTitle.visibility = View.VISIBLE
        binding.tipsCard.visibility = View.VISIBLE
        binding.articleTitle.visibility = View.VISIBLE
        binding.rvArticles.visibility = View.VISIBLE
        binding.btnBack.visibility = View.VISIBLE
        binding.result.visibility = View.VISIBLE
    }

    private fun initializeContent() {
        // Ambil status prediksi dari intent
        val predictedClass = intent.getStringExtra("PREDICTED_CLASS") ?: ""

        // Tentukan nilai untuk slider (berdasarkan status prediksi)
        val tipsMessage = getTipsMessage(predictedClass)
        binding.tips.text = tipsMessage

        val predictionMessage = getCustomMessage(predictedClass)

        val sliderValue = when (predictedClass) {
            "severely_stunted" -> "sangat stunting"
            "stunted" -> "stunting"
            "normal" -> "normal"
            "tinggi" -> "baik"
            else -> "unknown"
        }

        setRangeSliderResult(sliderValue)
        binding.stuntResult.text = predictionMessage

        setupRecyclerView()
        fetchAndFilterNews(predictedClass)

        binding.btnBack.setOnClickListener {
            finish()
        }

        playAnimation()
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
            "severely_stunted" -> "severly_stunted"
            else -> predictedClass
        }
    }

    private fun fetchAndFilterNews(predictedClass: String) {
        binding.progressBar.visibility = View.VISIBLE // Tampilkan loading animation
        binding.rvArticles.visibility = View.GONE // Sembunyikan RecyclerView

        lifecycleScope.launch {
            try {
                val newsList = ApiConfig.getApiService().getNews()
                val mappedClass = mapPredictedClass(predictedClass)
                val filteredNews = newsList.filter { news ->
                    news.predictedClass.equals(mappedClass, ignoreCase = true)
                }
                newsAdapter.submitList(filteredNews)

                // Sembunyikan animasi dan tampilkan RecyclerView setelah data selesai dimuat
                binding.progressBar.visibility = View.GONE
                binding.rvArticles.visibility = View.VISIBLE

            } catch (e: Exception) {
                binding.progressBar.visibility = View.GONE
                Toast.makeText(this@ResultActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun setRangeSliderResult(result: String) {
        val minValue: Float
        val maxValue: Float
        val color: Int

        when (result) {
            "sangat stunting" -> {
                minValue = 0f
                maxValue = 1f
                color = Color.parseColor("#ba1a1a") // Merah
            }
            "stunting" -> {
                minValue = 1f
                maxValue = 2f
                color = Color.parseColor("#F17600") // Oranye
            }
            "normal" -> {
                minValue = 2f
                maxValue = 3f
                color = Color.parseColor("#FED000") // Kuning
            }
            "baik" -> {
                minValue = 3f
                maxValue = 4f
                color = Color.parseColor("#00A26A") // Hijau
            }
            else -> {
                minValue = 0f
                maxValue = 4f
                color = Color.GRAY
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

    private fun playAnimation() {
        val stuntBar = ObjectAnimator.ofFloat(binding.stuntBar, View.ALPHA, 1f).setDuration(100)
        val stunResult =
            ObjectAnimator.ofFloat(binding.stuntResult, View.ALPHA, 1f).setDuration(100)
        val stunDisclaimer =
            ObjectAnimator.ofFloat(binding.stuntDisclaimer, View.ALPHA, 1f).setDuration(100)
        val tipsTitle =
            ObjectAnimator.ofFloat(binding.tipsTitle, View.ALPHA, 1f).setDuration(100)
        val tipsCard =
            ObjectAnimator.ofFloat(binding.tipsCard, View.ALPHA, 1f).setDuration(100)
        val articleTitle =
            ObjectAnimator.ofFloat(binding.articleTitle, View.ALPHA, 1f).setDuration(100)
        val rvArticle =
            ObjectAnimator.ofFloat(binding.rvArticles, View.ALPHA, 1f).setDuration(100)

        AnimatorSet().apply {
            playSequentially(
                stuntBar,
                stunResult,
                stunDisclaimer,
                tipsTitle,
                tipsCard,
                articleTitle,
                rvArticle
            )
            startDelay = 100
        }.start()
    }

}
