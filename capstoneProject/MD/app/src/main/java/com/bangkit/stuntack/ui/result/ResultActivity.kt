package com.bangkit.stuntack.ui.result

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.bangkit.stuntack.databinding.ActivityResultBinding


class ResultActivity : AppCompatActivity() {
    private lateinit var binding: ActivityResultBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportActionBar?.hide()
        binding = ActivityResultBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Ambil status prediksi dari intent
        val predictedClass = intent.getStringExtra("PREDICTED_CLASS") ?: ""


        // Tentukan nilai untuk slider (berdasarkan status prediksi)
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

        // Button untuk kembali
        binding.btnBack.setOnClickListener {
            finish()
        }


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


}