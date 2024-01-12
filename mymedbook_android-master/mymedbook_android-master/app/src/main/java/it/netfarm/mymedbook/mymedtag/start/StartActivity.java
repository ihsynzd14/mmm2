package it.netfarm.mymedbook.mymedtag.start;

import android.Manifest;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.nfc.NfcAdapter;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.net.ConnectException;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import it.netfarm.mymedbook.mymedtag.AppController;
import it.netfarm.mymedbook.mymedtag.BuildConfig;
import it.netfarm.mymedbook.mymedtag.MainActivity;
import it.netfarm.mymedbook.mymedtag.R;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.api.MyMedTagServiceInterface;
import it.netfarm.mymedbook.mymedtag.model.LoginObj;
import it.netfarm.mymedbook.mymedtag.utils.GenericUtils;
import it.netfarm.mymedbook.mymedtag.utils.SettingsUtils;
import it.netfarm.mymedbook.mymedtag.utils.StringUtils;
import rx.Subscriber;
import rx.Subscription;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

public class StartActivity extends AppCompatActivity {
    private static final int MY_PERMISSIONS_REQUEST = 232;
    @BindView(R.id.edit_email)
    EditText editEmail;
    @BindView(R.id.edit_password)
    EditText editPassword;
    @BindView(R.id.progress_login)
    ProgressBar progressBarLogin;
    @BindView(R.id.button_login)
    Button buttonLogin;
    @BindView(R.id.signup)
    TextView buttonRegister;
    @BindView(R.id.text_error)
    TextView textError;
    @BindView(R.id.pass_visibility)
    ImageView passVisibilityImage;
    @BindView(R.id.url_edit)
    EditText urlEdit;
    private Subscription subscription;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        ButterKnife.bind(this);
        boolean needPermission = false;
        if (AppController.isMMTFlavour() &&
                (ActivityCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED
                        ||
                        ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
                        ||
                        ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED
                        || ActivityCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS) != PackageManager.PERMISSION_GRANTED
                )
                ) {
            needPermission = true;
            new AlertDialog.Builder(this).setMessage(R.string.richiesta_permessi)
                    .setOnDismissListener(new DialogInterface.OnDismissListener() {
                        @Override
                        public void onDismiss(DialogInterface dialog) {
                            ActivityCompat.requestPermissions(StartActivity.this,
                                    new String[]{Manifest.permission.CALL_PHONE, Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION,
                                            Manifest.permission.SEND_SMS},
                                    MY_PERMISSIONS_REQUEST);
                        }
                    }).show();

        }

        if (SettingsUtils.getToken(this) != null) {
            editEmail.setText(SettingsUtils.getProfileEmail(this));
            editPassword.setText(SettingsUtils.getProfilePassword(this));
            //if (!needPermission)
            //  clickLogin();
        }
        urlEdit.setText(ApiManager.getInstance().getRetroInstance().baseUrl().toString());
    }

    @Override
    protected void onResume() {
        super.onResume();
        NfcAdapter mNfcAdapter = NfcAdapter.getDefaultAdapter(this);
        if (mNfcAdapter == null) {
            textError.setText(R.string.no_nfc);
            return;
        }
        if (!mNfcAdapter.isEnabled()) {
            textError.setText(R.string.nfc_non_abilitato);
        }
    }

    @OnClick(R.id.pass_visibility)
    void clickPasswordVisibility() {
        if (editPassword.getInputType() == (InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD)) {
            editPassword.setInputType(InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD);
            passVisibilityImage.setImageResource(R.drawable.ic_remove_red_eye);
        } else {
            editPassword.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
            passVisibilityImage.setImageResource(R.drawable.ic_remove_red_eye_line);

        }
        editPassword.setSelection(editPassword.length());

    }

    @OnClick(R.id.signup)
    void clickSignup() {
        startActivity(new Intent(this, SignupActivity.class));
    }

    @OnClick(R.id.button_login)
    void clickLogin() {
        if (StringUtils.EditIsEmpty(editEmail, 5))
            return;
        if (StringUtils.EditIsEmpty(editPassword, 4))
            return;
        if (urlEdit.getVisibility() == View.VISIBLE)
            ApiManager.getInstance().init(getApplicationContext(), urlEdit.getText().toString());

        requestLayoutChange(true);
        final MyMedTagServiceInterface retroInstance = ApiManager.getInstance().getRetrofitInstance();
        final String nomeString = editEmail.getText().toString();
        final String passwordString = editPassword.getText().toString();
        subscription = retroInstance.loginRequestObservable(nomeString, passwordString, BuildConfig.CLIENT_ID, "password")
                .observeOn(AndroidSchedulers.mainThread())
                .subscribeOn(Schedulers.io())
                .subscribe(new Subscriber<LoginObj>() {
                    @Override
                    public void onCompleted() {

                    }

                    @Override
                    public void onError(Throwable e) {
                        requestLayoutChange(false);
                        if (e instanceof ConnectException)
                            Toast.makeText(StartActivity.this, R.string.richiesta_non_buon_fine, Toast.LENGTH_LONG).show();
                        else
                            Toast.makeText(StartActivity.this, R.string.email_o_password_sbagliata, Toast.LENGTH_LONG).show();

                    }

                    @Override
                    public void onNext(LoginObj loginObj) {
                        //forse qui ci sarà prima la chiamata per il profilo ma in fase di testing non si considera
                        SettingsUtils.setFirstToken(StartActivity.this, loginObj);
                        SettingsUtils.setProfileEmail(StartActivity.this, editEmail.getText().toString());
                        SettingsUtils.setProfilePassword(StartActivity.this, editPassword.getText().toString());
                        startActivity(new Intent(StartActivity.this, MainActivity.class));
                        finish();
                    }
                });

    }

    private void requestLayoutChange(boolean start) {
        if (start)
            GenericUtils.closeKeyBoard(this);
        progressBarLogin.setVisibility(start ? View.VISIBLE : View.GONE);
        buttonLogin.setVisibility(start ? View.GONE : View.VISIBLE);
        buttonRegister.setVisibility(start ? View.GONE : View.VISIBLE);
    }

    @Override
    protected void onDestroy() {
        if (subscription != null)
            subscription.unsubscribe();
        super.onDestroy();
    }
}
