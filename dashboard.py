import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURATIE (Moet als eerste!) ---
st.set_page_config(page_title="Brabantse Jongeren Monitor", page_icon="📊", layout="wide")

# --- 2. FUNCTIES ---

@st.cache_data
def laad_data():
    try:
        # Lees data in
        df = pd.read_csv('data.csv', sep=';', engine='python')
        
        # Hernoem kolommen naar korte namen
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
        
        # Leeftijd schoonmaken (zorg dat het getallen zijn)
        df['Leeftijd'] = pd.to_numeric(df['Leeftijd'], errors='coerce')
        
        # Motivatie samenvoegen
        df['Motivatie_Combined'] = df['Motivatie_1'].fillna('') + ',' + df['Motivatie_2'].fillna('')
        
        return df
    except Exception as e:
        st.error(f"Fout bij laden data: {e}")
        return None

def split_en_tel(series):
    """Hulpfunctie om komma-gescheiden antwoorden te tellen"""
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
    st.sidebar.markdown("Filter de respondenten:")

    # We maken filters voor de demografische factoren
    # Multiselect is handig: als het leeg is, bedoelen we 'Alles'
    
    # Filter 1: Locatie
    opties_locatie = df['Locatie'].unique()
    keuze_locatie = st.sidebar.multiselect("Woonplaats", opties_locatie, default=opties_locatie)
    
    # Filter 2: Geslacht
    opties_geslacht = df['Geslacht'].unique()
    keuze_geslacht = st.sidebar.multiselect("Geslacht", opties_geslacht, default=opties_geslacht)

    # Filter 3: Opleiding
    opties_opleiding = df['Opleiding'].unique()
    keuze_opleiding = st.sidebar.multiselect("Opleiding", opties_opleiding, default=opties_opleiding)
    
    # Filter 4: Leeftijd (Slider)
    min_leeftijd = int(df['Leeftijd'].min())
    max_leeftijd = int(df['Leeftijd'].max())
    keuze_leeftijd = st.sidebar.slider("Leeftijd", min_leeftijd, max_leeftijd, (min_leeftijd, max_leeftijd))

    # --- FILTER TOEPASSEN ---
    df_filtered = df[
        (df['Locatie'].isin(keuze_locatie)) &
        (df['Geslacht'].isin(keuze_geslacht)) &
        (df['Opleiding'].isin(keuze_opleiding)) &
        (df['Leeftijd'] >= keuze_leeftijd[0]) &
        (df['Leeftijd'] <= keuze_leeftijd[1])
    ]

    # --- 5. HOOFDPAGINA ---
    st.title("📊 Brabantse Jongeren Dashboard")
    st.markdown(f"**Aantal respondenten na filter:** {len(df_filtered)} van de {len(df)}")
    
    # Waarschuwing als er te weinig data overblijft
    if len(df_filtered) < 3:
        st.warning("⚠️ Let op: Je hebt erg ver doorgefilterd. De grafieken kunnen er gek uitzien.")

    # TABBLADEN MAKEN
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Demografie", 
        "📢 Thema's & Zorgen", 
        "🚀 Deelname & Motivatie", 
        "📱 Communicatie",
        "📋 Ruwe Data"
    ])

    # --- TAB 1: DEMOGRAFIE ---
    with tab1:
        st.header("Wie zijn deze jongeren?")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Verdeling Stad/Dorp")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Locatie', palette='viridis', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
            
        with col2:
            st.subheader("Opleidingsniveau")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, y='Opleiding', palette='rocket', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Leeftijdsverdeling")
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['Leeftijd'], bins=10, kde=True, color='skyblue', ax=ax)
            st.pyplot(fig)
        
        with col4:
            st.subheader("Geslacht")
            fig, ax = plt.subplots()
            counts = df_filtered['Geslacht'].value_counts()
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
            st.pyplot(fig)

    # --- TAB 2: THEMA'S ---
    with tab2:
        st.header("Waar liggen ze wakker van?")
        
        # Data splitsen
        top_themas = split_en_tel(df_filtered['Themas']).head(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_themas.values, y=top_themas.index, palette='Reds_r', ax=ax)
        ax.set_xlabel("Aantal keer genoemd")
        ax.bar_label(ax.containers[0])
        st.pyplot(fig)
        
        st.markdown("**Interpretatie:** Dit zijn de onderwerpen die het vaakst zijn aangevinkt door de geselecteerde groep.")

    # --- TAB 3: MOTIVATIE ---
    with tab3:
        st.header("Hoe krijgen we ze mee?")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Bereidheid tot deelname")
            fig, ax = plt.subplots()
            # Volgorde vastzetten voor duidelijkheid
            volgorde = ['Ja', 'Misschien', 'Nee']
            sns.countplot(data=df_filtered, x='Deelname', order=[x for x in volgorde if x in df_filtered['Deelname'].unique()], palette='Set2', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
            
        with c2:
            st.subheader("Top Motivatoren")
            top_motivatie = split_en_tel(df_filtered['Motivatie_Combined']).head(10)
            fig, ax = plt.subplots()
            sns.barplot(x=top_motivatie.values, y=top_motivatie.index, palette='Greens_r', ax=ax)
            ax.set_xlabel("Stemmen")
            st.pyplot(fig)

    # --- TAB 4: COMMUNICATIE ---
    with tab4:
        st.header("Via welk kanaal?")
        
        top_kanalen = split_en_tel(df_filtered['Kanalen'])
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top_kanalen.values, y=top_kanalen.index, palette='Blues_r', ax=ax)
        ax.bar_label(ax.containers[0])
        st.pyplot(fig)

    # --- TAB 5: DATA ---
    with tab5:
        st.header("Alle data inzien")
        st.dataframe(df_filtered)

else:
    st.warning("Geen data geladen. Staat 'data.csv' in de map?")