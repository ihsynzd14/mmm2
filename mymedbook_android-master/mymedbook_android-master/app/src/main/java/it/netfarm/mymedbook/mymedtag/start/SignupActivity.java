package it.netfarm.mymedbook.mymedtag.start;

import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.customtabs.CustomTabsIntent;
import android.support.v7.app.AppCompatActivity;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.Toast;

import com.afollestad.materialdialogs.DialogAction;
import com.afollestad.materialdialogs.MaterialDialog;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import it.netfarm.mymedbook.mymedtag.R;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.utils.StringUtils;
import okhttp3.ResponseBody;
import retrofit2.adapter.rxjava.HttpException;
import rx.Subscriber;
import rx.Subscription;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

import static it.netfarm.mymedbook.mymedtag.Constants.BASE;

public class SignupActivity extends AppCompatActivity {
    @BindView(R.id.name_edit)
    EditText nameEdit;
    @BindView(R.id.surname_edit)
    EditText surnameEdit;
    @BindView(R.id.password_edit)
    EditText passwordEdit;
    @BindView(R.id.password_repeat_edit)
    EditText passworRepeatEdit;
    @BindView(R.id.check_profilation)
    CheckBox checkProfilation;
    @BindView(R.id.check_geo)
    CheckBox checkGeo;
    @BindView(R.id.check_share)
    CheckBox checkShare;
    @BindView(R.id.email_edit)
    EditText emailEdit;
    private Subscription subscription;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signup);
        ButterKnife.bind(this);
    }

    @Override
    protected void onDestroy() {
        if (subscription != null)
            subscription.unsubscribe();
        super.onDestroy();
    }

    @OnClick(R.id.button_signup)
    void clickSignup() {
        if (!checkConditions()) //se le condizioni non sono rispettate non effettua la registrazione
            return;

        if (subscription != null)
            subscription.unsubscribe();
        subscription = ApiManager.getInstance().getRetrofitInstance()
                .signup(
                        nameEdit.getText().toString(),
                        surnameEdit.getText().toString(),
                        emailEdit.getText().toString(),
                        passwordEdit.getText().toString())
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new Subscriber<ResponseBody>() {
                    @Override
                    public void onCompleted() {

                    }

                    @Override
                    public void onError(Throwable e) {
                        if (e instanceof HttpException && ((HttpException) e).code() == 400) {
                            new MaterialDialog.Builder(SignupActivity.this).content(R.string.already_exist).show();
                        } else
                            Toast.makeText(SignupActivity.this, R.string.signup_error, Toast.LENGTH_LONG).show();
                    }

                    @Override
                    public void onNext(ResponseBody requestBody) {
                        new MaterialDialog.Builder(SignupActivity.this).title(R.string.success)
                                .cancelable(false)
                                .positiveText(R.string.ok)
                                .content(R.string.signup_completed)
                                .onPositive(new MaterialDialog.SingleButtonCallback() {
                                    @Override
                                    public void onClick(@NonNull MaterialDialog dialog, @NonNull DialogAction which) {
                                        finish();
                                    }
                                }).show();

                    }
                });
    }


    private boolean checkConditions() {
        if (StringUtils.EditIsEmpty(nameEdit, 0) || StringUtils.EditIsEmpty(surnameEdit, 0)
                || StringUtils.CheckInvalidEmail(emailEdit)
                || StringUtils.EditIsEmpty(passwordEdit, 6) || StringUtils.notPasswordEquals(passwordEdit, passworRepeatEdit)
                || !CheckPress(checkProfilation) || !CheckPress(checkGeo) || !CheckPress(checkShare))
            return false;
        return true;
    }

    private boolean CheckPress(CheckBox checkBox) {
        boolean isCheck = checkBox.isChecked();
        if (!isCheck)
            checkBox.setError(getString(R.string.devi_dare_il_tuo_consenso));
        return isCheck;
    }

    @OnClick(R.id.privacy_text_conditions)
    void clickPrivacy() {
        String url = BASE + "templates/privacy_text.html";
        CustomTabsIntent.Builder builder = new CustomTabsIntent.Builder();
        CustomTabsIntent customTabsIntent = builder.build();
        customTabsIntent.launchUrl(this, Uri.parse(url));
    }
}
