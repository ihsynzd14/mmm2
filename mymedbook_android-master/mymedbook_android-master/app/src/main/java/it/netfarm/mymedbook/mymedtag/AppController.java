package it.netfarm.mymedbook.mymedtag;

import android.support.multidex.MultiDexApplication;

import com.crashlytics.android.Crashlytics;
import com.crashlytics.android.core.CrashlyticsCore;
import com.facebook.drawee.backends.pipeline.Fresco;

import io.fabric.sdk.android.Fabric;
import io.realm.Realm;
import io.realm.RealmConfiguration;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;

public class AppController extends MultiDexApplication {

    @Override
    public void onCreate() {
        super.onCreate();
        Fabric.with(this, new Crashlytics.Builder().core(new CrashlyticsCore.Builder()
                .disabled(BuildConfig.DEBUG).build()).build(), new Crashlytics());
        ApiManager.getInstance().init(getApplicationContext());
        Fresco.initialize(this);
        Realm.init(this);
        RealmConfiguration config = new RealmConfiguration.Builder().deleteRealmIfMigrationNeeded()
                .build();
        Realm.setDefaultConfiguration(config);
    }


    public static boolean isMMTFlavour() {
        return "mymedtag".equals(BuildConfig.FLAVOR) || "local".equals(BuildConfig.FLAVOR);
    }
}
