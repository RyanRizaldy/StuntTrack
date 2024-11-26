package com.bangkit.stuntack.ui.welcome

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.bangkit.stuntack.MainActivity
import com.bangkit.stuntack.R

class WelcomeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)
        supportActionBar?.hide()

        val buttonStarted: Button = findViewById(R.id.button_started)

        buttonStarted.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            intent.putExtra("open_tracking", true)
            startActivity(intent)
            finish()
        }
    }
}