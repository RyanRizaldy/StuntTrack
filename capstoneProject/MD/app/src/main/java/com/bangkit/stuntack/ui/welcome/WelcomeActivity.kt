package com.bangkit.stuntack.ui.welcome

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import com.bangkit.stuntack.MainActivity
import com.bangkit.stuntack.R
import com.bangkit.stuntack.databinding.ActivityWelcomeBinding


class WelcomeActivity : AppCompatActivity() {

    private lateinit var binding: ActivityWelcomeBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Inisialisasi binding dengan ViewBinding
        binding = ActivityWelcomeBinding.inflate(layoutInflater)
        setContentView(binding.root)

        supportActionBar?.hide()

        playAnimation()

        binding.buttonStarted.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            intent.putExtra("open_tracking", true)
            startActivity(intent)
            finish()
        }
    }

    private fun playAnimation() {
        ObjectAnimator.ofFloat(binding.imageView, View.TRANSLATION_X, -20f, 20f).apply {
            duration = 6000
            repeatCount = ObjectAnimator.INFINITE
            repeatMode = ObjectAnimator.REVERSE
        }.start()

        val title = ObjectAnimator.ofFloat(binding.textView, View.ALPHA, 1f).setDuration(100)
        val desc = ObjectAnimator.ofFloat(binding.textView3, View.ALPHA, 1f).setDuration(100)
        val started = ObjectAnimator.ofFloat(binding.buttonStarted, View.ALPHA, 1f).setDuration(100)

        AnimatorSet().apply {
            playSequentially(title, desc, started)
            startDelay = 100
        }.start()
    }
}