import streamlit as st
import folium
from streamlit_folium import st_folium
import swisseph as swe
from datetime import datetime
from geopy.geocoders import Nominatim
import urllib.parse
import random
import openai

# --- 1. CONFIGURAZIONE & BLINDATURA LEGALE ---
st.set_page_config(page_title="AstroCarto Pro", layout="wide", page_icon="🌍")

# Footer Legale e ToS (Blindatura contro il furto d'idea)
legal_footer = """
<style>
.footer { position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 10px; color: gray; background: rgba(255,255,255,0.1); }
</style>
<div class="footer">
© 2026 AstroCarto Pro. Proprietà Intellettuale Riservata. È vietata la riproduzione del codice, dello storytelling e l'uso commerciale non autorizzato.
Reverse engineering e scraping sono monitorati e perseguiti legalmente.
</div>
"""

# --- 2. DIZIONARI TRADUZIONI E STORYTELLING ---
TRAD = {
    "EN": {
        "hero_title": "🌍 AstroCarto Pro",
        "hero_subtitle": "Your global destiny, calculated by the stars.",
        "install_text": "📲 Add to Home Screen for daily luck tracking.",
        "share_msg": "Check out where your stars shine! 🌍✨ ",
        "disclaimer": "FOR ENTERTAINMENT ONLY. No refunds for instant digital content. Data: NASA JPL.",
        "name_label": "Full Name",
        "mail_label": "Your Email",
        "btn_free": "Start Your Journey",
        "city_label": "Birth City",
        "date_label": "Birth Date",
        "pro_label": "Unlock PRO Transits",
        "buy_btn": "Get PRO Access - $9.99/mo",
        "oracle_btn": "Generate Premium AI Report ($49)",
        "oracle_title": "🔮 Ask the Oracle",
        "success_pro": "✅ PRO Mode Active.",
        "story_title": "✨ History is written in the stars"
    },
    "IT": {
        "hero_title": "🌍 AstroCarto Pro",
        "hero_subtitle": "Il tuo destino globale, calcolato dalle stelle.",
        "install_text": "📲 Installa sulla Home per monitorare la tua fortuna.",
        "share_msg": "Scopri dove brillano le tue stelle! 🌍✨ ",
        "disclaimer": "SOLO PER INTRATTENIMENTO. Rinuncia al recesso per contenuti digitali istantanei. Dati: NASA JPL.",
        "name_label": "Nome Completo",
        "mail_label": "La tua Email",
        "btn_free": "Inizia il Viaggio",
        "city_label": "Città di Nascita",
        "date_label": "Data di Nascita",
        "pro_label": "Sblocca Transiti PRO",
        "buy_btn": "Attiva PRO - 9.99€/mese",
        "oracle_btn": "Genera Report AI Premium (49€)",
        "oracle_title": "🔮 Chiedi all'Oracolo",
        "success_pro": "✅ Modalità PRO Attiva.",
        "story_title": "✨ La storia è scritta nelle stelle"
    },
    "ES": {
        "hero_title": "🌍 AstroCarto Pro",
        "hero_subtitle": "Tu destino global, calculado por las estrellas.",
        "install_text": "📲 Añadir a inicio para seguir tu suerte.",
        "share_msg": "¡Mira dónde brillan tus estrellas! 🌍✨ ",
        "disclaimer": "SOLO ENTRETENIMIENTO. Sin devoluciones en contenido digital. Datos: NASA JPL.",
        "name_label": "Nombre Completo",
        "mail_label": "Tu Email",
        "btn_free": "Empezar",
        "city_label": "Ciudad de Nacimiento",
        "date_label": "Fecha de Nacimiento",
        "pro_label": "Tránsitos PRO",
        "buy_btn": "Activar PRO - $9.99/mes",
        "oracle_btn": "Generar Informe AI Premium ($49)",
        "oracle_title": "🔮 Consulta al Oráculo",
        "success_pro": "✅ Modo PRO Activo.",
        "story_title": "✨ La historia está escrita en las estrellas"
    }
}

STORIES_DATA = {
    "IT": [
        {"name": "Principessa Diana", "hook": "Il Monito di Parigi", "story": "Parigi sedeva sull'incrocio Marte-Urano: zona di massimo rischio fisico.", "source": "Dati: 1 Luglio 1961, Astro-Databank (AA).", "icon": "⚠️"},
        {"name": "Steve Jobs", "hook": "Visione in India", "story": "Il suo viaggio in India lo pose sulla linea Sole-MC, accendendo la leadership di Apple.", "source": "Dati: 24 Febbraio 1955, Astro-Databank (AA).", "icon": "🚀"},
        {"name": "J.K. Rowling", "hook": "Dalle Stalle alle Stelle", "story": "Si trasferì a Londra sulla linea Giove-AS poco prima di scrivere Harry Potter.", "source": "Dati: 31 Luglio 1965, Astro-Databank (A).", "icon": "💰"}
    ]
}

