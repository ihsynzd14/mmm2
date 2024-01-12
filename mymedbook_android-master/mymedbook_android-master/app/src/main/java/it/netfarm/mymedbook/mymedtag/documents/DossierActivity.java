package it.netfarm.mymedbook.mymedtag.documents;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v7.app.ActionBar;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;

import com.afollestad.materialdialogs.DialogAction;
import com.afollestad.materialdialogs.MaterialDialog;

import java.util.ArrayList;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import it.netfarm.mymedbook.mymedtag.R;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.model.MyDossiers;
import it.netfarm.mymedbook.mymedtag.utils.BaseNetworkActivity;
import rx.Subscriber;
import rx.Subscription;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

public class DossierActivity extends BaseNetworkActivity implements DossiersAdapter.DossierListner {

    @BindView(R.id.recycleDossiers)
    RecyclerView recyclerDossier;
    private ArrayList<MyDossiers> listDossier = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dossier);
        ButterKnife.bind(this);
        recyclerDossier.setLayoutManager(new LinearLayoutManager(this));
        recyclerDossier.setAdapter(new DossiersAdapter(listDossier, this));
        final ActionBar supportActionBar = getSupportActionBar();
        if (supportActionBar != null) {
            supportActionBar.setDisplayHomeAsUpEnabled(true);
            supportActionBar.setDisplayShowHomeEnabled(true);
            supportActionBar.setTitle(R.string.my_dossiers);
        }
        askForContents();
    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }

    private void askForContents() {
        if (subscription != null)
            subscription.unsubscribe();
        createDialogLoading();
        subscription = ApiManager.getInstance().getRetrofitInstance().askMyDossier()
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new Subscriber<List<MyDossiers>>() {
                    @Override
                    public void onCompleted() {
                        cancelDialog();

                    }

                    @Override
                    public void onError(Throwable e) {
                        cancelDialog();
                        dialog = new MaterialDialog.Builder(DossierActivity.this).content(R.string.impossibile_rec_lista)
                                .cancelable(false)
                                .positiveText(R.string.riprova)
                                .onPositive(new MaterialDialog.SingleButtonCallback() {
                                    @Override
                                    public void onClick(@NonNull MaterialDialog dialog, @NonNull DialogAction which) {
                                        askForContents();
                                    }
                                }).negativeText(R.string.chiudi)
                                .onNegative(new MaterialDialog.SingleButtonCallback() {
                                                @Override
                                                public void onClick(@NonNull MaterialDialog dialog, @NonNull DialogAction which) {
                                                    finish();
                                                }
                                            }
                                )
                                .show();
                    }

                    @Override
                    public void onNext(List<MyDossiers> myDossiers) {
                        listDossier.clear();
                        listDossier.addAll(myDossiers);
                        recyclerDossier.getAdapter().notifyDataSetChanged();

                    }
                });
    }


    @Override
    public void clickDossier(MyDossiers dossier) {
        DocumentsActivity.startDocActivity(this, dossier);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == Activity.RESULT_OK) {
            askForContents();
        }
    }
}
