import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from datetime import datetime
import service as service
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Proj, transform
import requests
from PIL import Image

# ========== CHARGEMENT DU CSS EXTERNE ==========
def load_css(file_name):
    """Charge le fichier CSS externe"""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"❌ Fichier CSS '{file_name}' introuvable! Assurez-vous qu'il est dans le même dossier que main.py")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du CSS: {e}")

def get_coordinates(destination):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": destination,
        "format": "json",
        "limit": 1,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            print("Location not found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_pos(lat, lng):
    return lat, lng

def lon_lat_to_utm(lon, lat):
    utm_proj = Proj(init="epsg:2263")
    utm_x, utm_y = transform(Proj(init="epsg:4326"), utm_proj, lon, lat)
    return utm_x, utm_y

shapefile = './shapes/geo_export_84578745-538d-401a-9cb5-34022c705879.shp'
borough_sh = './borough/nybb.shp'

def get_precinct_and_borough(lat, lon):
    precinct_gdf = gpd.read_file(shapefile)
    borough_gdf = gpd.read_file(borough_sh)
    point = Point(lon, lat)
    point2 = Point(lon_lat_to_utm(lon, lat))
    precinct = None
    borough = None
    for _, row in precinct_gdf.iterrows():
        if row['geometry'].contains(point):
            precinct = row['precinct']
    for _, row in borough_gdf.iterrows():
        if row['geometry'].contains(point2):
            borough = row['BoroName']
            break
    return precinct, borough

def generate_base_map(default_location=[40.704467, -73.892246], default_zoom_start=11, min_zoom=11, max_zoom=15):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start,
                          min_zoom=min_zoom, max_zoom=max_zoom, max_bounds=True, min_lat=40.47739894,
                          min_lon=-74.25909008, max_lat=40.91617849, max_lon=-73.70018092)
    return base_map

def get_user_information():
    """Function to collect all user information within a form"""
    with st.form(key='user_info_form'):
        # Collecting gender with radio buttons
        gender = st.radio("Gender 👤", ["Male", "Female"])

        # Collecting race with a selectbox
        race = st.selectbox("Race 🌍", ['WHITE', 'WHITE HISPANIC', 'BLACK', 'ASIAN / PACIFIC ISLANDER', 
                                       'BLACK HISPANIC', 'AMERICAN INDIAN/ALASKAN NATIVE', 'OTHER'])

        # Collecting age with a slider
        age = st.number_input(
            "Age 🧑:",
            min_value=0,
            max_value=120,
            step=1,
            value=25
        )

        # Collecting date using date input
        date = st.date_input("Date 🗓️:", datetime.now())

        # Valeur par défaut neutre (00:00)
        default_time = datetime.strptime("00:00", "%H:%M").time()

        # Widget pour entrer l'heure manuellement
        time = st.time_input("Entrez l'heure 🕒 :", value=default_time)

        # Extraire l'heure et les minutes
        hour = time.hour
        minute = time.minute

        
        
        # Collecting place with radio buttons
        place = st.radio("Place 📍", ("In park", "In public housing", "In station"))

        # Submit button for the form
        submit_button = st.form_submit_button("Submit 📝")
    
    return gender, race, age, date, hour, place, submit_button

# Streamlit page config
st.set_page_config(
    page_title="NYC Crime Prediction 🚔",
    page_icon="🌍",
    layout="wide",  
    initial_sidebar_state="expanded",
)

