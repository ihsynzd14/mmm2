package it.netfarm.mymedbook.mymedtag;

import android.util.Log;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.FirebaseInstanceIdService;

public class MyFirebaseInstanceIDService extends FirebaseInstanceIdService {

    @Override
    public void onTokenRefresh() {
        super.onTokenRefresh();
        if (BuildConfig.DEBUG)
            Log.i("TOKEN_FIRE", FirebaseInstanceId.getInstance().getToken());
        // SettingsUtils.setFirebaseToken(this, FirebaseInstanceId.getInstance().getToken());
    }
}
