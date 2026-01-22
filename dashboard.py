import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import io

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
def voeg_download_knop_toe(figuur, bestandsnaam="grafiek.png"):
    """
    Deze functie maakt een downloadknop voor een Matplotlib figuur.
    """
    # 1. Maak een tijdelijke opslag in het geheugen
    buf = io.BytesIO()
    
    # 2. Sla de grafiek op in die tijdelijke opslag
    figuur.savefig(buf, format="png", bbox_inches='tight', dpi=300)
    
    # 3. Zet de 'lezer' weer aan het begin van het bestand
    buf.seek(0)
    
    # 4. Maak de knop in Streamlit
    st.download_button(
        label="📥 Download deze grafiek",
        data=buf,
        file_name=bestandsnaam,
        mime="image/png"
    )

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
    
    if not delen:
        return tekst + "Alle respondenten."
    else:
        return tekst + " + ".join(delen) + "."

# ====================================================================
#              🚀 HOOFD PROGRAMMA 🚀
# ====================================================================
df = laad_data()

if df is not None:
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("Stel hier je doelgroep samen:")

    opties_locatie = df['Locatie'].dropna().unique()
    keuze_locatie = st.sidebar.multiselect("Woonplaats", opties_locatie, default=opties_locatie)
    
    opties_geslacht = df['Geslacht'].dropna().unique()
    keuze_geslacht = st.sidebar.multiselect("Geslacht", opties_geslacht, default=opties_geslacht)

    opties_opleiding = df['Opleiding'].dropna().unique()
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
    
    # Filters opslaan voor de tekst
    huidige_filters = {'Locatie': keuze_locatie, 'Geslacht': keuze_geslacht, 'Opleiding': keuze_opleiding}
    beschrijving_tekst = maak_beschrijving(huidige_filters)

    # --- HOOFDPAGINA ---
    st.title(TITEL_DASHBOARD)
    st.markdown(INTRO_TEKST)
    st.markdown("---")

    st.markdown(f"**Huidige selectie:** {len(df_filtered)} respondenten")
    if len(df_filtered) < 3:
        st.warning("⚠️ Let op: Weinig data over. Filters zijn erg streng.")

    # TABBLADEN
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Demografie", 
        "📢 Thema's", 
        "🚀 Motivatie", 
        "📱 Communicatie",
        "⚖️ Vergelijken", 
        "📋 Ruwe Data"
    ])

    # Styling
    sns.set_style("darkgrid")

    # --- TAB 1: DEMOGRAFIE ---
    with tab1:
        st.header("Wie zijn deze jongeren?")
        st.info(f"ℹ️ {beschrijving_tekst}")
        
        # RIJ 1: Locatie & Opleiding
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Woonplaats")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Locatie', palette='viridis', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
            # --- HIER PLAK JE DE KNOP ---
            (fig, "mijn_mooie_grafiek.png")
            st.caption(f"Verdeling tussen Stad en Dorp binnen jouw selectie.")
            
        with col2:
            st.subheader("Opleidingsniveau")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, y='Opleiding', palette='rocket', ax=ax)
            ax.bar_label(ax.containers[0])
            st.pyplot(fig)
            (fig, "mijn_mooie_grafiek.png")
            st.caption(f"Het opleidingsniveau van de geselecteerde groep.")
            
        # RIJ 2: Leeftijd & Geslacht
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Leeftijdsverdeling")
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['Leeftijd'], bins=10, kde=True, color='skyblue', ax=ax)
            st.pyplot(fig)
            (fig, "mijn_mooie_grafiek.png")
            st.caption("De leeftijdsopbouw van deze groep.")
        
        with col4:
            st.subheader("Geslacht")
            fig, ax = plt.subplots()
            counts = df_filtered['Geslacht'].value_counts()
            if len(counts) > 0:
                ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
            st.pyplot(fig)
            (fig, "mijn_mooie_grafiek.png")
            st.caption("Verdeling man/vrouw/anders.")

    # --- TAB 2: THEMA'S ---
    with tab2:
        st.header("Waar liggen ze wakker van?")
        st.info(f"ℹ️ {beschrijving_tekst} - Dit zijn de thema's die zij belangrijk vinden.")
        
        top_themas = split_en_tel(df_filtered['Themas']).head(15)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_themas.values, y=top_themas.index, palette='Reds_r', ax=ax)
        ax.set_xlabel("Aantal stemmen")
        st.pyplot(fig)
        (fig, "mijn_mooie_grafiek.png")
        st.caption("Top 15 meest gekozen thema's door deze groep.")

    # --- TAB 3: MOTIVATIE ---
    with tab3:
        st.header("Hoe krijgen we ze mee?")
        st.info(f"ℹ️ Inzichten in de motivatie van: {', '.join(keuze_geslacht) if len(keuze_geslacht) < 3 and len(keuze_geslacht) > 0 else 'de geselecteerde groep'}.")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Bereidheid tot deelname")
            fig, ax = plt.subplots()
            sns.countplot(data=df_filtered, x='Deelname', palette='Set2', ax=ax)
            st.pyplot(fig)
            (fig, "mijn_mooie_grafiek.png")
            st.caption("Willen ze meedoen aan toekomstig onderzoek?")
            
        with c2:
            st.subheader("Top Motivatoren")
            top_motivatie = split_en_tel(df_filtered['Motivatie_Combined']).head(10)
            fig, ax = plt.subplots()
            sns.barplot(x=top_motivatie.values, y=top_motivatie.index, palette='Greens_r', ax=ax)
            st.pyplot(fig)
            (fig, "mijn_mooie_grafiek.png")
            st.caption("Wat trekt hen over de streep?")

    # --- TAB 4: COMMUNICATIE ---
    with tab4:
        st.header("Via welk kanaal?")
        st.info(f"ℹ️ {beschrijving_tekst} - Waar zijn ze online te vinden?")
        
        top_kanalen = split_en_tel(df_filtered['Kanalen'])
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top_kanalen.values, y=top_kanalen.index, palette='Blues_r', ax=ax)
        st.pyplot(fig)
        (fig, "mijn_mooie_grafiek.png")
        st.caption("De populairste mediakanalen voor deze doelgroep.")

    # --- TAB 5: VERGELIJKEN (VERNIEUWD) ---
    with tab5:
        st.header("⚖️ Vergelijk Groepen")
        st.markdown("""
        Hier kun je zelf onderzoek doen! Kies een onderwerp en kijk hoe verschillende groepen (bijv. Stad vs Dorp) daarover denken.
        """)
        
        # Keuze opties
        col_opties1, col_opties2, col_opties3 = st.columns(3)
        
        with col_opties1:
            onderwerp = st.selectbox("1. Wat wil je analyseren?", 
                                     ["Thema's (Zorgen)", "Communicatie Kanalen", "Motivatie om mee te doen"])
        
        with col_opties2:
            vergelijk_op = st.selectbox("2. Vergelijk op basis van:", 
                                        ["Locatie", "Geslacht", "Opleiding", "Deelname"])
            
        with col_opties3:
            weergave = st.radio("3. Kies weergave:", ["Aantallen", "Percentages"], horizontal=True)

        kolom_map = {
            "Thema's (Zorgen)": 'Themas',
            "Communicatie Kanalen": 'Kanalen',
            "Motivatie om mee te doen": 'Motivatie_Combined'
        }
        gekozen_data_kolom = kolom_map[onderwerp]
        
        # Stap A: Data splitsen
        vergelijk_df = bereid_data_voor_vergelijking(df_filtered, gekozen_data_kolom, vergelijk_op)
        
        if not vergelijk_df.empty:
            
            # Stap B: Berekenen Aantallen
            # We groeperen op 'Groep' (bijv Stad) en 'Item' (bijv Veiligheid) en tellen hoe vaak het voorkomt
            tel_df = vergelijk_df.groupby(['Groep', 'Item']).size().reset_index(name='Aantal')
            
            # Stap C: Berekenen Percentages
            # We moeten weten hoeveel mensen er TOTAAL in die groep zitten in de huidige selectie
            groep_totalen = df_filtered[vergelijk_op].value_counts()
            
            # Functie om percentage te berekenen
            def get_percentage(row):
                totaal_in_deze_groep = groep_totalen.get(row['Groep'], 1) # , 1 voorkomt delen door nul
                return (row['Aantal'] / totaal_in_deze_groep) * 100
            
            tel_df['Percentage'] = tel_df.apply(get_percentage, axis=1)

            # Stap D: Alleen de top 10 items tonen (anders wordt de grafiek te druk)
            top_items = vergelijk_df['Item'].value_counts().head(10).index
            plot_df = tel_df[tel_df['Item'].isin(top_items)]
            
            st.subheader(f"Verschil in '{onderwerp}' per '{vergelijk_op}'")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if weergave == "Aantallen":
                sns.barplot(data=plot_df, y='Item', x='Aantal', hue='Groep', palette='tab10', ax=ax, order=top_items)
                ax.set_xlabel("Aantal keer genoemd")
            else:
                sns.barplot(data=plot_df, y='Item', x='Percentage', hue='Groep', palette='tab10', ax=ax, order=top_items)
                ax.set_xlabel("Percentage van de groep (%)")
                ax.set_xlim(0, 100) # Percentage loopt tot 100
            
            st.pyplot(fig)
            (fig, "mijn_mooie_grafiek.png")
            if weergave == "Percentages":
                st.info(f"💡 **Tip:** Je kijkt nu naar percentages. Voorbeeld: Als de balk bij 'Stad' op 50% staat, betekent dit dat de helft van alle jongeren uit de stad dit heeft aangevinkt.")
            else:
                 st.info(f"💡 In deze grafiek zie je de absolute aantallen. Let op: als de ene groep veel groter is dan de andere (bijv. veel meer mensen uit een dorp), zullen die balkjes vanzelf hoger zijn.")

        else:
            st.warning("Niet genoeg data om te vergelijken met deze filters.")

    # --- TAB 6: DATA ---
    with tab6:
        st.header("Ruwe Data")
        st.dataframe(df_filtered)

else:
    st.warning("Geen data geladen. Staat 'data.csv' in de map?")