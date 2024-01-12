package it.netfarm.mymedbook.mymedtag.api;

import android.content.Context;
import android.util.Log;

import com.google.gson.ExclusionStrategy;
import com.google.gson.FieldAttributes;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

import it.netfarm.mymedbook.mymedtag.BuildConfig;
import it.netfarm.mymedbook.mymedtag.Constants;
import it.netfarm.mymedbook.mymedtag.utils.GsonUTCDateAdapter;
import it.netfarm.mymedbook.mymedtag.utils.SettingsUtils;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.adapter.rxjava.RxJavaCallAdapterFactory;
import retrofit2.converter.gson.GsonConverterFactory;
import rx.schedulers.Schedulers;


public class ApiManager {

    static final String AUTHORIZATION = "Authorization";
    private static ApiManager instance = null;
    private static MyMedTagServiceInterface service;
    private static Retrofit retrofitInstance;
    private RxJavaCallAdapterFactory rxAdapter = RxJavaCallAdapterFactory.createWithScheduler(Schedulers.io());
    public static Gson gson;

    public static ApiManager getInstance() {
        if (instance == null)
            instance = new ApiManager();
        return instance;
    }

    public MyMedTagServiceInterface getRetrofitInstance() {
        return service;
    }

    //
    public void init(final Context applicationContext) {
        init(applicationContext, Constants.BASE_URL);

    }

    public Retrofit getRetroInstance(){
        return retrofitInstance;
    }

    public void init(final Context applicationContext, String baseUrl) {
        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
// set your desired log level
        logging.setLevel(BuildConfig.DEBUG ? HttpLoggingInterceptor.Level.BODY : HttpLoggingInterceptor.Level.NONE);

        OkHttpClient client = new OkHttpClient.Builder().authenticator(new ApiAuthenticator(applicationContext))
                .addInterceptor(logging)
                .readTimeout(1, TimeUnit.MINUTES)
                .writeTimeout(1, TimeUnit.MINUTES)
                .addInterceptor(new Interceptor() { //ad ogni richiesta invio come parametro ulteriore la lingua
                    @Override
                    public Response intercept(Chain chain) throws IOException {
                        String authToken = SettingsUtils.getToken(applicationContext);
                        Request.Builder builder = chain.request().newBuilder()
                                .addHeader("lang", Locale.getDefault().getLanguage());
                        builder.addHeader("Accept", "application/json");
                        if (authToken != null) {
                            String token = "Bearer " + authToken;
                            builder.header(AUTHORIZATION, token);   //di base aggiungo sempre il token di autenticazione
                            if (BuildConfig.DEBUG)
                                Log.i("AUTHTOKEN", token);
                        }
                        return chain.proceed(builder.build());
                    }
                }).build();
        gson = new GsonBuilder().serializeNulls()
                .enableComplexMapKeySerialization()
                .addSerializationExclusionStrategy(new ExclusionStrategy() {
                    @Override
                    public boolean shouldSkipField(FieldAttributes f) {
                        return f.getAnnotation(SkipSerialisation.class) != null; //ho creato un'annotazione che mi esclude il campo dalla serializazzione
                    }

                    @Override
                    public boolean shouldSkipClass(Class<?> clazz) {
                        return false;
                    }
                })
                .registerTypeAdapter(Date.class, new GsonUTCDateAdapter())
                //.registerTypeAdapter(Date.class, new GsonUTCDateAdapter())
                .create();

        retrofitInstance = new Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .addCallAdapterFactory(rxAdapter)
                .build();
        service = ApiManager.retrofitInstance.create(MyMedTagServiceInterface.class);
    }


}