# SOLUTION ALTERNATIVE : CSS intégré directement
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* Background rouge/noir - SANS BANDE BLANCHE */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(217deg, rgba(139,0,0,.8), rgba(139,0,0,0) 70.71%),
                    linear-gradient(127deg, rgba(0,0,0,.8), rgba(0,0,0,0) 70.71%),
                    linear-gradient(336deg, rgba(255,0,0,.8), rgba(255,0,0,0) 70.71%) !important;
        background-color: #0a0000 !important;
    }
    
    /* Supprimer le header blanc */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #0a0000 !important;
        background: #0a0000 !important;
    }
    
    /* Toolbar en haut */
    [data-testid="stToolbar"] {
        background-color: rgba(10, 0, 0, 0.9) !important;
        background: rgba(10, 0, 0, 0.9) !important;
    }
    
    /* Conteneur principal */
    .main .block-container, [data-testid="stMainBlockContainer"] {
        background: rgba(0, 0, 0, 0.6) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        box-shadow: 0 0 60px rgba(255, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 0, 0, 0.3) !important;
    }
    
    /* Titre principal */
    h1 {
        font-family: 'Creepster', cursive !important;
        color: #ff0000 !important;
        font-size: 4rem !important;
        text-shadow: 
        0 0 5px rgba(255, 0, 0, 0.5),
        0 0 10px rgba(255, 0, 0, 0.4),
        0 0 15px rgba(255, 0, 0, 0.3),
        0 0 20px rgba(255, 0, 0, 0.2) !important;
        text-align: center !important;
        animation: glowPulse 2s ease-in-out infinite !important;
        text-transform: uppercase !important;
        letter-spacing: 8px !important;
    }
    
    @keyframes glowPulse {
        0%, 100% { text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000, 0 0 30px #ff0000; }
        50% { text-shadow: 0 0 20px #ff0000, 0 0 40px #ff0000, 0 0 60px #8b0000, 0 0 80px #8b0000; }
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"], [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0000 0%, #000000 100%) !important;
        border-right: 5px solid #ff0000 !important;
    }
    
    section[data-testid="stSidebar"]::before,
    [data-testid="stSidebar"]::before {
        content: "⚠️ CRIME SCENE - DO NOT CROSS ⚠️";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        background: repeating-linear-gradient(45deg, #ffcc00, #ffcc00 20px, #000000 20px, #000000 40px);
        color: #fff;
        text-align: center;
        padding: 5px 5px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        letter-spacing: 3px;
        z-index: 1000;
    }
    
    section[data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 70px !important;
    }
    
    /* Boutons */
    .stButton > button, button[kind="primary"] {
        background: linear-gradient(135deg, #ff0000 0%, #8b0000 100%) !important;
        color: white !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        border: 3px solid #ff0000 !important;
        border-radius: 12px !important;
        padding: 15px 40px !important;
        font-size: 1.3rem !important;
        text-transform: uppercase !important;
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.7) !important;
        animation: buttonGlow 2s ease-in-out infinite !important;
    }
    
    @keyframes buttonGlow {
        0%, 100% { box-shadow: 0 0 30px rgba(255, 0, 0, 0.7); }
        50% { box-shadow: 0 0 50px rgba(255, 0, 0, 1); }
    }
    
    .stButton > button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 0 50px rgba(255, 0, 0, 1) !important;
    }
            
            
    
    /* Formulaire */
    form[data-testid="stForm"], [data-testid="stForm"] {
        background: linear-gradient(135deg, rgba(20, 0, 0, 0.95), rgba(40, 0, 0, 0.95)) !important;
        border: 3px solid #ff0000 !important;
        border-radius: 20px !important;
        padding: 35px !important;
        box-shadow: 0 0 50px rgba(255, 0, 0, 0.5) !important;
        position: relative !important;
        animation: formPulse 3s ease-in-out infinite !important;
    }
    
    @keyframes formPulse {
        0%, 100% { box-shadow: 0 0 50px rgba(255, 0, 0, 0.5); }
        50% { box-shadow: 0 0 70px rgba(255, 0, 0, 0.7); }
    }
    
    form[data-testid="stForm"]::before,
    [data-testid="stForm"]::before {
        content: "📋Enter your information📋";
        position: absolute;
        top: -20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #8b0000, #ff0000);
        color: white;
        padding: 8px 25px;
        border-radius: 20px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.8);
        border: 2px solid #ffcc00;
    }
    
    /* Inputs */
    input, select {
        background: rgba(30, 0, 0, 0.9) !important;
        color: #ff6666 !important;
        border: 2px solid #8b0000 !important;
        border-radius: 10px !important;
        font-family: 'Rajdhani', sans-serif !important;
        padding: 12px 15px !important;
    }
    
    input:focus, select:focus {
        border-color: #ff0000 !important;
        box-shadow: 0 0 25px rgba(255, 0, 0, 0.7) !important;
    }
    
    /* Labels */
    label {
        color: #ffcc00 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px rgba(255, 204, 0, 0.5) !important;
    }
    
    /* Texte */
    p, li, .stMarkdown {
        font-family: 'Rajdhani', sans-serif !important;
        color: #f0f0f0 !important;
        font-size: 1.2rem !important;
    }
    
    /* Radio buttons */
    div[role="radiogroup"] {
        background: linear-gradient(135deg, rgba(30, 0, 0, 0.7), rgba(50, 0, 0, 0.7)) !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255, 0, 0, 0.4) !important;
    }
    
    /* Slider */
    .stSlider {
        background: linear-gradient(135deg, rgba(20, 0, 0, 0.6), rgba(40, 0, 0, 0.6)) !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255, 0, 0, 0.3) !important;
    }
    
    /* Alertes */
    .stAlert, div[data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.95), rgba(180, 0, 0, 0.95)) !important;
        border: 3px solid #ff0000 !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        padding: 20px !important;
        box-shadow: 0 0 40px rgba(255, 0, 0, 0.8) !important;
        animation: alertGlow 2s ease-in-out infinite !important;
    }
    
    @keyframes alertGlow {
        0%, 100% { box-shadow: 0 0 40px rgba(255, 0, 0, 0.8); }
        50% { box-shadow: 0 0 60px rgba(255, 0, 0, 1); }
    }
    
    /* Carte - OPTIONS EN NOIR ET CENTRAGE */
    iframe {
        border: 4px solid #ff0000 !important;
        border-radius: 15px !important;
        box-shadow: 0 0 50px rgba(255, 0, 0, 0.6) !important;
        display: block !important;
        margin: 0 auto !important;
    }
    
    /* Conteneur de la carte centré */
    [data-testid="stIFrame"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* Popup de la carte avec texte NOIR */
    .leaflet-popup-content-wrapper {
        background-color: rgba(0, 0, 0, 0.95) !important;
        color: #ff0000 !important;
        border: 2px solid #ff0000 !important;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.8) !important;
    }
    
    .leaflet-popup-content {
        color: #ff6666 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
    }
    
    .leaflet-popup-content b {
        color: #ff0000 !important;
    }
    
    .leaflet-popup-tip {
        background-color: rgba(0, 0, 0, 0.95) !important;
    }
    
    /* Contrôles de zoom en noir */
    .leaflet-control-zoom a {
        background-color: #000000 !important;
        color: #ff0000 !important;
        border: 2px solid #ff0000 !important;
    }
    
    .leaflet-control-zoom a:hover {
        background-color: #ff0000 !important;
        color: #000000 !important;
    }
    
    /* Attributions en noir */
    .leaflet-control-attribution {
        background-color: rgba(0, 0, 0, 0.9) !important;
        color: #ff6666 !important;
        border: 1px solid #ff0000 !important;
    }
    
    .leaflet-control-attribution a {
        color: #ff0000 !important;
    }
    
    /* Zone warning */
    .warning-zone {
        background: repeating-linear-gradient(45deg, rgba(255, 0, 0, 0.15), rgba(255, 0, 0, 0.15) 15px, rgba(0, 0, 0, 0.15) 15px, rgba(0, 0, 0, 0.15) 30px) !important;
        border: 3px dashed #ff0000 !important;
        padding: 25px !important;
        border-radius: 15px !important;
        margin: 30px 0 !important;
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.3) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #000000;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8b0000, #ff0000, #8b0000);
        border-radius: 6px;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
    }
    
