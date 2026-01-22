import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import io

st.markdown("""
    <style>
        h1 { font-size: 40px !important; }
        h2 { font-size: 30px !important; }
        h3 { font-size: 24px !important; }
        p, li, .stMarkdown { font-size: 20px !important; }
        .stCaption { font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Brabantse Jongeren Monitor", page_icon="📊", layout="wide")

TITEL_DASHBOARD = "Brabantse Jongeren Dashboard"
INTRO_TEKST = """
**Welkom!**

**Noord-Brabant telt ruim 600.000 jongeren met eigen ambities en dromen.** ✨
Toch zien we dat zij tegen steeds meer uitdagingen aanlopen.
Dit dashboard helpt om beleid te maken **mét** jongeren.

* 🔍 **Verken** de data.
* ⚖️ **Vergelijk** groepen.
* 🚀 **Ontdek** inzichten.
"""

# --- ACHTERGROND ---
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        b64_data = base64.b64encode(data).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64_data}");
            background-size: cover;
            background-position: center;
            background-attachment: scroll;
        }}
        </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

set_background('achtergrond.jpg')

# --- FUNCTIES ---
@st.cache_data
def laad_data():
    try:
        # Probeer eerst puntkomma (NL excel), anders komma
        try:
            df = pd.read_csv('data.csv', sep=';', engine='python')
        except:
            df = pd.read_csv('data.csv', sep=',', engine='python')
            
        df = df.rename(columns={
            'Woon je in een stad of dorp?': 'Locatie',
            'Wat is jouw leeftijd? (geef je leeftijd in cijfers)': 'Leeftijd',
            'Hoe identificieer jij je?': 'Geslacht',
            'Wat is jou religie of levensovertuiging?': 'Religie',
            'Wat is jouw huidige opleiding?': 'Opleiding',
            'Voor het grootste deel in de week ben ik:': 'Status',
            'Vink dat thema aan en vul daarnaast ook aan welke andere thema’s jij zorgen over hebt. (Meerdere antwoorden mogelijk)': 'Themas',
            'Zou jij in de toekomst meedoen aan de Brabantse Jongerenmonitor?': 'Deelname',
            'Wat zou jou motiveren om mee te doen? (meerdere antwoorden mogelijk) ': 'Motivatie_1',
            'Wat zou jou motiveren om wél deel te nemen? (Meerdere antwoorden mogelijk)': 'Motivatie_2',
            'Via welk kanaal zouden we jou het beste kunnen bereiken? (Meerdere antwoorden mogelijk)': 'Kanalen'
        })
        
        df['Leeftijd'] = pd.to_numeric(df['Leeftijd'], errors='coerce')
        df['Motivatie_Combined'] = df['Motivatie_1'].fillna('') + ',' + df['Motivatie_2'].fillna('')
        return df
    except Exception as e:
        st.error(f"Fout bij laden data: {e}")
        return None

def split_en_tel(series):
    alle_items = []
    for item in series.dropna():
        if isinstance(item, str):
            stukjes = [x.strip() for x in item.split(',')]
            alle_items.extend([s for s in stukjes if s])
    return pd.Series(alle_items).value_counts()

def voeg_download_knop_toe(figuur, bestandsnaam):
    """Maakt een downloadknop voor de grafiek"""
    buf = io.BytesIO()
    figuur.savefig(buf, format="png", bbox_inches='tight', dpi=300)
    buf.seek(0)
    st.download_button(
        label=f"📥 Download {bestandsnaam}",
        data=buf,
        file_name=bestandsnaam,
        mime="image/png"
    )

def bereid_data_voor_vergelijking(df, kolom_met_lijstjes, groepeer_kolom):
    records = []
    for index, row in df.iterrows():
        waarde = row[kolom_met_lijstjes]
        groep = row[groepeer_kolom]
        if isinstance(waarde, str) and isinstance(groep, str):
            items = [x.strip() for x in waarde.split(',')]
            for item in items:
                if item:
                    records.append({'Item': item, 'Groep': groep})
    return pd.DataFrame(records)

def maak_beschrijving(filters):
    tekst = "Resultaten voor: "
    delen = []
    if len(filters['Locatie']) > 0: delen.append(f"inwoners uit {', '.join(filters['Locatie'])}")
    if len(filters['Geslacht']) > 0: delen.append(f"{', '.join(filters['Geslacht'])}")
    if len(filters['Opleiding']) > 0: delen.append(f"studenten {', '.join(filters['Opleiding'])}")
    
    if not delen: return tekst + "Iedereen."
    return tekst + " + ".join(delen) + "."

# --- HOOFD PROGRAMMA ---
df = laad_data()

if df is not None:
    # FILTERS
    st.sidebar.header("🔍 Filters")
    opties_locatie = df['Locatie'].dropna().unique()
    keuze_locatie = st.sidebar.multiselect("Woonplaats", opties_locatie, default=opties_locatie)
    
    opties_geslacht = df['Geslacht'].dropna().unique()
    keuze_geslacht = st.sidebar.multiselect("Geslacht", opties_geslacht, default=opties_geslacht)

    opties_opleiding = df['Opleiding'].dropna().unique()
    keuze_opleiding = st.sidebar.multiselect("Opleiding", opties_opleiding, default=opties_opleiding)
    
    if df['Leeftijd'].notnull().any():
        min_l, max_l = int(df['Leeftijd'].min()), int(df['Leeftijd'].max())
        keuze_leeftijd = st.sidebar.slider("Leeftijd", min_l, max_l, (min_l, max_l))
    else:
        keuze_leeftijd = (0, 100)

    df_filtered = df[
        (df['Locatie'].isin(keuze_locatie)) &
        (df['Geslacht'].isin(keuze_geslacht)) &
        (df['Opleiding'].isin(keuze_opleiding)) &
        (df['Leeftijd'] >= keuze_leeftijd[0]) &
        (df['Leeftijd'] <= keuze_leeftijd[1])
    ]
    
    beschrijving_tekst = maak_beschrijving({'Locatie': keuze_locatie, 'Geslacht': keuze_geslacht, 'Opleiding': keuze_opleiding})

    st.title(TITEL_DASHBOARD)
    st.markdown(INTRO_TEKST)
    st.markdown("---")
    st.markdown(f"**Huidige selectie:** {len(df_filtered)} respondenten")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Demografie", "📢 Thema's", "🚀 Motivatie", "📱 Communicatie", "⚖️ Vergelijken", "📋 Data"])
    sns.set_style("darkgrid")

    # TAB 1: DEMOGRAFIE
    with tab1:
        st.header("Wie zijn deze jongeren?")
        st.info(f"ℹ️ {beschrijving_tekst}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Woonplaats")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Locatie', palette='viridis', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "woonplaats.png") # <--- NU GOED!
            
        with c2:
            st.subheader("Opleiding")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, y='Opleiding', palette='rocket', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "opleiding.png")

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Leeftijd")
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['Leeftijd'], bins=10, kde=True, color='skyblue', ax=ax)
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "leeftijd.png")
        
        with c4:
            st.subheader("Geslacht")
            fig, ax = plt.subplots()
            counts = df_filtered['Geslacht'].value_counts()
            if len(counts) > 0: ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "geslacht.png")

    # TAB 2: THEMA'S
    with tab2:
        st.header("Zorgen")
        st.info(f"ℹ️ {beschrijving_tekst}")
        top = split_en_tel(df_filtered['Themas']).head(15)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top.values, y=top.index, palette='Reds_r', ax=ax)
        st.pyplot(fig)
        voeg_download_knop_toe(fig, "themas.png") # <--- NU GOED!

    # TAB 3: MOTIVATIE
    with tab3:
        st.header("Motivatie")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Deelname bereidheid")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Deelname', palette='Set2', ax=ax)
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "deelname.png")
        with c2:
            st.subheader("Drijfveren")
            top = split_en_tel(df_filtered['Motivatie_Combined']).head(10)
            fig, ax = plt.subplots()
            sns.barplot(x=top.values, y=top.index, palette='Greens_r', ax=ax)
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "drijfveren.png")

    # TAB 4: COMMUNICATIE
    with tab4:
        st.header("Kanalen")
        top = split_en_tel(df_filtered['Kanalen'])
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top.values, y=top.index, palette='Blues_r', ax=ax)
        st.pyplot(fig)
        voeg_download_knop_toe(fig, "kanalen.png")

    # TAB 5: VERGELIJKING
    with tab5:
        st.header("⚖️ Vergelijk Groepen")
        c1, c2, c3 = st.columns(3)
        onderwerp = c1.selectbox("1. Onderwerp", ["Thema's (Zorgen)", "Communicatie Kanalen", "Motivatie om mee te doen"])
        vergelijk_op = c2.selectbox("2. Vergelijk op", ["Locatie", "Geslacht", "Opleiding", "Deelname"])
        weergave = c3.radio("3. Weergave", ["Aantallen", "Percentages"], horizontal=True)

        kolom_map = {"Thema's (Zorgen)": 'Themas', "Communicatie Kanalen": 'Kanalen', "Motivatie om mee te doen": 'Motivatie_Combined'}
        
        vergelijk_df = bereid_data_voor_vergelijking(df_filtered, kolom_map[onderwerp], vergelijk_op)
        
        if not vergelijk_df.empty:
            tel_df = vergelijk_df.groupby(['Groep', 'Item']).size().reset_index(name='Aantal')
            groep_totalen = df_filtered[vergelijk_op].value_counts()
            tel_df['Percentage'] = tel_df.apply(lambda row: (row['Aantal'] / groep_totalen.get(row['Groep'], 1)) * 100, axis=1)
            
            top_items = vergelijk_df['Item'].value_counts().head(10).index
            plot_df = tel_df[tel_df['Item'].isin(top_items)]
            
            st.subheader(f"Verschil in '{onderwerp}' per '{vergelijk_op}'")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x_as = 'Aantal' if weergave == "Aantallen" else 'Percentage'
            sns.barplot(data=plot_df, y='Item', x=x_as, hue='Groep', palette='tab10', ax=ax, order=top_items)
            if weergave == "Percentages": ax.set_xlim(0, 100)
            
            st.pyplot(fig)
            voeg_download_knop_toe(fig, "vergelijking.png") # <--- NU GOED!
        else:
            st.warning("Te weinig data.")

    # TAB 6: DATA
    with tab6:
        st.dataframe(df_filtered)

else:
    st.warning("Geen data geladen.")