package it.netfarm.mymedbook.mymedtag.utils;

import android.support.annotation.StringRes;
import android.widget.EditText;

import it.netfarm.mymedbook.mymedtag.R;

public class StringUtils {

    public static boolean EditIsEmpty(String text, EditText editText, int minCount) {
        return EditIsEmpty(text, editText, minCount, R.string.campo_troppo_corto);
    }

    public static boolean EditIsEmpty(EditText editText, int minCount) {
        return EditIsEmpty(editText.getText().toString(), editText, minCount, R.string.campo_troppo_corto);
    }

    public static boolean EditIsEmpty(String text, final EditText editText, int minCount,
                                      @StringRes final int stringIdShort) {
        if (text == null || editText.length() == 0) {
            editText.post(new Runnable() {
                @Override
                public void run() {
                    editText.setError(editText.getContext().getString(R.string.campo_non_vuoto));
                    editText.requestFocus();

                }
            });
            return true;
        } else if (editText.length() < minCount) {
            editText.post(new Runnable() {
                @Override
                public void run() {
                    editText.setError(editText.getContext().getString(stringIdShort));
                    editText.requestFocus();

                }
            });
            return true;
        } else
            return false;
    }

    public static boolean notPasswordEquals(EditText passwordEdit, EditText passworRepeatEdit) {
        boolean notEquals = !passwordEdit.getText().toString().equals(passworRepeatEdit.getText().toString());
        if (notEquals) {
            passwordEdit.setError(passwordEdit.getContext().getString(R.string.password_non_uguali));
            passwordEdit.requestFocus();

        }
        return notEquals;
    }

    public static boolean CheckInvalidEmail(EditText emailEdit) {
        boolean isEmpty = EditIsEmpty(emailEdit, 0);
        if(isEmpty)
        return true;
        isEmpty = !android.util.Patterns.EMAIL_ADDRESS.matcher(emailEdit.getText()).matches();
        if(!isEmpty)
            return false;
        emailEdit.setError(emailEdit.getContext().getString(R.string.invalid_email));
        emailEdit.requestFocus();
        return true;

    }
}
