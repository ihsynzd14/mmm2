package it.netfarm.mymedbook.mymedtag.documents;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;

import butterknife.BindView;
import butterknife.ButterKnife;
import it.netfarm.mymedbook.mymedtag.R;
import it.netfarm.mymedbook.mymedtag.model.MyDossiers;



class DossiersAdapter extends RecyclerView.Adapter<DossiersAdapter.ViewHolder> {

    private final ArrayList<MyDossiers> mList;
    private final DossierListner mListner;

    public DossiersAdapter(ArrayList<MyDossiers> listDossier, DossierListner listner) {
        this.mListner = listner;
        this.mList = listDossier;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.dossier_adapter, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        holder.bind(mList.get(position));
    }

    @Override
    public int getItemCount() {
        return mList.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener {
        @BindView(R.id.dossier_name)
        TextView dossierName;

        public ViewHolder(View itemView) {
            super(itemView);
            ButterKnife.bind(this, itemView);
            itemView.setOnClickListener(this);
        }

        public void bind(MyDossiers item) {
            dossierName.setText(item.getName());
        }

        @Override
        public void onClick(View view) {
            mListner.clickDossier(mList.get(getAdapterPosition()));
        }
    }

    interface DossierListner {
        void clickDossier(MyDossiers idDossier);
    }
}

