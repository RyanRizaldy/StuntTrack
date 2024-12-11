package com.bangkit.stuntack.ui.history

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.bangkit.stuntack.databinding.FragmentHistoryBinding
import com.bangkit.stuntack.ui.ViewModelFactory

class HistoryFragment : Fragment() {

    private var _binding: FragmentHistoryBinding? = null
    private val binding get() = _binding!!

    private lateinit var historyAdapter: HistoryAdapter
    private lateinit var historyViewModel: HistoryViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHistoryBinding.inflate(inflater, container, false)

        historyViewModel = ViewModelProvider(
            this,
            ViewModelFactory.getInstance(requireActivity().application)
        )[HistoryViewModel::class.java]


        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        historyAdapter = HistoryAdapter()


        binding.rvHistory.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = historyAdapter
        }
        showLoadingAnimation()
        observeHistoryData()
    }

    private fun showLoadingAnimation() {
        // Tampilkan animasi selama 3 detik
        binding.loadingAnimation.visibility = View.VISIBLE
        binding.historyTitle.visibility = View.GONE
        binding.rvHistory.visibility = View.GONE
        binding.navView.visibility = View.GONE

        Handler(Looper.getMainLooper()).postDelayed({
            // Sembunyikan animasi dan tampilkan konten utama
            binding.loadingAnimation.visibility = View.GONE
            binding.historyTitle.visibility = View.VISIBLE
            binding.rvHistory.visibility = View.VISIBLE
            binding.navView.visibility = View.VISIBLE
        }, 3000) // Durasi animasi 3 detik
    }

    private fun observeHistoryData() {
        historyViewModel.getAllHistory().observe(viewLifecycleOwner) { historyList ->
            historyAdapter.submitList(historyList)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}