package it.netfarm.mymedbook.mymedtag;

import android.support.annotation.Nullable;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.lb.auto_fit_textview.AutoResizeTextView;

import java.util.ArrayList;

import butterknife.BindView;
import butterknife.ButterKnife;
import it.netfarm.mymedbook.mymedtag.model.AssistenceObj;

class AdapterAssistance extends RecyclerView.Adapter<AdapterAssistance.ViewHolder> {
    private static final int CANCEL_TYPE = 0;
    private static final int CENTODODICI_TYPE = 1;
    private static final int COC_TYPE = 2;
    private static final int CALL_TYPE = 3;
    private final ArrayList<AssistenceObj> list;
    private final ClickItemInterface clickItemInterface;

    public AdapterAssistance(ArrayList<AssistenceObj> listForAdapter, ClickItemInterface clickItemInterface) {
        this.list = listForAdapter;
        this.clickItemInterface = clickItemInterface;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View v = null;
        switch (viewType) {
            case CANCEL_TYPE:
                v = LayoutInflater.from(parent.getContext()).inflate(R.layout.cancel_button, parent, false);
                break;
            case CENTODODICI_TYPE:
                v = LayoutInflater.from(parent.getContext()).inflate(R.layout.centododici_button, parent, false);
                break;
            case COC_TYPE:
                v = LayoutInflater.from(parent.getContext()).inflate(R.layout.call_coc_button, parent, false);
                break;
            case CALL_TYPE:
                v = LayoutInflater.from(parent.getContext()).inflate(R.layout.call_button, parent, false);
                break;

        }
        return new ViewHolder(v);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        holder.bind(list.get(position));
    }

    @Override
    public int getItemViewType(int position) {
        if (position == 0)
            return CANCEL_TYPE;
        else if (position == 1)
            return CENTODODICI_TYPE;

        return list.get(position).isCocNumber ? COC_TYPE : CALL_TYPE;
    }

    @Override
    public int getItemCount() {
        if (list != null)
            return list.size();
        return 0;
    }

    public class ViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener {
        @Nullable
        @BindView(R.id.number_phone)
        AutoResizeTextView numberPhone;
        @Nullable
        @BindView(R.id.coc_name)
        AutoResizeTextView cocName;
        private AssistenceObj item;

        public ViewHolder(View itemView) {
            super(itemView);
            ButterKnife.bind(this, itemView);
            itemView.setOnClickListener(this);
        }


        public void bind(AssistenceObj item) {
            this.item = item;
            if (numberPhone != null)
                numberPhone.setText(item.phoneNumber);
            if (cocName != null)
                cocName.setText(item.nameCoc);
        }

        @Override
        public void onClick(View v) {
            int pos = getAdapterPosition();
            switch (pos) {
                case 0:
                    clickItemInterface.clickCancel();
                    break;
                case 1:
                    clickItemInterface.clickCallOneOneTwo();
                    break;
                default:
                    clickItemInterface.clickItemToCall(item);
            }

        }
    }

    public interface ClickItemInterface {
        void clickCancel();

        void clickCallOneOneTwo();

        void clickItemToCall(AssistenceObj item);
    }
}
