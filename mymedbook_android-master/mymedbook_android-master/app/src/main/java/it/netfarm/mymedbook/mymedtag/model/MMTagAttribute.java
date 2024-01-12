package it.netfarm.mymedbook.mymedtag.model;

import io.realm.RealmObject;
import io.realm.annotations.PrimaryKey;

public class MMTagAttribute extends RealmObject {
    @PrimaryKey
    private int pk;
    private String name;
    private String datatype;


    public int getPk() {
        return pk;
    }

    public void setPk(int pk) {
        this.pk = pk;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDatatype() {
        return datatype;
    }

    public void setDatatype(String datatype) {
        this.datatype = datatype;
    }
}
