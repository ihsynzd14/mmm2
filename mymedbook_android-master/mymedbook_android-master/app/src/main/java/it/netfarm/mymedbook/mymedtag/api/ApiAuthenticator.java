package it.netfarm.mymedbook.mymedtag.api;

import android.content.Context;

import java.io.IOException;
import java.util.List;

import it.netfarm.mymedbook.mymedtag.BuildConfig;
import it.netfarm.mymedbook.mymedtag.model.LoginObj;
import it.netfarm.mymedbook.mymedtag.utils.SettingsUtils;
import okhttp3.Authenticator;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.Route;
import retrofit2.Call;


public class ApiAuthenticator implements Authenticator {


    private Context applicationContext;

    public ApiAuthenticator(Context context) {
        this.applicationContext = context;
    }

    @Override
    public Request authenticate(Route route, Response resp) throws IOException {
        if (resp.request() == null)
            return null;
        List<String> listEncodedPath = resp.request().url().encodedPathSegments();
        if (listEncodedPath.contains("oauth") && listEncodedPath.contains("token")) //evito il loop che tenta di refreshare il token quando il token di refresh risulta non valido
            return null;

        SettingsUtils.setToken(applicationContext, null);

        if (SettingsUtils.getRefreshToken(applicationContext) == null) {//non ho refresh token
            return null;
        }
        Call<LoginObj> callAuth = ApiManager.getInstance().getRetrofitInstance()        //richiesta per avere un nuovo token
                .refreshRequest(SettingsUtils.getRefreshToken(applicationContext), "refresh_token", BuildConfig.CLIENT_ID);
        LoginObj respString = callAuth.execute().body();


        if (callAuth.isExecuted())      //aspetto in maniera sincrona la risposta
            if (respString != null) {
                final String newAuthToken = respString.getAccess_token();   //ho un nuovo token
                SettingsUtils.setToken(applicationContext, newAuthToken);
                SettingsUtils.setRefreshToken(applicationContext, respString.getRefresh_token());
                return resp.request().newBuilder()
                        .header(ApiManager.AUTHORIZATION, "Bearer " + newAuthToken) //fa l'override dell'header con la stessa chiave (così cancella il vecchio token)
                        .build();

            }


        return null;  //non ho un nuovo token quindi faccio passare la richiesta senza ulteriori modifiche
    }
}