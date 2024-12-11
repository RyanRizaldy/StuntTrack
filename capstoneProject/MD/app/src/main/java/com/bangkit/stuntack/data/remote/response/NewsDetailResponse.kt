package com.bangkit.stuntack.data.remote.response

import com.google.gson.annotations.SerializedName

data class NewsDetailResponse(

	@field:SerializedName("penulis")
	val penulis: String? = null,

	@field:SerializedName("predicted_class")
	val predictedClass: String? = null,

	@field:SerializedName("id")
	val id: Int? = null,

	@field:SerializedName("judul")
	val judul: String? = null,

	@field:SerializedName("gambar")
	val gambar: String? = null,

	@field:SerializedName("isi")
	val isi: String? = null
)
