import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
import re
from wordcloud import WordCloud
import plotly.express as px
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# Download NLTK data (silently)
import nltk

import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

from nltk.corpus import stopwords

# ========== Utility Functions ==========

def preprocess_text(text):
    stop_words = set(stopwords.words('indonesian') + stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text.lower())
    words = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    return ' '.join(words)

def plot_confusion_matrix(y_true, y_pred, title="Confusion Matrix"):
    labels = sorted(list(set(list(y_true) + list(y_pred))))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title(title)
    return fig

def generate_wordcloud(text, title=None):
    if not text.strip():
        st.write("No data available to generate WordCloud.")
        return
    wc = WordCloud(
        background_color='white',
        max_words=100,
        width=400,
        height=300,
        contour_width=1,
        contour_color='steelblue',
        collocations=False,
        stopwords=set(stopwords.words('indonesian') + stopwords.words('english'))
    ).generate(text)
    plt.figure(figsize=(6, 4))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    if title:
        plt.title(title)
    st.pyplot(plt)

# ========== Cache Loaders ==========

@st.cache_data(show_spinner=True)
def load_data():
    return pd.read_csv('data/data_dengan_sentimen.csv')

@st.cache_resource(show_spinner=True)
def load_models():
    models = {}
    try:
        models['nb'] = joblib.load('model/nb_pipeline.pkl')
        models['svm'] = joblib.load('model/svm_pipeline.pkl')
        models['xgb'] = joblib.load('model/xgb_pipeline.pkl')
        models['tfidf'] = joblib.load('model/tfidf_vectorizer.pkl')
        models['label_encoder'] = joblib.load('model/label_encoder.pkl')
    except Exception as e:
        st.error(f"Error loading models: {e}")
    return models

# ========== PAGE CONFIG ==========

