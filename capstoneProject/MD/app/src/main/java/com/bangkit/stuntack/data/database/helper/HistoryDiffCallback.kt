package com.bangkit.stuntack.data.database.helper

import androidx.recyclerview.widget.DiffUtil
import com.bangkit.stuntack.data.database.room.History

class HistoryDiffCallback (private val oldHistoryList: List<History>, private val newHistoryList: List<History>) : DiffUtil.Callback() {
    override fun getOldListSize(): Int = oldHistoryList.size
    override fun getNewListSize(): Int = newHistoryList.size
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldHistoryList[oldItemPosition].id == newHistoryList[newItemPosition].id
    }
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        val oldHistory = oldHistoryList[oldItemPosition]
        val newHistory = newHistoryList[newItemPosition]
        return oldHistory.name == newHistory.name && oldHistory.status == newHistory.status
    }
}