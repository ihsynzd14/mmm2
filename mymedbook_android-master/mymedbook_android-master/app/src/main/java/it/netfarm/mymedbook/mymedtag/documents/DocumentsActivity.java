package it.netfarm.mymedbook.mymedtag.documents;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.customtabs.CustomTabsIntent;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.ActionBar;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.widget.Toast;

import com.afollestad.materialdialogs.folderselector.FileChooserDialog;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import it.netfarm.mymedbook.mymedtag.R;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.model.Document;
import it.netfarm.mymedbook.mymedtag.model.MyDossiers;
import it.netfarm.mymedbook.mymedtag.utils.BaseNetworkActivity;
import okhttp3.MediaType;
import okhttp3.RequestBody;
import rx.Subscriber;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

import static butterknife.internal.Utils.arrayOf;
import static it.netfarm.mymedbook.mymedtag.Constants.BASE;

public class DocumentsActivity extends BaseNetworkActivity implements AdapterDocuments.DocumentsInterface, FileChooserDialog.FileCallback {

    private static final int CODE_RESULT = 213;
    @BindView(R.id.recycle_doc)
    RecyclerView recycleDoc;

    private static final String ARG_DOSSIER = "arg_dossier";
    private MyDossiers dossier;
    private List<Document> documents = new ArrayList<>();
    private int MY_PERMISSIONS_REQUEST = 234;


    public static void startDocActivity(Activity activity, MyDossiers dossier) {
        Intent intent = new Intent(activity, DocumentsActivity.class);
        intent.putExtra(ARG_DOSSIER, dossier);
        activity.startActivityForResult(intent, CODE_RESULT);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_documents);
        ButterKnife.bind(this);
        final ActionBar supportActionBar = getSupportActionBar();
        if (supportActionBar != null) {
            supportActionBar.setDisplayHomeAsUpEnabled(true);
            supportActionBar.setDisplayShowHomeEnabled(true);
        }
        dossier = (MyDossiers) getIntent().getSerializableExtra(ARG_DOSSIER);
        if (dossier != null && dossier.getDocument_set() != null) {
            documents = dossier.getDocument_set();
            if (supportActionBar != null)
                supportActionBar.setTitle(dossier.getName());
        }
        recycleDoc.setLayoutManager(new LinearLayoutManager(this));
        recycleDoc.setAdapter(new AdapterDocuments(documents, this));
    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }

    @OnClick(R.id.fab_add)
    void clickFabAdd() {
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE),
                    MY_PERMISSIONS_REQUEST);


        } else {
            new FileChooserDialog.Builder(this)
                    .mimeType("*/*")
                    .show(this);
        }
    }

    @Override
    public void clickDoc(Document document) {
        String url = BASE + "media/" + document.getDocument();
        CustomTabsIntent.Builder builder = new CustomTabsIntent.Builder();
        CustomTabsIntent customTabsIntent = builder.build();
        customTabsIntent.launchUrl(this, Uri.parse(url));
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == MY_PERMISSIONS_REQUEST &&
                (grantResults[0] == PackageManager.PERMISSION_GRANTED) &&
                (grantResults[1] == PackageManager.PERMISSION_GRANTED)) {
            clickFabAdd();
        }
    }

    @Override
    public void onFileSelection(@NonNull FileChooserDialog dialog, @NonNull File file) {
        // RequestBody requestFile = RequestBody.create(MediaType.parse("multipart/form-data"), file);
        // MultipartBody.Part body  = MultipartBody.Part.createFormData("attachment", file.getName(), requestFile);
        createDialogLoading();
        String extension = "";
        String path = file.getPath();
        int i = path.lastIndexOf('.');
        int p = Math.max(path.lastIndexOf('/'), path.lastIndexOf('\\'));
        if (i > 0) {
            extension = path.substring(i + 1);
        }
        subscription = ApiManager.getInstance().getRetrofitInstance().uploadDossierFile(
                dossier.getPk(),
                "inline;filename*=UTF-8\"" + file.getName() + "\"",
                RequestBody.create(MediaType.parse("application/" + extension), file))
                .observeOn(AndroidSchedulers.mainThread())
                .subscribeOn(Schedulers.io())
                .subscribe(new Subscriber<MyDossiers>() {
                    @Override
                    public void onCompleted() {

                    }

                    @Override
                    public void onError(Throwable e) {
                        cancelDialog();
                    }

                    @Override
                    public void onNext(MyDossiers dossiers) {
                        cancelDialog();
                        setResult(Activity.RESULT_OK);
                        Toast.makeText(DocumentsActivity.this, R.string.file_inviato_con_successo, Toast.LENGTH_LONG).show();
                        finish();
                    }
                });
    }

    @Override
    public void onFileChooserDismissed(@NonNull FileChooserDialog dialog) {

    }
}
