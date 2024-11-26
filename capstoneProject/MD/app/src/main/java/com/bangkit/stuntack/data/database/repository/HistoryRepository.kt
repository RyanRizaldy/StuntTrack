package com.bangkit.stuntack.data.database.repository

import android.app.Application
import androidx.lifecycle.LiveData
import com.bangkit.stuntack.data.database.room.History
import com.bangkit.stuntack.data.database.room.HistoryDao
import com.bangkit.stuntack.data.database.room.HistoryDatabase
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class HistoryRepository (application: Application) {
    private val mHistoryDao: HistoryDao
    private val executorService: ExecutorService = Executors.newSingleThreadExecutor()
    init {
        val db = HistoryDatabase.getDatabase(application)
        mHistoryDao = db.historyDao()
    }
    fun getAllHistory(): LiveData<List<History>> = mHistoryDao.getAllHistory()
    fun insert(history: History) {
        executorService.execute { mHistoryDao.insert(history) }
    }
    fun delete(history: History) {
        executorService.execute { mHistoryDao.delete(history) }
    }
    fun update(history: History) {
        executorService.execute { mHistoryDao.update(history) }
    }


}