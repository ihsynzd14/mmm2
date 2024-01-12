package it.netfarm.mymedbook.mymedtag.model;


import android.util.Pair;


import com.google.gson.reflect.TypeToken;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.List;

import io.realm.RealmList;
import io.realm.RealmObject;
import io.realm.annotations.Ignore;
import io.realm.annotations.PrimaryKey;
import it.netfarm.mymedbook.mymedtag.api.ApiManager;
import it.netfarm.mymedbook.mymedtag.utils.GenericUtils;

public class MMUser extends RealmObject {
    @PrimaryKey
    private int pk;
    private String first_name;
    private String last_name;
    private String avatar;
    private Date birthday;
    private String mymedtag_code;
    private MMTagObject lifesaverInternal; //li conservo all'interno dell'utente per comodità
    private RealmList<MMTagObject> attributes_groupsInternal; //li conservo all'interno dell'utente per comodità
    private RealmList<TherapyObj> therapies;
    private RealmList<MMGroup> groups;
    private String fastHelpSerialized;
    @Ignore
    private HashMap<String, List<HashMap<String, String>>> fastHelp;
    //        "created": "2017-01-25T15:54:40.759840",
    //       "modified": "2017-01-25T15:54:40.759855"

    public String getAvatarUrl() {
        if (avatar == null)
            return "";
        if (avatar.startsWith("http"))
            return avatar;
        return GenericUtils.getUrlImage(avatar);
    }

    public int getPk() {
        return pk;
    }

    public void setPk(int pk) {
        this.pk = pk;
    }

    public String getFirst_name() {
        return first_name;
    }

    public void setFirst_name(String first_name) {
        this.first_name = first_name;
    }

    public String getLast_name() {
        return last_name;
    }

    public void setLast_name(String last_name) {
        this.last_name = last_name;
    }

    public String getAvatar() {
        return avatar;
    }

    public void setAvatar(String avatar) {
        this.avatar = avatar;
    }

    public MMTagObject getLifesaverInternal() {
        return lifesaverInternal;
    }

    public void setLifesaverInternal(MMTagObject lifesaverInternal) {
        this.lifesaverInternal = lifesaverInternal;
    }


    public void setAttributes_groupsInternal(RealmList<MMTagObject> attributes_groupsInternal) {
        this.attributes_groupsInternal = attributes_groupsInternal;
    }

    public String getMymedtag_code() {
        return mymedtag_code;
    }

    public void setMymedtag_code(String mymedtag_code) {
        this.mymedtag_code = mymedtag_code;
    }

    public Date getBirthday() {
        return birthday;
    }

    public void setBirthday(Date birthday) {
        this.birthday = birthday;
    }

    public List<MMTagObject> getCompleteList() {  //devo compattare i field con stesso id_attribute
        List<MMTagObject> list = new ArrayList<>();
        if (getAttributes_groupsInternal() == null || getAttributes_groupsInternal().size() == 0)
            return list;

        Collections.sort(getAttributes_groupsInternal(), new Comparator<MMTagObject>() {
            @Override
            public int compare(MMTagObject mmTagObject, MMTagObject mmTagObject2) {
                return mmTagObject.getAttribute().getPk() - mmTagObject2.getAttribute().getPk();
            }
        });
        int id_attribute = -1;
        for (MMTagObject obj : getAttributes_groupsInternal()) {
            if (obj.getAttribute().getPk() != id_attribute) {
                list.add(obj.copy());
                id_attribute = obj.getAttribute().getPk();
            } else {
                MMTagObject prev = list.get(list.size() - 1);
                prev.setValue(String.format("%s\n%s", prev.getValue(), obj.getValue()));
            }
        }
        return list;
    }

    public RealmList<MMTagObject> getAttributes_groupsInternal() {
        return attributes_groupsInternal;
    }

    public RealmList<MMGroup> getGroups() {
        return groups;
    }

    public void setGroups(RealmList<MMGroup> groups) {
        this.groups = groups;
    }

    public RealmList<TherapyObj> getTherapies() {
        return therapies;
    }

    public void setTherapies(RealmList<TherapyObj> therapies) {
        this.therapies = therapies;
    }

    public void setfastHelpSerialized(HashMap<String, List<HashMap<String, String>>> fastHelp) {
        if (fastHelp == null || fastHelp.isEmpty()) {
            this.fastHelpSerialized = null;
            this.fastHelp = null;
            return;
        }
        this.fastHelpSerialized = ApiManager.gson.toJson(fastHelp);
        this.fastHelp = fastHelp;

    }

    public HashMap<String, List<HashMap<String, String>>> getFastHelp() {
        if (getFastHelpSerialized() == null)
            return null;
        else if (this.fastHelp != null)
            return fastHelp;
        try {
            this.fastHelp = ApiManager.gson.fromJson(getFastHelpSerialized(), new TypeToken<HashMap<String, List<HashMap<String, String>>>>() {
            }.getType());
            return fastHelp;
        } catch (Exception ignore) {
            return null;
        }
    }

    public String getFastHelpSerialized() {
        return fastHelpSerialized;
    }
}
