package com.bangkit.stuntack.ui.news.detail

import android.os.Bundle
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.bangkit.stuntack.R
import com.bangkit.stuntack.data.remote.response.NewsDetailResponse
import com.bangkit.stuntack.databinding.ActivityNewsDetailsBinding
import com.bumptech.glide.Glide

class NewsDetailsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityNewsDetailsBinding
    private val viewModel: NewsDetailsViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityNewsDetailsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        supportActionBar?.hide()

        // Get news ID from intent
        val newsId = intent.getIntExtra("NEWS_ID", -1)
        if (newsId != -1) {
            viewModel.getNewsDetail(newsId)
        } else {
            showError("Invalid News ID")
            return
        }

        // Observe ViewModel
        viewModel.newsDetail.observe(this) { detail ->
            if (detail != null) {
                populateData(detail)
            }
        }

        viewModel.isLoading.observe(this) { isLoading ->
            showLoading(isLoading)
        }

        viewModel.errorMessage.observe(this) { errorMessage ->
            errorMessage?.let { showError(it) }
        }

        // Back button functionality
        binding.backDetails.setOnClickListener {
            finish()
        }
    }

    private fun populateData(detail: NewsDetailResponse) {
        binding.textTitle.text = detail.judul
        binding.textDate.text = detail.predictedClass
        binding.textPublisher.text = detail.penulis
        binding.textDescription.text = detail.isi

        Glide.with(this)
            .load(detail.gambar)
            .placeholder(R.drawable.placeholder_image)
            .into(binding.imageNews)
    }

    private fun showLoading(isLoading: Boolean) {
        binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
    }

    private fun showError(message: String) {
        binding.progressBar.visibility = View.GONE
        binding.textDescription.text = getString(R.string.error_message, message)
    }
}