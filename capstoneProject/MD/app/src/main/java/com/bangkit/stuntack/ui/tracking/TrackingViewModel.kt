package com.bangkit.stuntack.ui.tracking

import android.app.Application
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bangkit.stuntack.data.database.room.History
import com.bangkit.stuntack.data.database.repository.HistoryRepository
import kotlinx.coroutines.launch

class TrackingViewModel(application: Application) : ViewModel() {
    private val mHistoryRepository: HistoryRepository = HistoryRepository(application)

    fun insertHistory(history: History) {
        viewModelScope.launch {
            mHistoryRepository.insert(history)
        }
    }
}
