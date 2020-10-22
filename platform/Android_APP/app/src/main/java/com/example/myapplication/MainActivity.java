package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

import java.io.IOException;
import java.io.InputStream;

public class MainActivity extends AppCompatActivity {

    // Used to load the 'native-lib' library on application startup.
    static {
        System.loadLibrary("native-lib");
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Example of a call to a native method
        TextView tv = findViewById(R.id.sample_text);
        AssetManager am = getAssets();

        // Bitmap
        String filename = "test.png";
        Bitmap bitmap = null;
        try
        {
            InputStream is = am.open(filename);
            bitmap = BitmapFactory.decodeStream(is);
            is.close();
        }catch (IOException e)
        {
            e.printStackTrace();
        }
        tv.setText(stringFromJNI(am, bitmap));
    }

    /**
     * A native method that is implemented by the 'native-lib' native library,
     * which is packaged with this application.
     */
    public native String stringFromJNI(AssetManager am, Bitmap bitmap);
}