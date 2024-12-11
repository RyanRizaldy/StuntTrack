package com.bangkit.stuntack.ui.news

import android.content.Context
import android.content.Intent
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bangkit.stuntack.R
import com.bangkit.stuntack.data.remote.response.NewsResponseItem
import com.bangkit.stuntack.databinding.CardNewsBinding
import com.bangkit.stuntack.ui.news.detail.NewsDetailsActivity
import com.bumptech.glide.Glide

class NewsAdapter(private val context: Context) : ListAdapter<NewsResponseItem, NewsAdapter.MyViewHolder>(
    DIFF_CALLBACK
) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val binding = CardNewsBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return MyViewHolder(binding)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        val newsItem = getItem(position)
        holder.bind(newsItem, context)
    }

    class MyViewHolder(private val binding: CardNewsBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(newsItem: NewsResponseItem, context: Context) {
            binding.newsTitle.text = newsItem.judul
            Glide.with(binding.root.context)
                .load(newsItem.gambar)
                .error(R.drawable.placeholder_image)
                .into(binding.newsImage)

            binding.root.setOnClickListener {
                val intent = Intent(context, NewsDetailsActivity::class.java)
                intent.putExtra("NEWS_ID", newsItem.id)
                context.startActivity(intent)
            }
        }
    }

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback<NewsResponseItem>() {
            override fun areItemsTheSame(
                oldItem: NewsResponseItem,
                newItem: NewsResponseItem
            ): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(
                oldItem: NewsResponseItem,
                newItem: NewsResponseItem
            ): Boolean {
                return oldItem == newItem
            }
        }
    }
}