# --- 3. LOGICA DI CALCOLO E AI ---
geolocator = Nominatim(user_agent="astro_final_app")

def get_live_stats():
    base = 1420
    diff = (datetime.now() - datetime(2025, 1, 1)).total_seconds() // 60
    return int(base + (diff * 0.12)), random.randint(12, 48)

def get_planet_lon(p_id, jd):
    res, _ = swe.calc_ut(jd, p_id)
    gst = swe.sidtime(jd) * 15
    lon = (res[0] - gst) % 360
    return lon if lon <= 180 else lon - 360

def chiedi_all_oracolo(nome, dati, domanda):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    prompt = f"Utente: {nome}. Dati Astro: {dati}. Domanda: {domanda}. Fornisci un report professionale."
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Sei l'Oracolo AstroCartografico."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- 4. INTERFACCIA UTENTE ---
if 'status' not in st.session_state: st.session_state.status = 'ANONIMO'

lang = st.sidebar.selectbox("🌐 Lingua/Language/Idioma", ["IT", "EN", "ES"])
t = TRAD[lang]

if st.session_state.status == 'ANONIMO':
    st.title(t["hero_title"])
    st.subheader(t["hero_subtitle"])
    
    m_total, u_online = get_live_stats()
    c1, c2 = st.columns(2); c1.metric("Maps Generated", f"{m_total:,}"); c2.metric("Users Online", u_online)
    
    st.divider()
    st.subheader(t["story_title"])
    # Mostriamo lo storytelling (default IT per brevità nel template, ma dinamico)
    for item in STORIES_DATA["IT"]:
        with st.expander(f"{item['icon']} {item['name']} - {item['hook']}"):
            st.write(item['story'])
            st.caption(item['source'])
    
    st.divider()
    with st.form("lead"):
        nome = st.text_input(t["name_label"])
        email = st.text_input(t["mail_label"])
        if st.form_submit_button(t["btn_free"]):
            if email and nome:
                st.session_state.status, st.session_state.nome = 'FREE', nome
                st.rerun()

else:
    # APP CORE
    with st.sidebar:
        st.header(f"Ciao, {st.session_state.nome}!")
        citta = st.text_input(t["city_label"], "Rome")
        data = st.date_input(t["date_label"], datetime(1990, 1, 1))
        
        st.divider()
        is_pro = st.toggle(t["pro_label"], value=(st.session_state.status == 'PRO'))
        st.session_state.status = 'PRO' if is_pro else 'FREE'
        
        if st.session_state.status == 'FREE':
            st.link_button(t["buy_btn"], "https://buy.stripe.com/tuo_link_sub")

    # MAPPA
    try:
        loc = geolocator.geocode(citta)
        if loc:
            m = folium.Map(location=[loc.latitude, loc.longitude], zoom_start=2, tiles="CartoDB dark_matter")
            jd_n = swe.julday(data.year, data.month, data.day, 12)
            planets = {"Sun": 0, "Venus": 3, "Jupiter": 5, "Mars": 4}
            colors = {"Sun": "gold", "Venus": "#FF69B4", "Jupiter": "#4169E1", "Mars": "red"}
            
            dati_per_ai = ""
            for p, p_id in planets.items():
                ln = get_planet_lon(p_id, jd_n)
                folium.PolyLine([[-90, ln], [90, ln]], color=colors[p], weight=2, tooltip=p).add_to(m)
                dati_per_ai += f"{p} natal lon: {ln}; "
                if st.session_state.status == 'PRO':
                    lt = get_planet_lon(p_id, swe.julday(datetime.now().year, datetime.now().month, datetime.now().day, 12))
                    folium.PolyLine([[-90, lt], [90, lt]], color=colors[p], weight=2, dash_array='5,5').add_to(m)
            
            st_folium(m, width="100%", height=500)
            
            # SEZIONE ORACOLO AI (Upsell 50€)
            if st.session_state.status == 'PRO':
                st.divider()
                st.subheader(t["oracle_title"])
                domanda = st.text_area("Cosa vuoi sapere su questa posizione?")
                if st.button(t["oracle_btn"]):
                    # Qui idealmente verifichi il pagamento dell'acquisto singolo
                    st.link_button("Acquista Report Premium (49€)", "https://buy.stripe.com/tuo_link_49euro")
                    # Logica AI:
                    # responso = chiedi_all_oracolo(st.session_state.nome, dati_per_ai, domanda)
                    # st.markdown(responso)
    except Exception as e:
        st.error("Errore nel caricamento.")

st.markdown(legal_footer, unsafe_allow_html=True)
st.caption(t["disclaimer"])
