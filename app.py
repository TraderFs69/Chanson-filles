import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items

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

    df.columns = df.columns.str.strip()

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
    height: 60px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
}

[data-testid="stAudio"] {
    margin-top: -10px;
    margin-bottom: 20px;
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
# PLAYER CURRENTLY PLAYING
# ==================================================
if st.session_state.current_player:

    st.success(
        f"🎵 Lecture en cours : {st.session_state.current_player}"
    )

    try:

        row = df[
            df["Nom"] ==
            st.session_state.current_player
        ].iloc[0]

        audio_path = (
            f"songs/{row['Fichier']}"
        )

        with open(
            audio_path,
            "rb"
        ) as audio_file:

            st.audio(
                audio_file.read()
            )

    except Exception as e:

        st.error(
            "Impossible de lire la chanson."
        )

        st.write(e)

    col1, col2 = st.columns(2)

    # STOP
    with col1:

        if st.button(
            "⏹️ STOP",
            use_container_width=True
        ):

            st.session_state.current_player = None

            st.rerun()

    # NEXT BATTER
    with col2:

        if st.button(
            "⏭️ PROCHAINE FRAPPEUSE",
            use_container_width=True
        ):

            if len(st.session_state.lineup) > 0:

                try:

                    current_pos = (
                        st.session_state.lineup.index(
                            st.session_state.current_player
                        )
                    )

                    next_pos = (
                        current_pos + 1
                    ) % len(
                        st.session_state.lineup
                    )

                    st.session_state.current_player = (
                        st.session_state.lineup[next_pos]
                    )

                    st.rerun()

                except:

                    pass

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

            st.session_state.lineup.append(
                player_name
            )

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

    cols = st.columns([1,5,2,2])

    # ORDER
    with cols[0]:

        st.markdown(
            f"## #{i+1}"
        )

    # NAME
    with cols[1]:

        st.markdown(
            f"""
            <div class="player-card">
            {player_name}
            </div>
            """,
            unsafe_allow_html=True
        )

    # PLAY
    with cols[2]:

        if st.button(
            "▶️ PLAY",
            key=f"play_{i}",
            use_container_width=True
        ):

            st.session_state.current_player = (
                player_name
            )

            st.rerun()

    # REMOVE
    with cols[3]:

        if st.button(
            "❌ REMOVE",
            key=f"remove_{i}",
            use_container_width=True
        ):

            st.session_state.lineup.remove(
                player_name
            )

            if (
                st.session_state.current_player
                == player_name
            ):
                st.session_state.current_player = None

            st.rerun()

# ==================================================
# SAVE LINEUP
# ==================================================
st.divider()

if st.button(
    "💾 Sauvegarder le lineup",
    use_container_width=True
):

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

    st.success(
        "Lineup sauvegardé."
    )
