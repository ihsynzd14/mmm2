package it.netfarm.mymedbook.mymedtag;

import android.content.Context;
import android.graphics.drawable.Animatable;
import android.graphics.drawable.Drawable;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.os.CountDownTimer;
import android.os.Vibrator;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.AppCompatDrawableManager;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.Locale;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;

public class AlarmDialogActivity extends AppCompatActivity {
    private static final int VIBRARY_FOR = 500;
    private MediaPlayer mMediaPlayer;
    @BindView(R.id.time_text)
    TextView timeText;
    @BindView(R.id.image_bell)
    ImageView imageBell;
    Vibrator mVibrator;
    private CountDownTimer mCountDown;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_alarm_dialog);
        ButterKnife.bind(this);
        mVibrator = (Vibrator) getSystemService(VIBRATOR_SERVICE);
        mMediaPlayer = MediaPlayer.create(this, R.raw.sos);
        mMediaPlayer.setLooping(true);

        final Animation animShake = AnimationUtils.loadAnimation(this, R.anim.move_bell);
        imageBell.startAnimation(animShake);
        mCountDown = new CountDownTimer(5000, 1000) {
            @Override
            public void onTick(long millisUntilFinished) {

                timeText.setText(String.format(Locale.US, "%s %ds %s",
                        getString(R.string.mancano), millisUntilFinished / 1000,
                        getString(R.string.al_lancio)));

                if (mVibrator != null)
                    mVibrator.vibrate(VIBRARY_FOR);

            }

            @Override
            public void onFinish() {
                AudioManager mAudioManager = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
                if (mAudioManager != null)
                    mAudioManager.setStreamVolume(AudioManager.STREAM_MUSIC, mAudioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC), 0);
                mMediaPlayer.start();
                timeText.setText(R.string.richiesta_di_assistenza_in_corso);
            }
        }.start();
    }

    @OnClick(R.id.image_bell)
    void clickBell() {
        finish();
    }

    @Override
    protected void onDestroy() {
        if (mCountDown != null)
            mCountDown.cancel();
        if (mMediaPlayer != null)
            mMediaPlayer.stop();
        if (mVibrator != null)
            mVibrator.cancel();

        super.onDestroy();
    }
}
