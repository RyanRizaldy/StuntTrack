package com.bangkit.stuntack.data.database.helper

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object DateHelper {
    fun getCurrentDate(): String {
        val dateFormat = SimpleDateFormat("HH:mm dd/MM/yyyy ", Locale.getDefault())
        val date = Date()
        return dateFormat.format(date)
    }
}