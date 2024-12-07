package com.bangkit.stuntack.ui.news

import android.content.Context
import android.content.Intent
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bangkit.stuntack.data.remote.response.ListEventsItem
import com.bangkit.stuntack.databinding.CardNewsBinding
import com.bangkit.stuntack.ui.news.detail.NewsDetailsActivity
import com.bumptech.glide.Glide

class NewsAdapter(private val context: Context) : ListAdapter<ListEventsItem, NewsAdapter.MyViewHolder>(
    DIFF_CALLBACK
) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val binding = CardNewsBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return MyViewHolder(binding)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        val event = getItem(position)
        holder.bind(event, context)
    }

    class MyViewHolder(private val binding: CardNewsBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(event: ListEventsItem, context: Context) {
            binding.eventTitle.text = event.name
            Glide.with(binding.root.context)
                .load(event.mediaCover)
                .into(binding.eventImage)

            binding.root.setOnClickListener {
                val intent = Intent(context, NewsDetailsActivity::class.java)
                intent.putExtra("EVENT_ID", event.id)
                context.startActivity(intent)
            }
        }
    }

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<ListEventsItem>() {
            override fun areItemsTheSame(
                oldItem: ListEventsItem,
                newItem: ListEventsItem
            ): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(
                oldItem: ListEventsItem,
                newItem: ListEventsItem
            ): Boolean {
                return oldItem == newItem
            }
        }
    }
}