st.set_page_config(
    page_title="Dashboard Perbandingan Analisis Sentimen",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== SIDEBAR & APP STYLING ==========

st.markdown("""
<style>
/* ========== BACKGROUND HALAMAN PUTIH ========== */
.stApp {
    background-color: #ffffff !important;
    color: #1A1A1A !important;
}

/* ========== SIDEBAR NAVY ========== */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background-color: #1f2a40 !important;
    color: white !important;
    box-shadow: none !important;
    border: none !important;
}

/* ========== OPTION_MENU CUSTOM ========== */
.css-1d391kg {  /* container option_menu */
    background-color: transparent !important;
    color: white !important;
    border: none !important;
}

.css-1d391kg ul {
    background-color: transparent !important;
}

.css-1d391kg ul li a {
    background-color: transparent !important;
    color: #e0e6ed !important;
    font-weight: bold;
    border-radius: 8px;
    margin-bottom: 6px;
    padding: 10px;
    transition: 0.3s ease;
}

/* Aktif saat diklik */
.css-1d391kg ul li a[data-selected="true"] {
    background-color: #f87171 !important;
    color: white !important;
}

/* Hover efek */
.css-1d391kg ul li a:hover {
    background-color: #334155 !important;
    color: white !important;
}

/* ========== TOMBOL ========== */
div.stButton > button {
    background-color: #f0f4f8 !important;
    color: #1A1A1A !important;
    border: 1px solid #1A1A1A !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    background-color: #dbeafe !important;
    color: #1A1A1A !important;
    border-color: #1A1A1A !important;
}

/* ========== INPUT PUTIH ========== */
.stTextInput > div > div > input,
.stFileUploader > div {
    background-color: #ffffff !important;
    color: #1A1A1A !important;
    border: 1px solid #ccc !important;
}

/* ========== TEKS UMUM ========== */
.stApp, .stMarkdown, .stText, .stHeader, .stSubheader,
.stCaption, .stDataFrame, .stTable, .stExpander, .stCard {
    color: #1A1A1A !important;
}

/* ========== FOOTER ========== */
.footer {
    background-color: #1f2a40 !important;
    color: white !important;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
}

.footer a {
    color: #60a5fa;
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)


# ========== SIDEBAR HEADER ==========

st.markdown("""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg" width="100"/>
        <h1 style="margin: 0; color: black; font-size: 60px;">
           Dashboard Perbandingan Analisis Sentimen
        </h1>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
        selected_tab = option_menu(
        "Menu", 
      ["Analisis Sentimen", "Perbandingan Algoritma", "Prediksi Sentimen"],
        icons=["bar-chart", "activity", "search"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"background-color": "#1f2a40"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {
                "color": "white !important",
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#334155",
            },
            "nav-link-selected": {
                "background-color": "#2b019e",
                "color": "white !important",
                "font-weight": "bold",
            },
            "menu-title": {
                "color": "white",
                "font-size": "24px",
                "text-align": "",
                "margin-bottom": "10px",
            }
        }
    )
# ========== Load Data & Models ==========

data = load_data()
models = load_models()

nb_model = models.get('nb')
svm_model = models.get('svm')
xgb_model = models.get('xgb')
tfidf_vectorizer = models.get('tfidf')
le = models.get('label_encoder')

# ========== Split Data ==========

train_data, test_data = train_test_split(
    data, test_size=0.2, random_state=42, stratify=data['Sentiment']
)
X_test_raw = test_data['tweet']
y_test = test_data['Sentiment']

# ========== PAGE LOGIC ==========

if selected_tab == "Analisis Sentimen":
    st.subheader("Analisis Sentimen")

    # ===== TAMBAHAN: KOTAK JUMLAH DATA =====
    jumlah_sebelum = 18691
    jumlah_sesudah = 12509

    st.markdown("""
        <style>
        .box {
            background-color: rgba(31, 45, 85, 0.9); 
            padding: 25px;
            border-radius: 15px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
        .box span {
            font-size: 34px;
            display: block;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='box'>
            Data Mentah
            <span>{jumlah_sebelum}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='box'>
            Data Preprocessing
            <span>{jumlah_sesudah}</span>
        </div>
        """, unsafe_allow_html=True)

    sentiment_counts = data['Sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentimen', 'Jumlah']  # <- ubah nama kolom di sini

    # Mapping label ke format baku
    label_mapping = {
    "positif": "Positif",
    "negatif": "Negatif",
    "netral": "Netral"
    }

    # Bersihkan label → lowercase, strip spasi
    sentiment_counts["Sentimen"] = sentiment_counts["Sentimen"].astype(str).str.strip().str.lower()

    # Map label ke format standar
    sentiment_counts["Sentimen"] = sentiment_counts["Sentimen"].map(label_mapping)

    # Hapus baris kosong (jika ada label tidak dikenali)
    sentiment_counts = sentiment_counts.dropna(subset=["Sentimen"])

    # Urutkan label sesuai mapping warna
    sentiment_order = ["Positif", "Negatif", "Netral"]
    sentiment_counts = (
        sentiment_counts
        .set_index("Sentimen")
        .reindex(sentiment_order)
        .fillna(0)
        .reset_index()
    )

    color_map = {
        "Positif": "#2ecc71",   
        "Negatif": "#e74c3c",   
        "Netral": "#3498db"    
    }

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.bar(
            sentiment_counts,
            x='Sentimen',
            y='Jumlah',
            color='Sentimen',
            title="Distribusi Sentimen",
            color_discrete_map=color_map
        )
        fig_bar.update_layout(
            width=400,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000", size=16),
            title_font=dict(size=18, color="#000000"),
            legend=dict(font=dict(color="#000000")),
            xaxis=dict(
                title_font=dict(color="#000000", size=14),
                tickfont=dict(color="#000000", size=12)
            ),
            yaxis=dict(
                title_font=dict(color="#000000", size=14),
                tickfont=dict(color="#000000", size=12)
            )
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            sentiment_counts,
            values='Jumlah',
            names='Sentimen',
            hole=0.4,
            title="Proporsi Sentimen",
            color='Sentimen',                    
            color_discrete_map=color_map
        )
        fig_pie.update_layout(
            width=400,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#000000", size=16),
            title_font=dict(size=18, color="#000000"),
            legend=dict(font=dict(color="#000000"))
        )
        fig_pie.update_traces(
            textinfo='percent+label',
            textfont_color='#000000'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    freq = pd.Series(' '.join(data['tweet']).split()).value_counts().head(20)
    fig_freq = px.bar(
        freq,
        x=freq.index,
        y=freq.values,
        labels={'x': 'Kata', 'y': 'Frekuensi'},
        title="20 Kata Teratas Berdasarkan Frekuensi"
    )

    fig_freq.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#000000", size=16),
        title_font=dict(size=20, color="#000000"),
        legend=dict(font=dict(color="#000000")),
        xaxis=dict(
            title_font=dict(color='#000000', size=16),
            tickfont=dict(color='#000000', size=14)
        ),
        yaxis=dict(
            title_font=dict(color='#000000', size=16),
            tickfont=dict(color='#000000', size=14)
        )
    )

    fig_freq.update_traces(textfont_color='#000000')
    st.plotly_chart(fig_freq, use_container_width=True)

    st.markdown("### WordCloud per Sentimen")
    sentiments = ['Positif', 'Negatif', 'Netral']
    cols_wc = st.columns(len(sentiments))
    for i, sent in enumerate(sentiments):
        subset_text = ' '.join(data[data['Sentiment'] == sent]['tweet'].apply(preprocess_text))
        with cols_wc[i]:
            st.markdown(f"#### {sent}")
            generate_wordcloud(subset_text)

elif selected_tab == "Perbandingan Algoritma": 
    st.header("Perbandingan Algoritma")

    models_dict = {
        "Naive Bayes": nb_model,
        "Support Vector Machine": svm_model,
        "XGBoost": xgb_model
    }

    known_labels = set(le.classes_)
    mask = y_test.isin(known_labels)
    X_test_raw_filtered = X_test_raw[mask]
    y_test_filtered = y_test[mask]

    X_test_prep = X_test_raw_filtered.apply(preprocess_text)

    metrics_summary = {
        "Model": [],
        "Accuracy": [],
        "Precision": [],
        "Recall": [],
        "F1-score": []
    }

    cols_models = st.columns(3)

    model_results = {}

    for i, (model_name, model) in enumerate(models_dict.items()):
        with cols_models[i]:
            st.markdown(f"### {model_name}")

            if model is None:
                st.warning("Model not loaded.")
                continue

            y_pred = model.predict(X_test_prep)
            y_pred_encoded = le.transform(y_pred) if isinstance(y_pred[0], str) else y_pred
            y_test_encoded = le.transform(y_test_filtered)
            y_true_str = le.inverse_transform(y_test_encoded)
            y_pred_str = le.inverse_transform(y_pred_encoded)

            acc = accuracy_score(y_true_str, y_pred_str)
            report = classification_report(
                y_true_str, y_pred_str,
                labels=["Positif", "Negatif", "Netral"],
                output_dict=True,
                zero_division=0
            )
            precision = report['weighted avg']['precision']
            recall = report['weighted avg']['recall']
            f1score = report['weighted avg']['f1-score']

            metrics_summary["Model"].append(model_name)
            metrics_summary["Accuracy"].append(acc)
            metrics_summary["Precision"].append(precision)
            metrics_summary["Recall"].append(recall)
            metrics_summary["F1-score"].append(f1score)

            fig_cm = plot_confusion_matrix(y_true_str, y_pred_str, f"{model_name}")
            st.pyplot(fig_cm)

            with st.expander("Report"):
                # Tampilkan classification report table
                report_df = pd.DataFrame(report).transpose()
                report_df = report_df.round(2)  
                st.dataframe(report_df)


                # Overall accuracy & jumlah data uji
                overall_acc = round(report["accuracy"], 2)  
                n_test_data = len(y_true_str)

                st.markdown(f"""
                    <div style="
                        background-color: #ffe6e6;
                        border-left: 5px solid #ff4d4d;
                        padding: 10px;
                        margin-top: 10px;
                        color: black;
                        ">
                        <b>Akurasi Keseluruhan:</b> {overall_acc:.2f}<br>
                        <b>Jumlah Data Uji:</b> {n_test_data}
                        </div>
                    """, unsafe_allow_html=True)


                # Klasifikasi hasil algoritma
                pred_counts = pd.Series(y_pred_str).value_counts().to_dict()
                st.markdown("<h4>Ringkasan Hasil Klasifikasi:</h4>", unsafe_allow_html=True)

                for label, count in pred_counts.items():
                    st.markdown(f"- <b>{label}:</b> {count} data", unsafe_allow_html=True)

                # Kesimpulan sederhana
                conclusion = ""
                if overall_acc >= 0.85:
                    conclusion = "Model ini memiliki performa yang sangat baik untuk analisis sentimen."
                elif overall_acc >= 0.7:
                    conclusion = "Model ini memiliki performa yang cukup baik, namun masih bisa ditingkatkan."
                else:
                    conclusion = "Model ini memiliki performa yang kurang optimal dan perlu perbaikan."

                st.markdown(f"""
                    <div style="
                        background-color: #ccf5ff;
                        border-left: 5px solid #007acc;
                        padding: 10px;
                        margin-top: 10px;
                        color: black;
                    ">
                        <b>Kesimpulan:</b><br>{conclusion}
                    </div>
                """, unsafe_allow_html=True)

            # Simpan hasil akurasi untuk rekomendasi
            model_results[model_name] = round(overall_acc, 2)

        import plotly.express as px

    st.subheader("Perbandingan Metrik Antar Model")

    if metrics_summary["Model"]:
        # Siapkan data dalam format long
        df = pd.DataFrame(metrics_summary)
        df_long = df.melt(id_vars="Model", var_name="Metrik", value_name="Nilai")

        # Buat bar chart vertikal: grup per metrik, isi oleh model
        fig = px.bar(
            df_long,
            x="Metrik",             # Grup per metrik
            y="Nilai",              # Nilai metrik ke atas
            color="Model",          # Warna berdasarkan model
            barmode="group",        # Berkelompok, bukan tumpuk
            text="Nilai",
            height=600,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside',
            opacity=0.9
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            xaxis=dict(title='Metrik', color='white'),
            yaxis=dict(title='Nilai Metrik', color='white', range=[0, 1.1]),
            legend=dict(
                title='Model',
                bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- NEW: Rekomendasi Model ---
        best_model_name = max(model_results, key=model_results.get)
        best_model_acc = model_results[best_model_name]

        st.markdown(f"""
            <div style="
                background-color: #d4edda;
                border-left: 5px solid #28a745;
                padding: 10px;
                margin-top: 20px;
                color: black;
            ">
                <b>🔍 Rekomendasi Model:</b><br>
                Model yang direkomendasikan adalah <b>{best_model_name}</b> dengan akurasi {best_model_acc:.2f}.
            </div>
        """, unsafe_allow_html=True)

    else:
        st.info("No evaluation metrics available.")


elif selected_tab == "Prediksi Sentimen":
    
    st.subheader("Prediksi Sentimen")

    if not all([nb_model, svm_model, xgb_model]):
        st.error("Beberapa model belum dimuat. Pastikan semua model tersedia.")
    else:
        new_text = st.text_input("Masukkan teks untuk prediksi sentimen:")

        if st.button("Prediksi Sentimen"):
            if not new_text.strip():
                st.warning("Silakan masukkan beberapa teks.")
            else:
                preprocessed = preprocess_text(new_text)
                try:
                    predictions = {
                        "Naive Bayes": nb_model.predict([preprocessed])[0],
                        "SVM": svm_model.predict([preprocessed])[0],
                        "XGBoost": xgb_model.predict([preprocessed])[0]
                    }

                    # Decode jika pakai LabelEncoder
                    if le:
                        predictions = {k: le.inverse_transform([v])[0] for k, v in predictions.items()}

                    st.markdown("### 🔍 Hasil Prediksi:")
                    for model_name, pred in predictions.items():
                        st.success(f"**{model_name}** → {pred.capitalize()}")

                except Exception as e:
                    st.error(f"Prediction error: {e}")

        st.markdown("### 📂 Prediksi Sentimen dari File")
        uploaded_file = st.file_uploader("Unggah file teks:", type=["txt"])

        if uploaded_file is not None:
            lines = uploaded_file.read().decode('utf-8').split('\n')
            clean_lines = [line for line in lines if line.strip()]
            preprocessed_lines = [preprocess_text(line) for line in clean_lines]

            try:
                predictions_nb = nb_model.predict(preprocessed_lines)
                predictions_svm = svm_model.predict(preprocessed_lines)
                predictions_xgb = xgb_model.predict(preprocessed_lines)

                if le:
                    predictions_nb = le.inverse_transform(predictions_nb)
                    predictions_svm = le.inverse_transform(predictions_svm)
                    predictions_xgb = le.inverse_transform(predictions_xgb)

                results_df = pd.DataFrame({
                    "Teks": clean_lines,
                    "Naive Bayes": [p.capitalize() for p in predictions_nb],
                    "SVM": [p.capitalize() for p in predictions_svm],
                    "XGBoost": [p.capitalize() for p in predictions_xgb]
                })

                st.markdown("### 🧾 Hasil Prediksi Teks dari File:")
                st.dataframe(results_df)

            except Exception as e:
                st.error(f"Prediction error: {e}")

# ========== FOOTER ==========

current_year = datetime.now().year
st.markdown(f"""
    <style>
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #333;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        z-index: 1000;
    }}
    .footer a {{
        color: #00b6ff;
        text-decoration: none;
    }}
    .footer a:hover {{
        text-decoration: underline;
    }}
    </style>
    <div class="footer">
        Copyright © {current_year} | Apps Created by <b><a href="https://www.linkedin.com/in/sriagustin/" target="_blank">Sri Agustin</a></b>
    </div>
""", unsafe_allow_html=True)
