package it.netfarm.mymedbook.mymedtag;

import android.Manifest;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.location.Location;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.telephony.SmsManager;
import android.text.TextUtils;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.afollestad.materialdialogs.MaterialDialog;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.tasks.OnSuccessListener;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

import butterknife.BindView;
import butterknife.ButterKnife;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.model.AssistenceObj;
import it.netfarm.mymedbook.mymedtag.model.GenericResp;
import it.netfarm.mymedbook.mymedtag.model.HelpRequestBody;
import it.netfarm.mymedbook.mymedtag.model.MMUser;
import it.netfarm.mymedbook.mymedtag.utils.BaseNetworkActivity;
import it.netfarm.mymedbook.mymedtag.utils.RealmUtils;
import rx.Observable;
import rx.Subscriber;
import rx.Subscription;
import rx.android.schedulers.AndroidSchedulers;
import rx.schedulers.Schedulers;

public class AssistanceActivity extends BaseNetworkActivity implements AdapterAssistance.ClickItemInterface, OnSuccessListener<Location> {

    private static final int MY_PERMISSIONS_REQUEST_ACTION_CALL = 231;
    public static final String EXTRA_TAG = "TAG_CODE";
    private static final String SMS_SENT = "SMS_SENT";
    @BindView(R.id.recycle)
    RecyclerView recyclerView;
    @BindView(R.id.progressBar)
    ProgressBar progressBar;
    @BindView(R.id.sending_sms)
    TextView sendingSms;
    private HashMap<String, List<HashMap<String, String>>> fastHelp;
    private String phoneNumber;
    private Subscription subscription;
    private String codeTag;
    private Location position;
    private boolean startCall = false;
    private int numSMSToSend = 0;
    private BroadcastReceiver broadCastForSMS;
    private boolean sentRequestHelp = false;
    private Subscription autorequest;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_assistence);
        codeTag = getIntent().getStringExtra(EXTRA_TAG);

        //MODIFICHE AL LAYOUT
        DisplayMetrics metrics = getResources().getDisplayMetrics();
        int screenWidth = (int) (metrics.widthPixels * 0.80);
        int screenHeight = (int) (metrics.heightPixels * 0.80);
        getWindow().setLayout(screenWidth, screenHeight);
        setFinishOnTouchOutside(false);

        //CHIEDO LA POSIZIONE SE HO DATO IL PERMESSO
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
                && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            FusedLocationProviderClient mFusedLocationClient = LocationServices.getFusedLocationProviderClient(this);
            mFusedLocationClient.getLastLocation().addOnSuccessListener(this);
        }
        //INIZIALIZZO LA VISTA
        ButterKnife.bind(this);
        MMUser user;
        if (TextUtils.isEmpty(codeTag))
            user = RealmUtils.getMyUser(this);
        else
            user = RealmUtils.getOtherUsers(codeTag);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        assert user != null;
        fastHelp = user.getFastHelp();
        if (fastHelp == null || fastHelp.isEmpty()) {
            Toast.makeText(this, R.string.no_fast_help, Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        ArrayList<AssistenceObj> listForAdapter = new ArrayList<>();
        listForAdapter.add(new AssistenceObj()); //tasto annulla
        listForAdapter.add(new AssistenceObj()); //tasto 112
        for (String assistanceKey : fastHelp.keySet()) {  //controllo tutte le coc presenti
            List<HashMap<String, String>> mapForCoc = fastHelp.get(assistanceKey);
            for (HashMap<String, String> map : mapForCoc) {
                String callNumber = map.get("call");
                String callCocNumber = map.get("call_coc");
                if (!TextUtils.isEmpty(callNumber)) {
                    listForAdapter.add(new AssistenceObj(assistanceKey, false, callNumber));
                }
                if (!TextUtils.isEmpty(callCocNumber)) {
                    listForAdapter.add(new AssistenceObj(assistanceKey, true, callCocNumber));
                }

            }
        }
        recyclerView.setAdapter(new AdapterAssistance(listForAdapter, this));
        //

        //INIZIALIZZO IL LISTNER DEI MESSAGGI SE HO DATO IL CONSENSO ALL'INVIO
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS) == PackageManager.PERMISSION_GRANTED) {
            broadCastForSMS = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    numSMSToSend--; //non mi interessa sapere se il messaggio è andato a buon fine ma solo se ha terminato il giro e la linea è libera
                    if (numSMSToSend == 0)
                        sendingSms.post(new Runnable() {
                            @Override
                            public void run() {
                                sendingSms.setText(R.string.sending_request_help_to_server);
                            }
                        });
                    startCall();
                }
            };
            registerReceiver(broadCastForSMS, new IntentFilter(SMS_SENT));
        }
        Toast.makeText(this, R.string.richiesta_di_soccorso_automatica, Toast.LENGTH_LONG).show();
        //TIMER PER AVVIO AUTOMATICO DELL'HELP
        autorequest = Observable.timer(30, TimeUnit.SECONDS)
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new Subscriber<Long>() {
                    @Override
                    public void onCompleted() {
                        ArrayList<Integer> pkCocs = new ArrayList<>();
                        ArrayList<String> smsList = new ArrayList<>();
                        startCall = true; // considero la chiamata come inviata
                        for (String assistanceKey : fastHelp.keySet()) {  //controllo tutte le coc presenti
                            Integer pk = getPkForACoc(assistanceKey, fastHelp);
                            smsList.addAll(getSmsForACoc(assistanceKey, fastHelp));
                            if (pk != null)
                                pkCocs.add(pk);
                        }

                        updateLayout(true);
                        sendRequestHelp(pkCocs); //invio la richiesta di allarme

                        sendSMS(smsList); //invio gli sms
                    }

                    @Override
                    public void onError(Throwable e) {

                    }

                    @Override
                    public void onNext(Long aLong) {

                    }
                });
    }


    @Override
    protected void onDestroy() {
        if (subscription != null)
            subscription.unsubscribe();
        if (autorequest != null)
            autorequest.unsubscribe();
        if (broadCastForSMS != null)
            unregisterReceiver(broadCastForSMS);
        super.onDestroy();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (startCall && sentRequestHelp) { //ho mandato l'intent per la chiamata quindi ho terminato il giro e posso chiudere
            Toast.makeText(this, R.string.help_request_finished, Toast.LENGTH_LONG).show();
            finish();
        }
    }

    @Override
    public void clickCancel() {
        finish();
    }

    @Override
    public void clickCallOneOneTwo() {
        callNumber("112", null);
    }

    @Override
    public void clickItemToCall(AssistenceObj item) {
        callNumber(item.phoneNumber, item);
    }

    private void callNumber(final String phoneNumber, AssistenceObj item) { //HO SELEZIONATO UNA ENTRI DELLA RECYCLE VIEW
        createDialogLoading();
        if (autorequest != null)
            autorequest.unsubscribe();
        if (TextUtils.isEmpty(phoneNumber))
            updateLayout(true);

        //PRENDO TUTTI I NUMERI DEI MESSAGGI E GLI ID DELLE COC
        ArrayList<Integer> pkCocs = new ArrayList<>(); //id da inviare a Chiara
        ArrayList<String> smsList = new ArrayList<>(); //lista di sms da inviare
        if (item == null) { //HO SELEZIONATO 112, INVIO ALLARME A TUTTE LE COC
            for (String assistanceKey : fastHelp.keySet()) {  //controllo tutte le coc presenti
                Integer pk = getPkForACoc(assistanceKey, fastHelp);
                smsList.addAll(getSmsForACoc(assistanceKey, fastHelp));
                if (pk != null)
                    pkCocs.add(pk);
            }
        } else { //INVIO ALLARME ALLA SINGOLA COC
            Integer pk = getPkForACoc(item.nameCoc, fastHelp);
            smsList.addAll(getSmsForACoc(item.nameCoc, fastHelp));
            if (pk != null)
                pkCocs.add(pk);
        }
        sendRequestHelp(pkCocs); //invio la richiesta di allarme
        sendSMS(smsList); //invio gli sms
        waitingForCall(phoneNumber);
    }

    private void waitingForCall(final String phoneNumber) {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED) {
            this.phoneNumber = phoneNumber;
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CALL_PHONE},
                    MY_PERMISSIONS_REQUEST_ACTION_CALL);
            return;
        }
        this.phoneNumber = phoneNumber;
        startCall();
    }

    private void sendRequestHelp(ArrayList<Integer> pkCocs) {
        ArrayList<Double> coordinates = new ArrayList<>();
        if (position != null) {
            coordinates.add(position.getLatitude());
            coordinates.add(position.getLongitude());
        }
        if (subscription != null)
            subscription.unsubscribe();
        subscription = ApiManager.getInstance().getRetrofitInstance().sendRequestHelp(
                new HelpRequestBody(codeTag,
                        coordinates, pkCocs))
                .retry() //QUESTO MI ASSICURA CHE TENTA DI INVIARE LA RICHIESTA SINO A QUANDO NON SI CHIUDE L'ACTIVITY
                .timeout(5, TimeUnit.SECONDS)
                .observeOn(AndroidSchedulers.mainThread())
                .subscribeOn(Schedulers.io())
                .subscribe(new Subscriber<GenericResp>() {
                    @Override
                    public void onCompleted() {

                    }

                    @Override
                    public void onError(Throwable e) {
                        Log.e(AssistanceActivity.class.getName(), "error on sent");
                        sentRequestHelp = true;
                    }

                    @Override
                    public void onNext(GenericResp requestBody) {
                        Log.i(AssistanceActivity.class.getName(), "sent request");
                        finishSentRequest();
                    }
                });
    }

    private void finishSentRequest() {
        sentRequestHelp = true;
        if (startCall && !isFinishing()) { //HO GIA' AVVIATO LA CHIAMATA MA NON SONO PASSATO DA ONRESUME
            finish();
        }
    }

    private void updateLayout(boolean startRequestHelp) {
        recyclerView.setVisibility(startRequestHelp ? View.INVISIBLE : View.VISIBLE);
        progressBar.setVisibility(startRequestHelp ? View.VISIBLE : View.INVISIBLE);
        sendingSms.setVisibility(startRequestHelp ? View.VISIBLE : View.GONE);
    }

    private void sendSMS(ArrayList<String> smsList) {
        if (smsList.size() > 0 &&
                ActivityCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS) == PackageManager.PERMISSION_GRANTED) {
            numSMSToSend = smsList.size();
            if (numSMSToSend > 0)
                Toast.makeText(this, R.string.invio_sms_in_corso, Toast.LENGTH_LONG).show();
            PendingIntent sentPendingIntent = PendingIntent.getBroadcast(this, 0, new Intent(SMS_SENT), 0);
            SmsManager sms = SmsManager.getDefault();
            for (String number : smsList) {
                try {
                    MMUser user = TextUtils.isEmpty(codeTag) ? RealmUtils.getMyUser(this) : RealmUtils.getOtherUsers(codeTag);
                    assert user != null;
                    if (position != null)
                        sms.sendTextMessage("+39" + number, null,
                                String.format(Locale.US, getString(R.string.invio_richiesta_di_assistenza), user.getFirst_name(), user.getLast_name(),
                                        position.getLatitude(), position.getLongitude()),
                                sentPendingIntent, null);
                    else
                        sms.sendTextMessage(number, null,
                                String.format(Locale.US, getString(R.string.invio_richiesta_di_assistenza_no_coor), user.getFirst_name(), user.getLast_name()),
                                sentPendingIntent, null);
                } catch (Exception ignore) {
                    numSMSToSend--;
                }
            }
        } else {
            cancelDialog();
            numSMSToSend = 0;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    sendingSms.setText(R.string.sending_request_help_to_server);
                }
            });
        }

    }

    private void startCall() {
        if (numSMSToSend > 0) //devo aver avuto la risposta per ogni sms prima di startare la chiamata
            return;
        if (!TextUtils.isEmpty(this.phoneNumber)) {
            Intent callIntent = new Intent(Intent.ACTION_CALL);
            callIntent.setData(Uri.parse("tel:" + this.phoneNumber));
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED) {
                return;
            }
            startCall = true;
            startActivity(callIntent);
        } else
            startCall = true;
    }

    private
    @Nullable
    Integer getPkForACoc(String assistanceKey, HashMap<String, List<HashMap<String, String>>> fastHelp) {
        List<HashMap<String, String>> list = fastHelp.get(assistanceKey);
        for (HashMap<String, String> map : list) {
            String pk = map.get("pk");
            if (pk != null)
                return Integer.valueOf(pk);
        }
        return null;
    }

    @Override
    protected void createDialogLoading() {
        cancelDialog();
        dialog = new MaterialDialog.Builder(this).content(R.string.waiting_for_sms_sending)
                .progress(true, -1)
                .show();
    }

    private ArrayList<String> getSmsForACoc(String assistanceKey, HashMap<String, List<HashMap<String, String>>> fastHelp) {
        ArrayList<String> listToFill = new ArrayList<>();
        List<HashMap<String, String>> list = fastHelp.get(assistanceKey);
        for (HashMap<String, String> map : list) {
            String smsValue = map.get("sms");
            if (!TextUtils.isEmpty(smsValue))
                listToFill.add(smsValue);
        }
        return listToFill;
    }


    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST_ACTION_CALL:
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    startCall();
                    break;
                }
                phoneNumber = null;
                break;
        }
    }


    @Override
    public void onSuccess(Location location) {
        if (location != null)
            position = location;

    }

    public static void startInstance(Context context, @Nullable String tagUser) {
        Intent intent = new Intent(context, AssistanceActivity.class);
        intent.putExtra(AssistanceActivity.EXTRA_TAG, tagUser);
        context.startActivity(intent);
    }
}
