package com.bangkit.stuntack.data.remote.response

import com.google.gson.annotations.SerializedName

data class NewsResponse(

	@field:SerializedName("NewsResponse")
	val newsResponse: List<NewsResponseItem?>? = null
)

data class NewsResponseItem(

	@field:SerializedName("penulis")
	val penulis: String? = null,

	@field:SerializedName("predicted_class")
	val predictedClass: String? = null,

	@field:SerializedName("id")
	val id: Int? = null,

	@field:SerializedName("judul")
	val judul: String? = null,

	@field:SerializedName("gambar")
	val gambar: String? = null
)
