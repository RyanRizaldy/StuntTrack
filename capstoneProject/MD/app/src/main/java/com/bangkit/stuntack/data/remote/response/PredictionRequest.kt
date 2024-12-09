package com.bangkit.stuntack.data.remote.response

import com.google.gson.annotations.SerializedName

data class PredictionRequest(
    @SerializedName("umur")
    val umur: Int,
    @SerializedName("jenis_kelamin")
    val jenisKelamin: Int,
    @SerializedName("tinggi_badan")
    val tinggiBadan: Float
)