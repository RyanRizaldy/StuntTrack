package com.bangkit.stuntack.ui.news

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bangkit.stuntack.data.remote.response.NewsResponseItem
import com.bangkit.stuntack.data.remote.retrofit.ApiConfig
import kotlinx.coroutines.launch

class NewsViewModel : ViewModel() {

    private val _news = MutableLiveData<List<NewsResponseItem>>()
    val news: LiveData<List<NewsResponseItem>> = _news

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    companion object {
        private const val TAG = "NewsViewModel"
    }

    fun getNews() {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val response = ApiConfig.getApiService().getNews()
                _news.value = response
                _isLoading.value = false
            } catch (e: Exception) {
                _isLoading.value = false
                _errorMessage.value = e.message
                Log.e(TAG, "Error fetching news: ${e.message}")
            }
        }
    }
}
