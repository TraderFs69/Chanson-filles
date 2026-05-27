import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items
import streamlit.components.v1 as components
import base64
import time

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(
    page_title="Walk-Up Songs",
    layout="wide"
)

EXCEL_FILE = "Chanson Filles.xlsx"

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():

    df = pd.read_excel(EXCEL_FILE)

    # Nettoyage colonnes
    df.columns = df.columns.str.strip()

    # Uniformiser noms colonnes
    df = df.rename(columns={
        "nom": "Nom",
        "NOM": "Nom",
        "fichier": "Fichier",
        "FICHIER": "Fichier"
    })

    return df

df = load_data()

# ==================================================
# SESSION STATE
# ==================================================
if "lineup" not in st.session_state:
    st.session_state.lineup = []

if "current_player" not in st.session_state:
    st.session_state.current_player = None

if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

if "stop_audio" not in st.session_state:
    st.session_state.stop_audio = False

# ==================================================
# STYLE
# ==================================================
st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 20px;
}

.section-title {
    font-size: 30px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
}

.player-card {
    background-color: #111111;
    color: white;
    padding: 15px;
    border-radius: 12px;
    border: 2px solid #ff8c00;
    margin-bottom: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}

.stButton button {
    width: 100%;
    height: 55px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown(
    '<div class="main-title">⚾ WALK-UP SONGS ⚾</div>',
    unsafe_allow_html=True
)

# ==================================================
# STOP BUTTON
# ==================================================
stop_col1, stop_col2, stop_col3 = st.columns([1,2,1])

with stop_col2:

    if st.button("🛑 STOP SONG"):

        st.session_state.stop_audio = True

        st.session_state.audio_key = time.time()

        st.rerun()

# ==================================================
# AUDIO SECTION
# ==================================================
if st.session_state.current_player is not None:

    row = df[
        df["Nom"]
        == st.session_state.current_player
    ].iloc[0]

    st.markdown(f"""
    ## 🎵 Lecture en cours
    ### {row['Nom']}
    """)

    audio_path = f"songs/{row['Fichier']}"

    try:

        with open(audio_path, "rb") as audio_file:

            audio_bytes = audio_file.read()

        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode()

        unique_id = str(time.time()).replace(".", "")

        # ==================================================
        # STOP AUDIO
        # ==================================================
        if st.session_state.stop_audio:

            stop_html = f"""
            <html>
            <body>

            <script>

                const audios = document.getElementsByTagName('audio');

                for (let i = 0; i < audios.length; i++) {{

                    audios[i].pause();

                    audios[i].currentTime = 0;
                }}

            </script>

            </body>
            </html>
            """

            components.html(
                stop_html,
                height=0,
                key=unique_id
            )

            st.session_state.stop_audio = False

        # ==================================================
        # PLAY AUDIO
        # ==================================================
        else:

            audio_html = f"""
            <html>
            <body>

            <audio
                id="audio_{unique_id}"
                autoplay
            >
                <source
                    src="data:audio/mp3;base64,{audio_base64}#t={unique_id}"
                    type="audio/mp3"
                >
            </audio>

            <script>

                const audio = document.getElementById(
                    "audio_{unique_id}"
                );

                audio.load();

                const playPromise = audio.play();

                if (playPromise !== undefined) {{

                    playPromise
                        .then(() => {{
                            console.log("playing");
                        }})
                        .catch(error => {{
                            console.log(error);
                        }});
                }}

            </script>

            </body>
            </html>
            """

            components.html(
                audio_html,
                height=0,
                key=unique_id
            )

    except Exception as e:

        st.error(
            f"Impossible de lire : {audio_path}"
        )

        st.write(e)

st.divider()

# ==================================================
# AVAILABLE PLAYERS
# ==================================================
st.markdown(
    '<div class="section-title">Joueuses disponibles</div>',
    unsafe_allow_html=True
)

available_players = [
    name for name in df["Nom"].tolist()
    if name not in st.session_state.lineup
]

cols = st.columns(4)

for i, player_name in enumerate(available_players):

    with cols[i % 4]:

        if st.button(
            f"➕ {player_name}",
            key=f"add_{player_name}"
        ):

            st.session_state.lineup.append(player_name)

            st.rerun()

st.divider()

# ==================================================
# LINEUP
# ==================================================
st.markdown(
    '<div class="section-title">Ordre au bâton</div>',
    unsafe_allow_html=True
)

sorted_lineup = sort_items(
    st.session_state.lineup,
    direction="vertical",
    key="lineup_sort"
)

st.session_state.lineup = sorted_lineup

for i, player_name in enumerate(
    st.session_state.lineup
):

    row = df[
        df["Nom"] == player_name
    ].iloc[0]

    cols = st.columns([1,5,2,2])

    # ORDER
    with cols[0]:

        st.markdown(f"## #{i+1}")

    # NAME
    with cols[1]:

        st.markdown(f"""
        <div class="player-card">
        {player_name}
        </div>
        """, unsafe_allow_html=True)

    # PLAY
    with cols[2]:

        if st.button(
            "🎵 PLAY",
            key=f"play_{i}"
        ):

            st.session_state.current_player = (
                player_name
            )

            st.session_state.stop_audio = False

            st.session_state.audio_key = time.time()

            st.rerun()

    # REMOVE
    with cols[3]:

        if st.button(
            "❌ REMOVE",
            key=f"remove_{i}"
        ):

            st.session_state.lineup.remove(
                player_name
            )

            st.rerun()

# ==================================================
# SAVE LINEUP
# ==================================================
st.divider()

if st.button("💾 Sauvegarder le lineup"):

    lineup_df = pd.DataFrame({
        "ordre": range(
            1,
            len(st.session_state.lineup) + 1
        ),
        "Nom": st.session_state.lineup
    })

    lineup_df.to_excel(
        "lineup_match.xlsx",
        index=False
    )

    st.success("Lineup sauvegardé.")
