package it.netfarm.mymedbook.mymedtag.model;

import io.realm.RealmObject;
import io.realm.annotations.PrimaryKey;


public class MMGroup extends RealmObject {
    @PrimaryKey
    private String name;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
