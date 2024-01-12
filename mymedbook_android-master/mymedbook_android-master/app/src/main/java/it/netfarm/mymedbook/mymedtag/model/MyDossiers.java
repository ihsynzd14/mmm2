package it.netfarm.mymedbook.mymedtag.model;

import java.io.Serializable;
import java.util.List;


public class MyDossiers implements Serializable {
    private int pk;
    private String name;
    private List<Document> document_set;

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

    public List<Document> getDocument_set() {
        return document_set;
    }

    public void setDocument_set(List<Document> document_set) {
        this.document_set = document_set;
    }
}
