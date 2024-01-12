package it.netfarm.mymedbook.mymedtag.utils;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import it.netfarm.mymedbook.mymedtag.model.LoginObj;


public class SettingsUtils {
    private static final String USER_ID = "user_id";
    private static final String EMAIL_CODE = "email";
    private static final String PASSWORD_CODE = "password";
    private static final String TOKEN = "token_join";
    private static final String REFRESH_TOKEN = "refresh_token";


    public static void setUserId(Context activity, int id) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(activity);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putInt(USER_ID, id);
        editor.commit();        //il facebook_token mi server subito per cui uso il commit
    }

    public static int getUserId(Context context) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        return sharedPref.getInt(USER_ID, 0);
    }

    public static String getProfileEmail(Context context) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        return sharedPref.getString(EMAIL_CODE, null);
    }

    public static void setProfileEmail(Context context, String email) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString(EMAIL_CODE, email);
        editor.apply();
    }

    public static String getProfilePassword(Context context) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        return sharedPref.getString(PASSWORD_CODE, null);
    }

    public static void setProfilePassword(Context context, String password) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString(PASSWORD_CODE, password);
        editor.apply();
    }

    public static void setToken(Context context, String token) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString(TOKEN, token);
        editor.commit();        //il facebook_token mi server subito per cui uso il commit
    }

    public static String getToken(Context context) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        return sharedPref.getString(TOKEN, null);
    }

    public static void setRefreshToken(Context context, String token) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString(REFRESH_TOKEN, token);
        editor.commit();        //il facebook_token mi server subito per cui uso il commit
    }

    public static String getRefreshToken(Context context) {
        SharedPreferences sharedPref = PreferenceManager
                .getDefaultSharedPreferences(context);
        return sharedPref.getString(REFRESH_TOKEN, null);
    }

    public static void setFirstToken(Context context, LoginObj loginObj) {
        SettingsUtils.setToken(context, loginObj.getAccess_token());
        SettingsUtils.setRefreshToken(context, loginObj.getRefresh_token());
        //SettingsUtils.setUserId(context, loginObj.getPk());
    }


    public static void logout(Context context) {
        SettingsUtils.setToken(context, null);
        SettingsUtils.setRefreshToken(context, null);
        SettingsUtils.setUserId(context, 0);
        RealmUtils.clearDb();
        //SettingsUtils.setUserId(context, loginObj.getPk());
    }
}
