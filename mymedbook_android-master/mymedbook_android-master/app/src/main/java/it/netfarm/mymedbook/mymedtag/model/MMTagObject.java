package it.netfarm.mymedbook.mymedtag.model;


import io.realm.RealmObject;
import io.realm.annotations.PrimaryKey;

public class MMTagObject extends RealmObject {
    @PrimaryKey
    private int pk;
    private String other;
    private MMTagAttribute attribute;

    private String value;

    public MMTagObject() {
    }

    public MMTagObject(MMTagObject mmTagObject) {
        this.pk = mmTagObject.getPk();
        this.attribute = mmTagObject.getAttribute();
        this.value = mmTagObject.getValue();
        this.other = mmTagObject.getOther();

    }

    public int getPk() {
        return pk;
    }

    public void setPk(int pk) {
        this.pk = pk;
    }


    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }


    public MMTagObject copy() {
        return new MMTagObject(this);
    }

    public MMTagAttribute getAttribute() {
        return attribute;
    }

    public void setAttribute(MMTagAttribute attribute) {
        this.attribute = attribute;
    }

    public String getOther() {
        return other;
    }

    public void setOther(String other) {
        this.other = other;
    }
}
