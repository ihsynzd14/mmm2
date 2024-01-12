package it.netfarm.mymedbook.mymedtag.model;




public class AssistenceObj {

    public String phoneNumber;
    public boolean isCocNumber;  //il numero può essere relativo ad una coc o ad un numero
    public String nameCoc;

    public AssistenceObj() {

    }

    public AssistenceObj(String nameCoc, boolean isCocNumber, String phoneNumber) {
        this.nameCoc = nameCoc;
        this.isCocNumber = isCocNumber;
        this.phoneNumber = phoneNumber;

    }
}
