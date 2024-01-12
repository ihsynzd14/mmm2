package it.netfarm.mymedbook.mymedtag.model;

import java.io.Serializable;
import java.util.Date;


public class Document implements Serializable {
    private int pk;
    private String document;
    private Date created;

    public int getPk() {
        return pk;
    }

    public void setPk(int pk) {
        this.pk = pk;
    }

    public String getDocument() {
        return document;
    }

    public void setDocument(String document) {
        this.document = document;
    }

    public Date getCreated() {
        return created;
    }

    public void setCreated(Date created) {
        this.created = created;
    }
}
