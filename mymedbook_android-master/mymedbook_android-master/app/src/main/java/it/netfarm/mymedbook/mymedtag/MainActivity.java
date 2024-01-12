package it.netfarm.mymedbook.mymedtag;

import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Bundle;
import android.support.customtabs.CustomTabsIntent;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.content.res.AppCompatResources;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.facebook.drawee.view.SimpleDraweeView;

import java.io.File;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import io.realm.Realm;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.documents.DossierActivity;
import it.netfarm.mymedbook.mymedtag.model.MMGroup;
import it.netfarm.mymedbook.mymedtag.model.MMUser;
import it.netfarm.mymedbook.mymedtag.model.MedTagResp;
import it.netfarm.mymedbook.mymedtag.start.StartActivity;
import it.netfarm.mymedbook.mymedtag.utils.GenericUtils;
import it.netfarm.mymedbook.mymedtag.utils.RealmUtils;
import it.netfarm.mymedbook.mymedtag.utils.SettingsUtils;
import okhttp3.MediaType;
import okhttp3.RequestBody;
import pl.aprilapps.easyphotopicker.DefaultCallback;
import pl.aprilapps.easyphotopicker.EasyImage;
import rx.Subscriber;
import rx.Subscription;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

import static it.netfarm.mymedbook.mymedtag.Constants.BASE;

public class MainActivity extends AppCompatActivity {

    public static final String EXTRA_USER_TAG = "USER_TAG_EXTRA";
    private static final int EDIT_IMAGE_PROFILE = 435;
    private static final String CDV = "cdv";
    private static final String CDV_OPERATORE = "operatore_sanitario_cdv";
    private List<Object> list = new ArrayList<>();
    private AdapterItems adapter;
    @BindView(R.id.recycle)
    RecyclerView recyclerView;
    @BindView(R.id.textView)
    TextView textName;
    @BindView(R.id.textView2)
    TextView textSurname;
    @BindView(R.id.imageView)
    SimpleDraweeView imageView;
    @BindView(R.id.button)
    Button logout;
    @BindView(R.id.date_text)
    TextView dateText;
    @BindView(R.id.fab_help)
    View fabHelp;
    @BindView(R.id.dossier)
    TextView dossierText;
    private Subscription subscription;
    private boolean isMyUser = false;
    private Subscription subscriptionAvatar;
    private boolean canChangePhoto;
    private int pkCurrUser;
    private String currentTag;
    private boolean isFastHelp;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ButterKnife.bind(this);
        recyclerView.setHasFixedSize(true);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new AdapterItems(list);
        recyclerView.setAdapter(adapter);
        Drawable img = AppCompatResources.getDrawable(this, R.drawable.ic_exit_to_app);
        logout.setCompoundDrawables(img, null, null, null);
        String tagUser = getIntent().getStringExtra(EXTRA_USER_TAG);

