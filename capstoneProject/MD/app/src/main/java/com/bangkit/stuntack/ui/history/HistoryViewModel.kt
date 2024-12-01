package com.bangkit.stuntack.ui.history


import android.app.Application
import androidx.lifecycle.LiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bangkit.stuntack.data.database.room.History
import com.bangkit.stuntack.data.database.repository.HistoryRepository
import kotlinx.coroutines.launch


class HistoryViewModel(application: Application) : ViewModel() {
    private val mHistoryRepository = HistoryRepository(application)

    fun getAllHistory(): LiveData<List<History>> = mHistoryRepository.getAllHistory()

    fun addHistory(history: History) {
        viewModelScope.launch {
            mHistoryRepository.insert(history)
        }
    }
}
