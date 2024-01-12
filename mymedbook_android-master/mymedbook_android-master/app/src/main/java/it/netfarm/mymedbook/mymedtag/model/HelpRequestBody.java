package it.netfarm.mymedbook.mymedtag.model;


import java.util.ArrayList;
import java.util.List;

public class HelpRequestBody {
    private String code;
    private PositionObj latlng;
    private ArrayList<Integer> COC;

    public HelpRequestBody() {

    }

    public HelpRequestBody(String tag, List<Double> coordinates, ArrayList<Integer> coc) {
        this.code = tag;
        if (coordinates != null && coordinates.size() > 1)
            this.latlng = new PositionObj(coordinates);
        this.COC = coc;

    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public ArrayList<Integer> getCOC() {
        return COC;
    }

    public void setCOC(ArrayList<Integer> COC) {
        this.COC = COC;
    }

    public PositionObj getLatlng() {
        return latlng;
    }

    public void setLatlng(PositionObj latlng) {
        this.latlng = latlng;
    }

    private class PositionObj {
        private String type = "Point";
        private List<Double> coordinates;

        public PositionObj() {

        }

        public PositionObj(List<Double> coordinates) {
            this.coordinates = coordinates;
        }

        public List<Double> getCoordinates() {
            return coordinates;
        }

        public void setCoordinates(List<Double> coordinates) {
            this.coordinates = coordinates;
        }

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }
    }
}
