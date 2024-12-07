package com.bangkit.stuntack.data.remote.retrofit

import com.bangkit.stuntack.data.remote.response.NewsResponse
import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Query

interface ApiService {
    @GET("events")
    fun getListNews(
        @Query("active") isActive: Boolean
    ): Call<NewsResponse>
}