        if (tagUser == null) {
            MMUser user = RealmUtils.getMyUser(this);
            if (user != null)
                updateView(user, true);
            askMyUser();
        } else {
            MMUser myUser = RealmUtils.getMyUser(this);
            MMUser user = RealmUtils.getOtherUsers(tagUser);
            if (myUser != null && user != null && myUser.getPk() == user.getPk()) {
                updateView(myUser, true);
                askMyUser();
                if (myUser.getFastHelp() != null && !myUser.getFastHelp().isEmpty() || AppController.isMMTFlavour()) {
                    AssistanceActivity.startInstance(this, tagUser);
                } else
                    startActivity(new Intent(this, AlarmDialogActivity.class));

            } else {
                if (user != null)
                    updateView(user, false);
                else {
                    Toast.makeText(MainActivity.this, R.string.impossibile_caricare_utente, Toast.LENGTH_LONG).show();
                    finish();
                }
            }
        }

    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        String tagUser = intent.getStringExtra(EXTRA_USER_TAG);
        if (tagUser == null) {
            //  askMyUser();
            return;
        }
        MMUser user = RealmUtils.getOtherUsers(tagUser);
        if (user != null) {
            MMUser myUser = RealmUtils.getMyUser(this);
            if (myUser != null && myUser.getPk() == user.getPk()) {
                updateView(user, true);
                if (myUser.getFastHelp() != null && !myUser.getFastHelp().isEmpty() && AppController.isMMTFlavour()) {
                    AssistanceActivity.startInstance(this, tagUser);
                } else
                    startActivity(new Intent(this, AlarmDialogActivity.class));
            } else
                updateView(user, false);
        } else {
            Toast.makeText(MainActivity.this, R.string.impossibile_caricare_utente, Toast.LENGTH_LONG).show();
            finish();
        }

    }

    private void askMyUser() {
        subscription = ApiManager.getInstance().getRetrofitInstance().askMyMedTag().subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new Subscriber<MedTagResp>() {
                    @Override
                    public void onCompleted() {

                    }

                    @Override
                    public void onError(Throwable e) {
                        Toast.makeText(MainActivity.this, R.string.richiesta_non_buon_fine, Toast.LENGTH_LONG).show();
                    }

                    @Override
                    public void onNext(MedTagResp medTagResp) {
                        list.clear();
                        MMUser user = medTagResp.getUser();
                        SettingsUtils.setUserId(MainActivity.this, user.getPk());
                        updateView(user, true);
                    }
                });
    }

    @OnClick(R.id.fab_help)
    void clickHelp() {
        if (isFastHelp) {
            AssistanceActivity.startInstance(this, currentTag);//currentTag nullo se si tratta dell'utente loggato
        } else {
            AlertDialog.Builder build = new AlertDialog.Builder(this).setMessage(R.string.iscriviti)
                    .setPositiveButton(getString(R.string.vai_al_sito), new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            String url = BASE + "sottoscrizione-pacchetto-fasthelp-plus/";
                            CustomTabsIntent.Builder builder = new CustomTabsIntent.Builder();
                            CustomTabsIntent customTabsIntent = builder.build();
                            customTabsIntent.launchUrl(MainActivity.this, Uri.parse(url));
                        }
                    })
                    .setNegativeButton(R.string.chiudi, new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {

                        }
                    });
            AlertDialog dialog = build.create();
            dialog.show();
        }
    }

    @OnClick(R.id.imageView)
    void clickImage() {
        if (canChangePhoto)
            EasyImage.openCamera(this, EDIT_IMAGE_PROFILE);
    }

    @OnClick(R.id.info_image)
    void clickInfo() {
        new AlertDialog.Builder(this).setMessage(R.string.nfc_advice).show();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        EasyImage.handleActivityResult(requestCode, resultCode, data, this, new DefaultCallback() {
            @Override
            public void onImagePickerError(Exception e, EasyImage.ImageSource source, int type) {
                //Some error handling
            }

            @Override
            public void onImagePicked(File imageFile, EasyImage.ImageSource source, int type) {
                sendImage(imageFile);


            }
        });
    }

    private void sendImage(File file) {
        file = GenericUtils.saveBitmapToFile(file);
        if (file == null)
            return;
        //RequestBody requestBody = RequestBody.create(MediaType.parse("multipart/form-data"), file);
        // MultipartBody.Part imageFileBody = MultipartBody.Part.createFormData("upload", file.getName(), requestBody);

        if (canChangePhoto) { //se è true posso inviare la foto
            if (subscriptionAvatar != null)
                subscriptionAvatar.unsubscribe();//evito di avere sottoscrizioni pendenti
            subscriptionAvatar = ApiManager.getInstance().getRetrofitInstance().uploadAvatarImage(pkCurrUser, RequestBody.create(MediaType.parse("image"), file))
                    .subscribeOn(Schedulers.io())
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribe(new Subscriber<MMUser>() {
                        @Override
                        public void onCompleted() {

                        }

                        @Override
                        public void onError(Throwable e) {
                            Toast.makeText(MainActivity.this, R.string.invio_non_riuscito, Toast.LENGTH_LONG).show();
                        }

                        @Override
                        public void onNext(MMUser userResp) {
                            Realm realm = Realm.getDefaultInstance();

                            int userId = userResp.getPk();
                            MMUser user = Realm.getDefaultInstance().where(MMUser.class).equalTo("pk", userId).findFirst();
                            if (user != null) {
                                realm.beginTransaction();
                                user.setAvatar(userResp.getAvatar());
                                realm.commitTransaction();
                                imageView.setImageURI(user.getAvatarUrl());
                                realm.close();
                            }

                        }
                    });
        }
    }

    @Override
    protected void onDestroy() {
        if (subscription != null)
            subscription.unsubscribe();
        if (subscriptionAvatar != null)
            subscriptionAvatar.unsubscribe();
        super.onDestroy();
    }

    private void updateView(final MMUser user, boolean myUser) {
        canChangePhoto = myUser;
        pkCurrUser = user.getPk();
        currentTag = user.getMymedtag_code();
        if (!canChangePhoto && CDV.equals(BuildConfig.FLAVOR)) {  //se non è il mio utente devo controllare se l'ambiente è quello di Campo del Vescovo
            MMUser myuser = RealmUtils.getMyUser(this);
            if (myuser != null && myuser.getGroups() != null)
                for (MMGroup group : myuser.getGroups()) {//controllo se l'utente loggato i diritti per cambiare la foto
                    if (CDV_OPERATORE.equals(group.getName())) {
                        canChangePhoto = true;
                        break;
                    }
                }
        }
        list.clear();
        boolean header = false;
        if (user.getLifesaverInternal() != null && user.getLifesaverInternal().getAttribute() != null && user.getLifesaverInternal().getAttribute().getName() != null) {
            list.add(user.getLifesaverInternal());
            header = true;
        }
        if (user.getBirthday() == null)
            dateText.setVisibility(View.GONE);
        else {
            dateText.setVisibility(View.VISIBLE);
            dateText.setText(String.format("%s: %s", getString(R.string.data_di_nascita), DateFormat.getDateInstance(DateFormat.SHORT, Locale.getDefault()).format(user.getBirthday())));
        }
        if (user.getAttributes_groupsInternal() != null)
            list.addAll(user.getCompleteList());
        if (user.getTherapies() != null)
            list.addAll(user.getTherapies());
        adapter.hasHeader(header);
        adapter.notifyDataSetChanged();
        textName.setVisibility(TextUtils.isEmpty(user.getFirst_name()) ? View.GONE : View.VISIBLE);
        textName.setText(user.getFirst_name());
        textSurname.setVisibility(TextUtils.isEmpty(user.getLast_name()) ? View.GONE : View.VISIBLE);
        textSurname.setText(user.getLast_name());
        imageView.setImageURI(user.getAvatarUrl());
        HashMap<String, List<HashMap<String, String>>> fh = user.getFastHelp();
        if (BuildConfig.FLAVOR.equals("cdv")) {
            fabHelp.setVisibility(View.GONE);
        }
        isFastHelp = !(fh == null || fh.isEmpty() || !AppController.isMMTFlavour());
        Realm realm = Realm.getDefaultInstance();
        realm.executeTransaction(new Realm.Transaction() {
            @Override
            public void execute(Realm realm) {
                realm.insertOrUpdate(user);
            }
        });
        if (myUser) {
            logout.setVisibility(View.VISIBLE);
            dossierText.setVisibility(View.VISIBLE);
            isMyUser = true;
        } else {
            logout.setVisibility(View.GONE);
            dossierText.setVisibility(View.GONE);
            isMyUser = false;
        }
    }

    @OnClick(R.id.dossier)
    void clickDossier() {
        startActivity(new Intent(this,DossierActivity.class));
    }

    @OnClick(R.id.button)
    void clickLogout() {
        SettingsUtils.logout(this);
        startActivity(new Intent(this, StartActivity.class));
        finish();
    }
}
