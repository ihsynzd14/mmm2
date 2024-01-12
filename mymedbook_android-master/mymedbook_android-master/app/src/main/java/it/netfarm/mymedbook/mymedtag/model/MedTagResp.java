package it.netfarm.mymedbook.mymedtag.model;


import android.util.Log;
import android.util.Pair;

import com.google.gson.annotations.SerializedName;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import io.realm.RealmList;

public class MedTagResp {
    private String Error;
    private MMUser user;
    private MMTagObject lifesaver;
    @SerializedName("fast_help")
    private HashMap<String, List<HashMap<String, String>>> fastHelp;
    private RealmList<TherapyObj> therapies;
    private RealmList<MMTagObject> attributes_groups;


    public MMTagObject getLifesaver() {
        return lifesaver;
    }

    public void setLifesaver(MMTagObject lifesaver) {
        this.lifesaver = lifesaver;
    }


    public MMUser getUser() {
        user.setLifesaverInternal(lifesaver);
        user.setAttributes_groupsInternal(attributes_groups);
        user.setTherapies(therapies);
        try {
            user.setfastHelpSerialized(fastHelp);
        } catch (Exception e) {
            Log.e(MedTagResp.class.getName(), "errore nella serializzazione");
        }
        return user;
    }

    public void setUser(MMUser user) {
        this.user = user;
    }

    public String getError() {
        return Error;
    }

    public void setError(String error) {
        Error = error;
    }

    public void setAttributes_groups(RealmList<MMTagObject> attributes_groups) {
        this.attributes_groups = attributes_groups;
    }
}
