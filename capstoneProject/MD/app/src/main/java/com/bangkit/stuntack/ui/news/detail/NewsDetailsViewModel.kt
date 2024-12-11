package com.bangkit.stuntack.ui.news.detail

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bangkit.stuntack.data.remote.response.NewsDetailResponse
import com.bangkit.stuntack.data.remote.retrofit.ApiConfig
import kotlinx.coroutines.launch

class NewsDetailsViewModel : ViewModel() {

    private val _newsDetail = MutableLiveData<NewsDetailResponse>()
    val newsDetail: LiveData<NewsDetailResponse> = _newsDetail

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    companion object {
        private const val TAG = "NewsDetailsViewModel"
    }

    fun getNewsDetail(newsId: Int) {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val response = ApiConfig.getApiService().getNewsDetail(newsId)
                _newsDetail.value = response
                _isLoading.value = false
            } catch (e: Exception) {
                _isLoading.value = false
                _errorMessage.value = e.message
                Log.e(TAG, "Error fetching news detail: ${e.message}")
            }
        }
    }
}