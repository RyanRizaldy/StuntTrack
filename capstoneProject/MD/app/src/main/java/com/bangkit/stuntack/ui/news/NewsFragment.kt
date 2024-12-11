package com.bangkit.stuntack.ui.news

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Observer
import androidx.recyclerview.widget.LinearLayoutManager
import com.bangkit.stuntack.databinding.FragmentNewsBinding

class NewsFragment : Fragment() {

    private var _binding: FragmentNewsBinding? = null
    private val binding get() = _binding!!
    private lateinit var newsAdapter: NewsAdapter
    private val viewModel: NewsViewModel by viewModels()
    private var isAnimationMinTimeElapsed = false

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentNewsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Setup RecyclerView
        binding.rvNews.layoutManager = LinearLayoutManager(requireContext())

        // Initialize the adapter
        newsAdapter = NewsAdapter(requireContext())
        binding.rvNews.adapter = newsAdapter

        // Observe news data
        viewModel.news.observe(viewLifecycleOwner) { news ->
            if (news != null) {
                newsAdapter.submitList(news)
            }
            if (isAnimationMinTimeElapsed) {
                showLoading(false)
            }
        }

        // Observe loading state
        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            if (isLoading) {
                showLoading(true)
                startMinimumAnimationTimer()
            } else if (isAnimationMinTimeElapsed) {
                showLoading(false)
            }
        }

        // Fetch news data from API
        viewModel.getNews()
    }

    private fun showLoading(isLoading: Boolean) {
        // Add null check for binding
        if (_binding == null) return

        if (isLoading) {
            binding.progressBar.apply {
                visibility = View.VISIBLE
                playAnimation()
            }
            binding.contentLayout.visibility = View.GONE
        } else {
            binding.progressBar.apply {
                cancelAnimation()
                visibility = View.GONE
            }
            binding.contentLayout.visibility = View.VISIBLE
        }
    }

    private fun startMinimumAnimationTimer() {
        isAnimationMinTimeElapsed = false
        Handler(Looper.getMainLooper()).postDelayed({
            isAnimationMinTimeElapsed = true
            if (viewModel.isLoading.value == false) {
                showLoading(false)
            }
        }, 3000) // Minimum animation duration: 3 seconds
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Set binding to null to prevent memory leaks
        _binding = null
    }
}


