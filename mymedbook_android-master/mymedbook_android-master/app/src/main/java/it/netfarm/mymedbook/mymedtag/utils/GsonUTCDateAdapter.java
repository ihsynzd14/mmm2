package it.netfarm.mymedbook.mymedtag.utils;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;
import com.google.gson.JsonPrimitive;
import com.google.gson.JsonSerializationContext;
import com.google.gson.JsonSerializer;

import java.lang.reflect.Type;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

/**
 * Created by alevittoria on 28/04/2017.
 */

public class GsonUTCDateAdapter implements JsonSerializer<Date>, JsonDeserializer<Date> {

    private final DateFormat dateFormat;
    public static final String dateFormatServer = "yyyy-MM-dd'T'HH:mm:ss'Z'";
    public static final String dateFormatTherapy = "yyyy-MM-dd'T'HH:mm:ss";
    public static final String dateFormatShort = "yyyy-MM-dd";

    private static final String[] DATE_FORMATS = new String[]{
            dateFormatTherapy,
            dateFormatServer,
            dateFormatShort
    };

    public GsonUTCDateAdapter() {
        dateFormat = new SimpleDateFormat(dateFormatServer, Locale.US);      //This is the format I need
        dateFormat.setTimeZone(TimeZone.getTimeZone("UTC"));                               //This is the key line which converts the date to UTC which cannot be accessed with the default serializer
    }

    @Override
    public synchronized JsonElement serialize(Date date, Type type, JsonSerializationContext jsonSerializationContext) {
        return new JsonPrimitive(dateFormat.format(date));
    }

    @Override
    public synchronized Date deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) {
        for (String format : DATE_FORMATS) {
            try {
                SimpleDateFormat simple = new SimpleDateFormat(format, Locale.US);
                simple.setTimeZone(TimeZone.getTimeZone("UTC"));
                return simple.parse(jsonElement.getAsString());
            } catch (ParseException e) {
            }
        }
        return null;
    }

}