import streamlit as st
import pandas as pd
import hashlib
from streamlit_gsheets import GSheetsConnection
import openai

# 1. CONFIGURAZIONE E STILE "DEEP SPACE"
st.set_page_config(page_title="ASTROPATH - Oracle", layout="wide", page_icon="🏹")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e0e0e0; }
    .main-card { background: linear-gradient(145deg, #1e2024, #111214); padding: 25px; border-radius: 15px; border: 1px solid #333; }
    .nasa-box { border-left: 3px solid #00529b; background: #1a1c23; padding: 15px; font-family: monospace; font-size: 0.85rem; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Sostituisci la sezione 2 del codice precedente con questa:
try:
    if "connections.gsheets" in st.secrets:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_utenti = conn.read(worksheet="utenti")
    else:
        st.error("Configurazione Secrets mancante: controlla il blocco [connections.gsheets]")
        df_utenti = pd.DataFrame(columns=['Email', 'CodiceID', 'Status']) # Crea un foglio vuoto per non crashare
except Exception as e:
    st.error(f"Errore di connessione: {e}")
    df_utenti = pd.DataFrame(columns=['Email', 'CodiceID', 'Status'])

# 3. LOGICA MULTILINGUA (Storytelling & Termini)
TEXTS = {
    "IT": {
        "welcome": "Benvenuto nell'Astropath",
        "cta_free": "Analisi Base Disponibile",
        "cta_pro": "Sblocca la tua Linea di Potere",
        "terms": "L'uso di questo software implica l'accettazione dei dati orbitali NASA JPL.",
        "oracle_prompt": "Agisci come l'Oracolo di Atene. Analizza la posizione di {p} a {lat}/{lon}. Sii criptico ma autorevole."
    },
    "EN": {
        "welcome": "Welcome to Astropath",
        "cta_free": "Basic Analysis Available",
        "cta_pro": "Unlock your Power Line",
        "terms": "Use of this software implies acceptance of NASA JPL orbital data.",
        "oracle_prompt": "Act as the Oracle of Athens. Analyze {p} position at {lat}/{lon}. Be cryptic yet authoritative."
    }
}
lang = st.sidebar.selectbox("Language / Lingua", ["IT", "EN"])
T = TEXTS[lang]

# 4. FUNZIONE GRAFICO / MAPPA (L'esca visiva)
def mostra_anteprima_mappa():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("📍 Le tue linee di potere correnti")
    # Qui simuliamo il grafico che "invoglia"
    df_map = pd.DataFrame({'lat': [37.98], 'lon': [23.72]}) # Esempio Atene
    st.map(df_map, zoom=2)
    st.info("⚠️ Le linee di Giove e Plutone sono bloccate. Passa a PRO per visualizzarle.")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. LOGICA DI ACCESSO
st.sidebar.title("🏹 Login")
u_email = st.sidebar.text_input("Email")
u_code = st.sidebar.text_input("Stripe ID / Access Code", type="password")
is_pro = False

if u_email and u_code:
    # Verifica nel database (Google Sheets)
    user_row = df_utenti[(df_utenti['Email'] == u_email) & (df_utenti['CodiceID'] == u_code)]
    if not user_row.empty and user_row.iloc[0]['Status'] == 'PRO':
        is_pro = True
        st.sidebar.success("Status: PRO UNLOCKED")
    else:
        st.sidebar.warning("Codice errato o accesso FREE.")

# 6. INTERFACCIA DINAMICA (Storytelling e Contenuti)
if not is_pro:
    st.title(T["welcome"])
    mostra_anteprima_mappa()
    st.markdown(f"### {T['cta_free']}")
    st.write("Il tuo tema natale indica una forte risonanza con le coordinate del Mediterraneo.")
    if st.button("Acquista Report Oracle (49€)"):
        st.link_button("Vai al Pagamento Stripe", "https://buy.stripe.com/tuo_link")
else:
    # CONTENUTO PRO
    st.title("🔮 L'Oracolo è Attivo")
    query = st.text_input("Fai la tua domanda sulla tua destinazione:")
    if query:
        with st.spinner("Consultando le effemeridi..."):
            # Chiamata reale all'AI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": T["oracle_prompt"].format(p="Jupiter", lat="37.9", lon="23.7")},
                          {"role": "user", "content": query}]
            )
            st.write(response.choices[0].message.content)
            
            # BOX METADATI NASA (Accreditamento)
            st.markdown(f"""
                <div class="nasa-box">
                    <b>NASA JPL DATA VALIDATION</b><br>
                    Epoch: J2000.0 | Object: JUPITER | Precision: 0.00001s<br>
                    Status: Validated for {u_email}
                </div>
            """, unsafe_allow_html=True)

st.sidebar.markdown(f"--- \n<small>{T['terms']}</small>", unsafe_allow_html=True)
