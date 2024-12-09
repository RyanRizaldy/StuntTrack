package com.bangkit.stuntack.data.remote.response

import com.google.gson.annotations.SerializedName

data class ModelResponse(

	@field:SerializedName("predicted_class")
	val predictedClass: String? = null,

	@field:SerializedName("prediction_probability")
	val predictionProbability: List<Any?>? = null
)
