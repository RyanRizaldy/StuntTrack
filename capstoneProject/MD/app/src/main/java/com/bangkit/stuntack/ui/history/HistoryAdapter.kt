package com.bangkit.stuntack.ui.history

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bangkit.stuntack.data.database.room.History
import com.bangkit.stuntack.databinding.CardHistoryBinding

class HistoryAdapter : ListAdapter<History, HistoryAdapter.HistoryViewHolder>(DIFF_CALLBACK) {

    companion object {
        private val DIFF_CALLBACK = object : DiffUtil.ItemCallback<History>() {
            override fun areItemsTheSame(oldItem: History, newItem: History): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(oldItem: History, newItem: History): Boolean {
                return oldItem == newItem
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): HistoryViewHolder {
        val binding = CardHistoryBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return HistoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: HistoryViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class HistoryViewHolder(private val binding: CardHistoryBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(history: History) {
            binding.apply {
                nameText.text = history.name
                dateText.text = history.date
                statusText.text = when (history.status) {
                    "severely_stunted" -> "Severely stunted and needs immediate medical attention."
                    "stunted" -> "Stunted and requires nutritional support and monitoring."
                    "normal" -> "Normal growth, but continue to ensure proper nutrition."
                    "tinggi" -> "Good nutritional health, continue maintaining a balanced diet."
                    else -> "Unable to determine the prediction. Please consult a healthcare provider."
                }
            }
        }
    }
}