import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Brabantse Jongeren Monitor", page_icon="📊", layout="wide")

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
    
    # A. De Titel
    st.title(TITEL_DASHBOARD)
    
    # B. Jou