</style>
""", unsafe_allow_html=True)

# Sidebar for additional input options or instructions
with st.sidebar:
    image = Image.open(r"D:\NYC_crime_prediction\NYC_Crime_Prediction\application\assets\NYC.jpg") 
    st.image(image, width='stretch')
    st.markdown("# NYC Crime Prediction")
    st.markdown("""
        helps you understand potential risks, plan ahead, and navigate the city with confidence.
    """)

# Main content area
with st.container():
    st.title("NYC Crime Prediction 🚔")

    # Application description centered with icons
    st.markdown("""
        Curious about safety in New York City? NYC Crime Preiction predicts the likelihood of crimes at any location, giving you actionable insights to stay safe and make smarter choices while exploring the city.
        
        ### How it Works:
        1. **Choose your destination**: Click on the interactive map to select  the area you're interested in .
        2. **Enter your details** : Provide your age, gender, race, and the time you plan to be out.
        3. **See your risk** : Get predictions on the types of crimes most likely to occur in that area at that time.

        ### Stay informed. Stay vigilant. Stay safe.
        NYC Crime Prediction  helps you understand potential risks, plan ahead, and navigate the city with confidence.
    """)

# Render the map **outside the form** - CENTRÉ
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    base_map = generate_base_map()
    base_map.add_child(folium.LatLngPopup())
    
    # Add a marker with popup for when the user clicks on the map
    map = st_folium(base_map, height=400, width=None, use_container_width=True)

# Instruction to click on the map
st.markdown("""
<div class="warning-zone">
    <h3 style="margin-top: 0;"> Click on the map to select your location! </h3>
    <p>After selecting a location, fill in the form below to get a prediction about the crime risks in the area.</p>
</div>
""", unsafe_allow_html=True)

# When a location is clicked, get coordinates and display info creatively
if map['last_clicked']:
    lat = map['last_clicked']['lat']
    lon = map['last_clicked']['lng']

    # Get precinct and borough from the selected coordinates
    precinct, borough = get_precinct_and_borough(lat, lon)

    if borough:
        # Create a dynamic popup for coordinates and additional info
        popup_content = f"""
        <b>📍 Selected Coordinates:</b><br>
        <i>Latitude:</i> {lat}<br>
        <i>Longitude:</i> {lon}<br><br>
        <b>Precinct:</b> {precinct} <br>
        <b>Borough:</b> {borough} 🏙️
        """
        
        # Add marker to the map with the popup
        folium.Marker([lat, lon], popup=folium.Popup(popup_content, max_width=300)).add_to(base_map)

        # Display the updated map with marker and popup - CENTRÉ
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st_folium(base_map, height=400, width=None, use_container_width=True)

        # Collect user information after selecting location
        gender, race, age, date, hour, place, submit_button = get_user_information()

        # Trigger the crime prediction once the location is confirmed and the form is submitted
        if submit_button:
            # Check for necessary inputs before prediction
            if lat == '' or lon == '' or precinct is None:
                st.error("Please make sure that you selected a location on the map ")
            else:
                # Call service to create a DataFrame and predict
                X = service.create_df(date, hour, lat, lon, place, age, race, gender, precinct, borough)
                pred, crimes = service.predict(X)  # Predict after inputs are given
                
                # Display the result with a creative touch
                st.markdown(f"Based on the information you provided, you may face a higher risk of a **{pred}**  crime. Stay aware and take the necessary steps to protect yourself. ")
    else:
        st.error("Select a destination in NYC ")