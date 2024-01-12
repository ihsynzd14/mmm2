package it.netfarm.mymedbook.mymedtag;

import android.content.Intent;
import android.nfc.NdefMessage;
import android.nfc.NdefRecord;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.nfc.tech.Ndef;
import android.os.AsyncTask;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLDecoder;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

import butterknife.BindView;
import butterknife.ButterKnife;
import io.realm.Realm;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.model.MMUser;
import it.netfarm.mymedbook.mymedtag.model.MedTagResp;
import it.netfarm.mymedbook.mymedtag.start.StartActivity;
import it.netfarm.mymedbook.mymedtag.utils.RealmUtils;
import it.netfarm.mymedbook.mymedtag.utils.SettingsUtils;
import retrofit2.adapter.rxjava.HttpException;
import rx.Subscriber;
import rx.Subscription;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

public class NfcActivity extends AppCompatActivity {
    private static final String CODE = "code";
    private Subscription subscription;
    @BindView(R.id.progressBar)
    ProgressBar progressBar;
    @BindView(R.id.text_error)
    TextView textError;
    private NfcAdapter mNfcAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_nfc);
        ButterKnife.bind(this);
        mNfcAdapter = NfcAdapter.getDefaultAdapter(this);
        if (mNfcAdapter == null) {
            // Stop here, we definitely need NFC
            Toast.makeText(this, "This device doesn't support NFC.", Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        handleIntent(getIntent());
    }

    private void startRequest(String url) {
        if (!url.startsWith("http://"))
            url = "http://" + url;
        try {
            Map<String, String> map = splitQuery(new URL(url));

            if (map == null || map.get("code") == null) {
                textError.setText(R.string.codice_tag_non_trovato);
                progressBar.setVisibility(View.GONE);
                return;
            }
            final String code = map.get("code");

            askUser(code);

        } catch (UnsupportedEncodingException | MalformedURLException e) {
            e.printStackTrace();
        }
    }

    private void askUser(final String code) {
        if (subscription != null && !subscription.isUnsubscribed())
            subscription.unsubscribe();
        progressBar.setVisibility(View.VISIBLE);
        subscription = ApiManager.getInstance().getRetrofitInstance().askUserMedTag(code).subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new Subscriber<MedTagResp>() {
                    @Override
                    public void onCompleted() {

                    }

                    @Override
                    public void onError(Throwable e) {
                        if (e instanceof HttpException) {
                            int code = HttpException.class.cast(e).code();
                            if (code == 403) {
                                String token = SettingsUtils.getToken(NfcActivity.this);
                                if (token == null) {
                                    Toast.makeText(NfcActivity.this, R.string.per_vedere_questo_profilo_devi_essere_autenticato, Toast.LENGTH_LONG).show();
                                    startActivity(new Intent(NfcActivity.this, StartActivity.class));
                                    finish();
                                } else {
                                    Toast.makeText(NfcActivity.this, R.string.non_sei_autorizzato, Toast.LENGTH_LONG).show();
                                    finish();
                                }
                                return;
                            }
                            if (code == 404) {
                                //Toast.makeText(NfcActivity.this, R.string.profilo_inesistente, Toast.LENGTH_LONG).show();
                                textError.setText(R.string.profilo_inesistente);
                                progressBar.setVisibility(View.GONE);
                                return;
                            }
                        }
                        textError.setText(R.string.richiesta_non_buon_fine_passare_nuovamente_nfc);
                        progressBar.setVisibility(View.GONE);
                        if (RealmUtils.getOtherUsers(code) != null) {
                            Toast.makeText(NfcActivity.this, R.string.caricamento_profilo_dalla_memoria, Toast.LENGTH_LONG).show();
                            Intent intent = new Intent(NfcActivity.this, MainActivity.class);
                            intent.putExtra(MainActivity.EXTRA_USER_TAG, code);
                            startActivity(intent);
                            finish();
                        }


                    }

                    @Override
                    public void onNext(MedTagResp medTagResp) {
                        textError.setText(null);
                        MMUser user = medTagResp.getUser();
                        user.setMymedtag_code(code);
                        Realm realm = Realm.getDefaultInstance();
                        realm.beginTransaction();
                        realm.insertOrUpdate(user);
                        realm.commitTransaction();
                        realm.close();
                        Intent intent = new Intent(NfcActivity.this, MainActivity.class);
                        intent.putExtra(MainActivity.EXTRA_USER_TAG, user.getMymedtag_code());
                        startActivity(intent);
                        finish();
                    }
                });
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        handleIntent(intent);
    }

    @Override
    protected void onDestroy() {
        if (subscription != null)
            subscription.unsubscribe();
        super.onDestroy();
    }

    @Override
    protected void onPause() {
        if (!isFinishing())
            finish();
        super.onPause();
    }

    private void handleIntent(Intent intent) {
        if(BuildConfig.DEBUG) {
            Log.i("INTENT TAG", "" + getIntent());
            Log.i("INTENT ACTION", "" + getIntent().getAction());
            Log.i("INTENT CODE", "" + getIntent().getStringExtra(CODE));
        }
        String action = intent.getAction();
        if (NfcAdapter.ACTION_NDEF_DISCOVERED.equals(action)) {

            String type = intent.getType();

            Tag tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG);

            new NdefReaderTask().execute(tag);


        } else if (NfcAdapter.ACTION_TECH_DISCOVERED.equals(action)) {

            // In case we would still use the Tech Discovered Intent
            Tag tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG);
            String[] techList = tag.getTechList();
            String searchedTech = Ndef.class.getName();

            for (String tech : techList) {
                if (searchedTech.equals(tech)) {
                    new NdefReaderTask().execute(tag);
                    break;
                }
            }
        } else if (Intent.ACTION_VIEW.equals(action)) {
            if (getIntent().getStringExtra(CODE) != null) {
                askUser(getIntent().getStringExtra(CODE));
            } else {
                String url = intent.getData().toString();
                startRequest(url);
            }
        }
    }


    public class NdefReaderTask extends AsyncTask<Tag, Void, String> {

        private static final String TAG = "TAG ERROR";

        @Override
        protected String doInBackground(Tag... params) {
            Tag tag = params[0];

            Ndef ndef = Ndef.get(tag);
            if (ndef == null) {
                // NDEF is not supported by this Tag.
                return null;
            }

            NdefMessage ndefMessage = ndef.getCachedNdefMessage();

            NdefRecord[] records = ndefMessage.getRecords();
            for (NdefRecord ndefRecord : records) {
                if (ndefRecord.getTnf() == NdefRecord.TNF_WELL_KNOWN && Arrays.equals(ndefRecord.getType(), NdefRecord.RTD_URI)) {
                    try {
                        return readText(ndefRecord);
                    } catch (UnsupportedEncodingException e) {
                        Log.e(TAG, "Unsupported Encoding", e);
                    }
                }
            }

            return null;
        }

        private String readText(NdefRecord record) throws UnsupportedEncodingException {
        /*
         * See NFC forum specification for "Text Record Type Definition" at 3.2.1
         *
         * http://www.nfc-forum.org/specs/
         *
         * bit_7 defines encoding
         * bit_6 reserved for future use, must be 0
         * bit_5..0 length of IANA language code
         */

            byte[] payload = record.getPayload();

            // Get the Text Encoding
            String textEncoding = ((payload[0] & 128) == 0) ? "UTF-8" : "UTF-16";

            // Get the Language Code
            int languageCodeLength = payload[0] & 0063;

            // String languageCode = new String(payload, 1, languageCodeLength, "US-ASCII");
            // e.g. "en"

            // Get the Text
            return new String(payload, languageCodeLength, payload.length - languageCodeLength, textEncoding);
        }

        @Override
        protected void onPostExecute(String result) {
            if (result != null) {
                startRequest(result);
            }
        }
    }

    public static
    @Nullable
    Map<String, String> splitQuery(URL url) throws UnsupportedEncodingException {
        if (url == null || url.getQuery() == null)
            return null;
        Map<String, String> query_pairs = new LinkedHashMap<>();
        String query = url.getQuery();
        String[] pairs = query.split("&");
        for (String pair : pairs) {
            int idx = pair.indexOf("=");
            query_pairs.put(URLDecoder.decode(pair.substring(0, idx), "UTF-8"), URLDecoder.decode(pair.substring(idx + 1), "UTF-8"));
        }
        return query_pairs;
    }
}
