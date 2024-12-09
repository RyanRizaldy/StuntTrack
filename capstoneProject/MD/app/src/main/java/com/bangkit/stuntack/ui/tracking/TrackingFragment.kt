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
import androidx.lifecycle.lifecycleScope
import com.bangkit.stuntack.MainActivity
import com.bangkit.stuntack.data.database.helper.DateHelper
import com.bangkit.stuntack.data.database.repository.HistoryRepository
import com.bangkit.stuntack.data.database.room.History
import com.bangkit.stuntack.data.remote.response.ModelResponse
import com.bangkit.stuntack.data.remote.response.PredictionRequest
import com.bangkit.stuntack.data.remote.retrofit.Config
import com.bangkit.stuntack.databinding.FragmentTrackingBinding
import com.bangkit.stuntack.ui.ViewModelFactory
import com.bangkit.stuntack.ui.history.HistoryViewModel
import com.bangkit.stuntack.ui.result.ResultActivity
import kotlinx.coroutines.launch

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

        binding.submitButton.setOnClickListener {
            val name = binding.nameInput.text.toString()
            val ageText = binding.ageEditText.editText?.text.toString()
            val heightText = binding.heightEditText.editText?.text.toString()
            val genderId = binding.radioGroupGender.checkedRadioButtonId

            if (name.isEmpty() || ageText.isEmpty() || heightText.isEmpty() || genderId == -1) {
                Toast.makeText(requireContext(), "Please fill all fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val umur = ageText.toInt()
            val tinggiBadan = heightText.toFloat()
            val jenisKelamin = when (binding.root.findViewById<RadioButton>(genderId).text.toString().lowercase()) {
                "male", "laki-laki" -> 1
                "female", "perempuan" -> 2
                else -> 0 // Default value jika gender tidak sesuai
            }

            lifecycleScope.launch {
                val prediction = sendPredictionRequest(umur, tinggiBadan, jenisKelamin)
                if (prediction != null) {
                    saveToHistory(name, prediction.predictedClass ?: "Unknown")
                    navigateToResultActivity(prediction)
                } else {
                    Toast.makeText(requireContext(), "Failed to get prediction", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private suspend fun sendPredictionRequest(umur: Int, tinggiBadan: Float, jenisKelamin: Int): ModelResponse? {
        return try {
            val request = PredictionRequest(umur, jenisKelamin, tinggiBadan)
            val response = Config.getApiService().predict(request)

            if (response.isSuccessful) {
                response.body() // Respons berhasil
            } else {
                val errorBody = response.errorBody()?.string()
                Log.e("API_ERROR", "Error Response: $errorBody")
                null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    private fun saveToHistory(name: String, predictedClass: String) {
        val currentDate = DateHelper.getCurrentDate()
        val history = History(name = name, status = predictedClass, date = currentDate)
        historyViewModel.addHistory(history)
    }

    private fun navigateToResultActivity(prediction: ModelResponse) {
        val intent = Intent(requireContext(), ResultActivity::class.java).apply {
            putExtra("PREDICTED_CLASS", prediction.predictedClass)
            putExtra("PREDICTION_PROBABILITY",
                prediction.predictionProbability?.let { ArrayList(it) })
        }
        startActivity(intent)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
