package it.netfarm.mymedbook.mymedtag.documents;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;
import java.util.Locale;

import butterknife.BindView;
import butterknife.ButterKnife;
import it.netfarm.mymedbook.mymedtag.R;
import it.netfarm.mymedbook.mymedtag.model.Document;

class AdapterDocuments extends RecyclerView.Adapter<AdapterDocuments.ViewHolder> {
    private final List<Document> items;
    private final DocumentsInterface mListner;

    public AdapterDocuments(List<Document> documents, DocumentsInterface listner) {
        items = documents;
        mListner = listner;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.documents_adapter, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        holder.bind(items.get(position));
    }

    @Override
    public int getItemCount() {
        return items.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener {
        @BindView(R.id.name_doc_text)
        TextView nameDoc;

        public ViewHolder(View itemView) {
            super(itemView);
            ButterKnife.bind(this, itemView);
            itemView.setOnClickListener(this);
        }

        public void bind(Document document) {
            nameDoc.setText(String.format(Locale.getDefault(), "%d", document.getPk()));
        }

        @Override
        public void onClick(View view) {
            mListner.clickDoc(items.get(getAdapterPosition()));
        }
    }

    interface DocumentsInterface {
        void clickDoc(Document document);
    }
}
