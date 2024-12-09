package com.bangkit.stuntack.data.remote.retrofit

import com.bangkit.stuntack.data.remote.response.ModelResponse
import com.bangkit.stuntack.data.remote.response.NewsResponse
import com.bangkit.stuntack.data.remote.response.PredictionRequest
import retrofit2.Call
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface ApiService {
    @POST("predict")
    suspend fun predict(@Body request: PredictionRequest): Response<ModelResponse>

    @GET("events")
    fun getListNews(
        @Query("active") isActive: Boolean
    ): Call<NewsResponse>

}