package com.bangkit.stuntack.ui.tracking

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.RadioButton
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.ViewModelProvider
import com.bangkit.stuntack.MainActivity
import com.bangkit.stuntack.data.database.helper.DateHelper
import com.bangkit.stuntack.data.database.repository.HistoryRepository
import com.bangkit.stuntack.data.database.room.History
import com.bangkit.stuntack.databinding.FragmentTrackingBinding
import com.bangkit.stuntack.ui.ViewModelFactory
import com.bangkit.stuntack.ui.history.HistoryViewModel

class TrackingFragment : Fragment() {

    private var _binding: FragmentTrackingBinding? = null
    private val binding get() = _binding!!
    private lateinit var trackingViewModel: TrackingViewModel
    private lateinit var historyRepository: HistoryRepository
    val historyViewModel: HistoryViewModel by viewModels {
        ViewModelFactory.getInstance(requireActivity().application)
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentTrackingBinding.inflate(inflater, container, false)

        trackingViewModel = ViewModelProvider(
            this,
            ViewModelFactory.getInstance(requireActivity().application)
        ).get(TrackingViewModel::class.java)

        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        historyRepository = HistoryRepository(requireActivity().application)

        binding.submitButton.setOnClickListener {
            val name = binding.nameInput.text.toString()
            val age = binding.ageEditText.editText?.text.toString()
            val height = binding.heightEditText.editText?.text.toString()
            val genderId = binding.radioGroupGender.checkedRadioButtonId
            if (genderId != -1) {
                val selectedGender = binding.root.findViewById<RadioButton>(genderId).text.toString()
                // Gunakan `selectedGender` untuk mendapatkan teks dari RadioButton yang dipilih
                Log.d("SelectedGender", selectedGender)
            } else {
                Log.d("SelectedGender", "No gender selected")
            }

            if (name.isEmpty() || age.isEmpty() || height.isEmpty()) {
                Toast.makeText(requireContext(), "Please fill all fields", Toast.LENGTH_SHORT).show()
            } else {
                saveToHistory(name)
                navigateToResultActivity()
            }
        }
    }

    private fun saveToHistory(name: String) {
        val currentDate = DateHelper.getCurrentDate()
        val defaultStatus = "Normal" // Prediksi default
        val history = History(name = name, status = defaultStatus, date = currentDate)
        historyViewModel.addHistory(history)
    }

    private fun navigateToResultActivity() {
        val intent = Intent(requireContext(), MainActivity::class.java)
        startActivity(intent)
        requireActivity().finish()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}