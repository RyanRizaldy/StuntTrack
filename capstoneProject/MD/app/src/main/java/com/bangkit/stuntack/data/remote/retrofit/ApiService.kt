package com.bangkit.stuntack.data.remote.retrofit

import com.bangkit.stuntack.data.remote.response.ModelResponse
import com.bangkit.stuntack.data.remote.response.NewsDetailResponse
import com.bangkit.stuntack.data.remote.response.NewsResponseItem
import com.bangkit.stuntack.data.remote.response.PredictionRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface ApiService {
    @POST("predict")
    suspend fun predict(
        @Body
        request: PredictionRequest
    ): Response<ModelResponse>


    @GET("articles")
    suspend fun getNews(): List<NewsResponseItem>

    @GET("articles/{id}")
    suspend fun getNewsDetail(
        @Path("id") newsId: Int
    ): NewsDetailResponse

}