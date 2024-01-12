package it.netfarm.mymedbook.mymedtag;

import android.content.Context;
import android.graphics.Typeface;
import android.support.v4.content.ContextCompat;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import it.netfarm.mymedbook.mymedtag.model.MMTagObject;
import it.netfarm.mymedbook.mymedtag.model.TherapyObj;
import it.netfarm.mymedbook.mymedtag.utils.GenericUtils;


public class AdapterItems extends RecyclerView.Adapter<AdapterItems.ViewHolder> {
    private static final int TYPE_HEADER = 0;
    private static final int TYPE_ITEM = 1;
    private final List<Object> list;
    private boolean header = false;

    public AdapterItems(List<Object> list) {
        this.list = list;
    }

    public AdapterItems(List<Object> list, boolean header) {
        this.list = list;
        this.header = header;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        if (viewType == TYPE_ITEM) {
            View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_adapter, parent, false);
            return new ViewHolderItem(v);
        }
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.header_adapter, parent, false);
        return new ViewHolderHeader(v);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        Object item = list.get(position);
        if (item instanceof MMTagObject)
            holder.bind((MMTagObject) item, position);
        else if (item instanceof TherapyObj)
            holder.bind((TherapyObj) item, position);


    }

    @Override
    public int getItemViewType(int position) {
        if (position == 0 && header)
            return TYPE_HEADER;
        else return TYPE_ITEM;
    }

    @Override
    public int getItemCount() {
        if (list != null)
            return list.size();
        return 0;
    }

    public void hasHeader(boolean header) {
        this.header = header;
    }

    public abstract class ViewHolder extends RecyclerView.ViewHolder {


        public ViewHolder(View itemView) {
            super(itemView);


        }

        public abstract void bind(MMTagObject s, int position);

        public abstract void bind(TherapyObj s, int position);
    }

    private class ViewHolderItem extends ViewHolder {
        private final View linForBack;
        private TextView textKey;
        private TextView textValue;

        public ViewHolderItem(View v) {
            super(v);
            textKey = itemView.findViewById(R.id.text_key);
            textValue = itemView.findViewById(R.id.text_value);
            linForBack = itemView.findViewById(R.id.lin);
        }

        @Override
        public void bind(MMTagObject s, int position) {
            boolean switchColor = position % 2 == 0;
            Context context = itemView.getContext();
            linForBack.setBackgroundColor(ContextCompat.getColor(context,
                    switchColor ? R.color.table_second : R.color.table_first));
            //int colorText  =ContextCompat.getColor(context,R.color.black)
            //textKey.setTextColor(ContextCompat.getColor(context,));
            if (s.getAttribute() != null) {
                String name = s.getAttribute().getName();
                if (!TextUtils.isEmpty(name)) {
                    if (name.startsWith("---")) {
                        name = s.getOther();
                    }
                }
                textKey.setText(name);

                textValue.setTypeface(null, Typeface.NORMAL);
                textValue.setOnClickListener(null);
                textValue.setTextColor(ContextCompat.getColor(textValue.getContext(), R.color.black));


                String datatype = s.getAttribute().getDatatype();

                if ("boolean".equals(datatype))
                    textValue.setText("TRUE".equals(s.getValue().toUpperCase()) ? R.string.si : R.string.no);
                else if ("year_with_text".equals(datatype) || "year_with_checkbox".equals(datatype)) {
                    textValue.setText(String.format("%s %s", textValue.getContext().getString(R.string.since), s.getValue()));
                } else
                    textValue.setText(s.getValue());

            } else {
                textValue.setText("");
                textKey.setText("");
            }

        }

        @Override
        public void bind(final TherapyObj s, int position) {
            textKey.setText(R.string.terapia);
            String key = GenericUtils.fromDateToStringLocal(s.getModified());
            if (list.size() > position + 1) {
                if (list.get(position + 1) instanceof TherapyObj) {
                    if (TextUtils.isEmpty(key))
                        textKey.setText(R.string.terapie);
                    else
                        textKey.setText(String.format("%s\n(%s)", textKey.getContext().getString(R.string.terapie), key));
                }
            }
            if (position > 0 && list.get(position - 1) instanceof TherapyObj) {
                textKey.setText(key);
            }

            textValue.setOnClickListener(null);
            if (!TextUtils.isEmpty(s.getFile())) {
                textValue.setText(R.string.apri);
                textValue.setTypeface(null, Typeface.BOLD);
                textValue.setTextColor(ContextCompat.getColor(textValue.getContext(), R.color.accent_link));
                textValue.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        if (!TextUtils.isEmpty(s.getFile()))
                            GenericUtils.openLink(textValue.getContext(), s.getFile());

                    }
                });
            } else {
                textValue.setText(s.getInfo());
                textValue.setTypeface(null, Typeface.NORMAL);
                textValue.setOnClickListener(null);
            }
        }
    }

    private class ViewHolderHeader extends ViewHolder {
        private TextView textHeader;

        public ViewHolderHeader(View v) {
            super(v);
            textHeader = (TextView) v.findViewById(R.id.text);
        }

        @Override
        public void bind(MMTagObject mmTagObject, int position) {
            //    textHeader.setOnClickListener(null);
            textHeader.setText(String.format("%s: %s", mmTagObject.getAttribute().getName(), mmTagObject.getValue()));
        }

        @Override
        public void bind(TherapyObj s, int position) {
            textHeader.setText(String.format("%s; %s", textHeader.getContext().getString(R.string.terapia), s.getInfo()));
            textHeader.setOnClickListener(null);
            textHeader.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {

                }
            });

        }
    }
}
