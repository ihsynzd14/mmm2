package it.netfarm.mymedbook.mymedtag.utils;

import android.support.v7.app.AppCompatActivity;

import com.afollestad.materialdialogs.MaterialDialog;

import it.netfarm.mymedbook.mymedtag.R;
import rx.Subscription;


abstract public class BaseNetworkActivity extends AppCompatActivity {
    protected MaterialDialog dialog;
    protected Subscription subscription;


    @Override
    protected void onDestroy() {
        if(subscription != null)
            subscription.unsubscribe();
        super.onDestroy();
    }

    protected void createDialogLoading() {
        cancelDialog();
        dialog = new MaterialDialog.Builder(this).content(R.string.loading_data)
                .progress(true, -1)
                .cancelable(false)
                .show();
    }

    protected void cancelDialog() {
        if (dialog != null)
            dialog.dismiss();
    }
}
