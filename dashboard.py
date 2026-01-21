import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Brabantse Jongeren Monitor", page_icon="📊", layout="wide")

# --- KLEUREN UIT JE AFBEELDING ---
KLEUR_DONKER = "#234E65"  # Diep Teal
KLEUR_ACCENT = "#199FEC"  # Goud/Oker
KLEUR_WARM   = "#DD3F0F"  # Roest Oranje

# ====================================================================
#              👇 HIER KUN JE JE EIGEN TEKST AANPASSEN 👇
# ====================================================================

TITEL_DASHBOARD = "Brabantse Jongeren Monitor"

INTRO_TEKST = """
**Welkom op dit interactieve dashboard!**

Dit onderzoek is uitgevoerd om inzicht te krijgen in de leefwereld, zorgen en behoeften 
van jongeren in Noord-Brabant. Met behulp van deze tool kun je zelf door de data klikken 
en ontdekken wat er speelt.

**Hoe werkt het?**
* 👈 Gebruik het menu aan de linkerkant om te filteren op **Stad/Dorp** of **Geslacht**.
* 👆 Klik op de tabbladen hierboven om verschillende onderwerpen te bekijken.
"""

# ====================================================================
#              👆 TOT HIER AANPASSEN 👆
# ====================================================================

# --- 2. FUNCTIES ---
@st.cache_data
def laad_data():
    try:
        df = pd.read_csv('data.csv', sep=';', engine='python')
        df = df.rename(columns={
            'Woon je in een stad of dorp?': 'Locatie',
            'Wat is jouw leeftijd? (geef je leeftijd in cijfers)': 'Leeftijd',
            'Hoe identificieer jij je?': 'Geslacht',
            'Wat is jouw huidige opleiding?': 'Opleiding',
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

# --- 3. MAIN ---
df = laad_data()

if df is not None:
    
    # --- STYLING TOEPASSEN (De kleuren uit je afbeelding) ---
    st.markdown(f"""
        <style>
        .hoofd-titel {{ color: {KLEUR_DONKER}; font-size: 3rem; font-weight: 700; margin-bottom: 0px; }}
        .intro-box {{ 
            background-color: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 6px solid {KLEUR_ACCENT}; 
            color: #333;
            margin-bottom: 25px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filters")
    opties_locatie = df['Locatie'].unique()
    keuze_locatie = st.sidebar.multiselect("Woonplaats", opties_locatie, default=opties_locatie)
    
    opties_geslacht = df['Geslacht'].unique()
    keuze_geslacht = st.sidebar.multiselect("Geslacht", opties_geslacht, default=opties_geslacht)

    df_filtered = df[
        (df['Locatie'].isin(keuze_locatie)) &
        (df['Geslacht'].isin(keuze_geslacht))
    ]

    # --- 4. DE PAGINA OPBOUW ---
    
    # A. De Titel (in jouw kleur)
    st.markdown(f'<p class="hoofd-titel">{TITEL_DASHBOARD}</p>', unsafe_allow_html=True)
    
    # B. Jouw Intro Tekst (in het kader)
    st.markdown(f'<div class="intro-box">{INTRO_TEKST}</div>', unsafe_allow_html=True)

    # C. KPI's
    c1, c2, c3 = st.columns(3)
    c1.metric("Aantal Respondenten", len(df_filtered))
    if len(df_filtered) > 0:
        c2.metric("Gemiddelde Leeftijd", f"{df_filtered['Leeftijd'].mean():.1f} jaar")
    
    # D. Tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Demografie", "📢 Thema's", "🚀 Motivatie"])

    # Stel het kleurenpalet in op jouw 'imago' kleuren
    custom_palette = [KLEUR_DONKER, KLEUR_ACCENT, KLEUR_WARM, '#6C5B7B', '#4D8098']
    sns.set_palette(sns.color_palette(custom_palette))

    with tab1:
        st.subheader("Demografie")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Locatie', ax=ax)
            st.pyplot(fig)
        with col2:
            fig, ax = plt.subplots()
            # Pie chart met jouw kleuren
            counts = df_filtered['Geslacht'].value_counts()
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=custom_palette)
            st.pyplot(fig)

    with tab2:
        st.subheader("Grootste Zorgen")
        top_themas = split_en_tel(df_filtered['Themas']).head(10)
        fig, ax = plt.subplots(figsize=(10,5))
        sns.barplot(x=top_themas.values, y=top_themas.index, ax=ax, palette="dark:"+KLEUR_DONKER)
        st.pyplot(fig)

    with tab3:
        st.subheader("Communicatie & Deelname")
        st.write("Hoe kunnen we ze bereiken?")
        top_kanalen = split_en_tel(df_filtered['Kanalen'])
        fig, ax = plt.subplots()
        sns.barplot(x=top_kanalen.values, y=top_kanalen.index, ax=ax)
        st.pyplot(fig)

else:
    st.warning("Data niet gevonden!")