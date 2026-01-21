import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Brabantse Jongeren Monitor", page_icon="📊", layout="wide")

# ====================================================================
#              👇 HIER KUN JE JE EIGEN TEKST AANPASSEN 👇
# ====================================================================

TITEL_DASHBOARD = "Brabantse Jongeren Dashboard"

INTRO_TEKST = """
**Welkom!**

**Noord-Brabant telt ruim 600.000 jongeren met eigen ambities en dromen.** ✨

Toch zien we dat zij tegen steeds meer uitdagingen aanlopen, zoals prestatiedruk, 
mentale gezondheidskwesties en zorgen over hun leefomgeving.

De provincie wil af van beleid maken *over* jongeren, en toe naar beleid maken **méth** jongeren. 
Zodat zij actieve medeontwerpers worden van onze samenleving. 🤝

**Dit dashboard is de eerste stap:**
* 🔍 **Verken** de data via het menu aan de linkerkant.
* 📊 **Zie** waar de grootste zorgen en kansen liggen.
* 🚀 **Ontdek** hoe we deze generatie in hun kracht kunnen zetten

Hieronder zie je de resultaten van het onderzoek naar jongeren in Noord-Brabant.
We hebben gekeken naar hun zorgen, drijfveren en hoe we ze het beste kunnen bereiken.

**Gebruiksaanwijzing:**
1.  👈 Gebruik de **filters in de linkerbalk** om een specifieke doelgroep te kiezen (bijv. Vrouwen uit een Dorp).
2.  👇 Klik op de **tabbladen** hieronder om te wisselen tussen de onderwerpen.
"""

# ====================================================================
#              🎨 HIER REGELEN WE DE ACHTERGROND 🎨
# ====================================================================

def set_background(image_file):
    """
    Deze functie zorgt ervoor dat je plaatje als achtergrond wordt ingesteld
    en dat hij 'vast' staat (Parallax effect).
    """
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        b64_data = base64.b64encode(data).decode()
        
        # Hieronder staat de CSS magie
        # background-attachment: fixed;  <-- DIT ZORGT VOOR HET DIEPTE EFFECT
        # opacity: 0.15;                 <-- DIT MAAKT HEM IETS DOORZICHTIGER (zodat tekst leesbaar blijft)
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64_data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Zorg dat de witte tekst goed leesbaar blijft met een klein schaduwrandje */
        h1, h2, h3, p, li, .stMarkdown {{
            text-shadow: 2px 2px 4px #000000;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Kon achtergrondafbeelding '{image_file}' niet vinden. Zorg dat hij in de map staat!")

# --- AANROEPEN ACHTERGROND ---
# Zorg dat je een plaatje hebt genaamd 'achtergrond.jpg' in je map!
set_background('achtergrond.jpg') 


# --- 2. FUNCTIES VOOR DATA ---
@st.cache_data
def laad_data():
    try:
        df = pd.read_csv('data.csv', sep=';', engine='python')
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

# --- 3. INLADEN ---
df = laad_data()

if df is not None:
    
    # --- 4. SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filters")
    
    opties_locatie = df['Locatie'].unique()
    keuze_locatie = st.sidebar.multiselect("Woonplaats", opties_locatie, default=opties_locatie)
    
    opties_geslacht = df['Geslacht'].unique()
    keuze_geslacht = st.sidebar.multiselect("Geslacht", opties_geslacht, default=opties_geslacht)

    opties_opleiding = df['Opleiding'].unique()
    keuze_opleiding = st.sidebar.multiselect("Opleiding", opties_opleiding, default=opties_opleiding)
    
    if df['Leeftijd'].notnull().any():
        min_l = int(df['Leeftijd'].min())
        max_l = int(df['Leeftijd'].max())
        keuze_leeftijd = st.sidebar.slider("Leeftijd", min_l, max_l, (min_l, max_l))
    else:
        keuze_leeftijd = (0, 100)

    # --- FILTER TOEPASSEN ---
    df_filtered = df[
        (df['Locatie'].isin(keuze_locatie)) &
        (df['Geslacht'].isin(keuze_geslacht)) &
        (df['Opleiding'].isin(keuze_opleiding)) &
        (df['Leeftijd'] >= keuze_leeftijd[0]) &
        (df['Leeftijd'] <= keuze_leeftijd[1])
    ]

    # --- 5. HOOFDPAGINA ---
    
    st.title(TITEL_DASHBOARD)
    st.markdown(INTRO_TEKST)
    st.markdown("---")

    # KPI's
    st.markdown(f"**Geselecteerde groep:** {len(df_filtered)} respondenten")

    # TABBLADEN
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Demografie", 
        "📢 Thema's", 
        "🚀 Motivatie", 
        "📱 Communicatie",
        "📋 Ruwe Data"
    ])

    # Omdat we nu een donkere achtergrond hebben via config.toml, 
    # moeten we de grafieken ook een beetje aanpassen zodat ze mooi blijven.
    # We gebruiken een donkere achtergrond-stijl voor Seaborn.
    sns.set_style("darkgrid") 

    with tab1:
        st.header("Demografie")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Woonplaats")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Locatie', palette='viridis', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
        with col2:
            st.subheader("Opleiding")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, y='Opleiding', palette='rocket', ax=ax)
            st.pyplot(fig)
            
    with tab2:
        st.header("Grootste Zorgen")
        top_themas = split_en_tel(df_filtered['Themas']).head(15)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_themas.values, y=top_themas.index, palette='Reds_r', ax=ax)
        st.pyplot(fig)

    with tab3:
        st.header("Motivatie")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Deelname")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Deelname', palette='Set2', ax=ax)
            st.pyplot(fig)
        with c2:
            st.subheader("Redenen")
            top_motivatie = split_en_tel(df_filtered['Motivatie_Combined']).head(10)
            fig, ax = plt.subplots()
            sns.barplot(x=top_motivatie.values, y=top_motivatie.index, palette='Greens_r', ax=ax)
            st.pyplot(fig)

    with tab4:
        st.header("Communicatie")
        top_kanalen = split_en_tel(df_filtered['Kanalen'])
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top_kanalen.values, y=top_kanalen.index, palette='Blues_r', ax=ax)
        st.pyplot(fig)

    with tab5:
        st.header("Ruwe Data")
        st.dataframe(df_filtered)

else:
    st.warning("Data niet gevonden!")