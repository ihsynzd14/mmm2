package it.netfarm.mymedbook.mymedtag.api;

import android.support.annotation.NonNull;

import java.util.List;

import it.netfarm.mymedbook.mymedtag.model.GenericResp;
import it.netfarm.mymedbook.mymedtag.model.HelpRequestBody;
import it.netfarm.mymedbook.mymedtag.model.LoginObj;
import it.netfarm.mymedbook.mymedtag.model.MMUser;
import it.netfarm.mymedbook.mymedtag.model.MedTagResp;
import it.netfarm.mymedbook.mymedtag.model.MyDossiers;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Field;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.Headers;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;
import rx.Observable;


public interface MyMedTagServiceInterface {

    @FormUrlEncoded
    @POST("oauth/token/")
    Call<LoginObj> refreshRequest(@NonNull @Field("refresh_token") String refresh,
                                  @NonNull @Field("grant_type") String grant_tipe,
                                  @NonNull @Field("client_id") String client_id);

    @FormUrlEncoded
    @POST("oauth/token/")
    Observable<LoginObj> loginRequestObservable(@NonNull @Field("username") String username,
                                                @NonNull @Field("password") String password,
                                                @NonNull @Field("client_id") String client_id,
                                                @NonNull @Field("grant_type") String grant_tipe);

    @GET("mymedtag/")
    Observable<MedTagResp> askMyMedTag();


    @GET("mymedtag/")
    Observable<MedTagResp> askUserMedTag(@Query("code") String id);

    @Headers("Content-Disposition:attachment;filename=\"*\"")
    @POST("upload/guest/"/*"upload/profile/avatars/"*/)
    Observable<MMUser> uploadAvatarImage(@Query("guest_id") int guestId, @Body RequestBody description);


    // @Headers("Content-Disposition:inline;")
    @POST("upload/dossier/{pk_dossier}/"/*"upload/profile/avatars/"*/)
    Observable<MyDossiers> uploadDossierFile(@Path("pk_dossier") int pkDossier,
                                             @Header("Content-Disposition") String filename,
                                             @Body RequestBody description);

    @POST("COC/assistance/request/")
    Observable<GenericResp> sendRequestHelp(@Body HelpRequestBody helpRequestBody);

    @FormUrlEncoded
    @POST("register/")
    Observable<ResponseBody> signup(@Field("first_name") String name, @Field("last_name") String surname, @Field("email") String email, @Field("password") String password);

    @GET("dossier/")
    Observable<List<MyDossiers>> askMyDossier();
}
