package it.netfarm.mymedbook.mymedtag.utils;

import android.content.Context;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;

import io.realm.Realm;
import it.netfarm.mymedbook.mymedtag.model.MMUser;


public class RealmUtils {

    public static
    @Nullable
    MMUser getMyUser(Context context) {
        int userId = SettingsUtils.getUserId(context);
        MMUser user = Realm.getDefaultInstance().where(MMUser.class).equalTo("pk", userId).findFirst();
        if (user != null)
            return Realm.getDefaultInstance().copyFromRealm(user);
        return null;
    }

    public static void clearDb() {
        Realm realm = Realm.getDefaultInstance();
        realm.beginTransaction();
        realm.deleteAll();
        realm.commitTransaction();
        realm.close();
    }

    public
    @Nullable
    static MMUser getOtherUsers(@NonNull String tagUser) {
        tagUser = tagUser.toUpperCase();
        MMUser user = Realm.getDefaultInstance().where(MMUser.class).equalTo("mymedtag_code", tagUser).findFirst();
        if (user != null)
            return Realm.getDefaultInstance().copyFromRealm(user);
        return null;
    }
}
