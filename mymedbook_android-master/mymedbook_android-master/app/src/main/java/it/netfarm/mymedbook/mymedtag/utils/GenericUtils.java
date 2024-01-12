package it.netfarm.mymedbook.mymedtag.utils;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.net.Uri;
import android.support.annotation.NonNull;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodManager;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.text.DateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

import it.netfarm.mymedbook.mymedtag.Constants;


public class GenericUtils {
    private static final int MAX_SIZE = 1024;
    private static final java.lang.String HTTP = "http";
    private static final String TAG = GenericUtils.class.getSimpleName();

    private static DateFormat dateLocaLong = DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT, Locale.getDefault());
    private static final TimeZone UTC = TimeZone.getTimeZone("UTC");

    public static void closeKeyBoard(Activity activity) {
        View view = activity.getCurrentFocus();
        if (view != null) {
            InputMethodManager imm = (InputMethodManager) activity.getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(view.getWindowToken(), 0);
        }
    }

    public static String fromDateToStringLocal(Date time) {
        if (time == null)
            return null;
        dateLocaLong.setTimeZone(UTC);
        return dateLocaLong.format(time);
    }


    public static String getUrlImage(String path) {
        if (TextUtils.isEmpty(path))
            return null;
        if (path.startsWith(GenericUtils.HTTP))
            return path;
        return Constants.BASE_URL_IMAGE + path;
    }

    public static void openLink(Context context, CharSequence text) {
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(Constants.BASE_URL_IMAGE + text));
        context.startActivity(browserIntent);
    }

    public static File saveBitmapToFile(@NonNull File file) {
        try {
            // BitmapFactory options to downsize the image
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inJustDecodeBounds = true;
            // factor of downsizing the image

            FileInputStream inputStream = new FileInputStream(file);
            BitmapFactory.decodeStream(inputStream, null, options);
            inputStream.close();

            options.inJustDecodeBounds = false;
            options.inSampleSize = calculateInSampleSize(options, MAX_SIZE, MAX_SIZE);
            inputStream = new FileInputStream(file);

            Bitmap selectedBitmap = BitmapFactory.decodeStream(inputStream, null, options);
            selectedBitmap = detectOrientationAndRotate(selectedBitmap, file.getAbsolutePath());
            inputStream.close();

            // here i override the original image file
            file.createNewFile();
            FileOutputStream outputStream = new FileOutputStream(file);

            Log.i(TAG, "Bitmap resized to " + selectedBitmap.getWidth() + "x" + selectedBitmap.getHeight());
            selectedBitmap.compress(Bitmap.CompressFormat.JPEG, 95, outputStream);

            return file;
        } catch (Exception e) {
            e.printStackTrace();
            return file;
        }
    }


    private static int calculateInSampleSize(BitmapFactory.Options options, int reqWidth, int reqHeight) {
        // Raw height and width of image
        final int height = options.outHeight;
        final int width = options.outWidth;
        int inSampleSize = 1;

        if (height > reqHeight || width > reqWidth) {

            final int halfHeight = height / 2;
            final int halfWidth = width / 2;

            // Calculate the largest inSampleSize value that is a power of 2 and keeps both
            // height and width larger than the requested height and width.
            while ((halfHeight / inSampleSize) >= reqHeight
                    && (halfWidth / inSampleSize) >= reqWidth) {
                inSampleSize *= 2;
            }
        }

        return inSampleSize;
    }

    private static Bitmap detectOrientationAndRotate(Bitmap bitmap, String absolutePath) {
        final ExifInterface ei;
        try {
            ei = new ExifInterface(absolutePath);
            final int orientation = ei.getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_UNDEFINED);

            switch (orientation) {
                case ExifInterface.ORIENTATION_ROTATE_90:
                    return rotateImage(bitmap, 90);
                case ExifInterface.ORIENTATION_ROTATE_180:
                    return rotateImage(bitmap, 180);
                case ExifInterface.ORIENTATION_ROTATE_270:
                    return rotateImage(bitmap, 270);
                default:
                    return rotateImage(bitmap, 0);
            }
        } catch (Exception e) {
            e.printStackTrace();
            return bitmap;
        }
    }


    public static Bitmap rotateImage(Bitmap source, float angle) {
        Bitmap retVal;

        Matrix matrix = new Matrix();
        matrix.postRotate(angle);
        retVal = Bitmap.createBitmap(source, 0, 0, source.getWidth(), source.getHeight(), matrix, true);

        return retVal;
    }
}

