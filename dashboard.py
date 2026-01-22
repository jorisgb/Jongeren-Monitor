import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import io  # <--- NIEUW: Nodig voor de downloadfunctionaliteit

st.markdown("""
    <style>
        /* 1. De Grote Titel bovenaan (H1) */
        h1 {
            font-size: 40px !important;
        }
        
        /* 2. De tussenkopjes (H2 en H3) */
        h2 {
            font-size: 30px !important;
        }
        h3 {
            font-size: 24px !important;
        }
        
        /* 3. De normale tekst en lijsten (p en li) */
        p, li, .stMarkdown {
            font-size: 20px !important; 
        }
        
        /* 4. De kleine lettertjes (captions onder grafieken) */
        .stCaption {
            font-size: 14px !important;
        }
    </style>
""", unsafe_allow_html=True)

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

De provincie wil af van beleid maken *over* jongeren, en toe naar beleid maken **mét** jongeren. 
Zodat zij actieve medeontwerpers worden van onze samenleving. 🤝

**Dit dashboard is de eerste stap:**
* 🔍 **Verken** de data via het menu aan de linkerkant.
* ⚖️ **Vergelijk** groepen (bijv. Stad vs Dorp) in het nieuwe tabblad.
* 🚀 **Ontdek** hoe we deze generatie in hun kracht kunnen zetten.
"""

# ====================================================================
#              🎨 ACHTERGROND & STYLING 🎨
# ====================================================================
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        b64_data = base64.b64encode(data).decode()
        
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64_data}");
            background-size: cover;
            background-position: center;
            background-attachment: scroll;
        }}
        h1, h2, h3, p, li, .stMarkdown {{
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Geen plaatje? Geen probleem.

set_background('achtergrond.jpg')

# ====================================================================
#              ⚙️ FUNCTIES ⚙️
# ====================================================================

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
    """Simpele teller voor enkele lijsten"""
    alle_items = []
    for item in series.dropna():
        if isinstance(item, str):
            stukjes = [x.strip() for x in item.split(',')]
            alle_items.extend([s for s in stukjes if s])
    return pd.Series(alle_items).value_counts()

def bereid_data_voor_vergelijking(df, kolom_met_lijstjes, groepeer_kolom):
    """
    Speciale functie die data 'uit elkaar trekt' zodat we groepen kunnen vergelijken.
    """
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
    """Maakt een mooie zin op basis van de gekozen filters"""
    tekst = "Deze grafiek toont de resultaten voor: "
    delen = []
    
    if len(filters['Locatie']) > 0: delen.append(f"inwoners uit {', '.join(filters['Locatie'])}")
    if len(filters['Geslacht']) > 0: delen.append(f"personen die zich identificeren als {', '.join(filters['Geslacht'])}")
    if len(filters['Opleiding']) > 0: delen.append(f"studenten van {', '.join(filters['Opleiding'])}")
    
    if