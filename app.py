import streamlit as st
import pandas as pd

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(
    page_title="Walk-Up Songs",
    layout="wide"
)

EXCEL_FILE = "Chanson Filles.xlsx"

# ==================================================
# LOAD EXCEL
# ==================================================
@st.cache_data
def load_data():

    df = pd.read_excel(EXCEL_FILE)

    # Nettoyage des colonnes
    df.columns = df.columns.str.strip()

    # Uniformiser noms colonnes
    df = df.rename(columns={
        "Ordre": "ordre",
        "ORDRE": "ordre",
        "nom": "Nom",
        "NOM": "Nom",
        "lien": "Lien",
        "LIEN": "Lien"
    })

    return df

if "df" not in st.session_state:
    st.session_state.df = load_data()

# ==================================================
# SESSION STATE
# ==================================================
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# ==================================================
# FUNCTIONS
# ==================================================
def move_up(index):

    if index > 0:

        df = st.session_state.df.copy()

        temp = df.iloc[index - 1].copy()

        df.iloc[index - 1] = df.iloc[index]
        df.iloc[index] = temp

        df["ordre"] = range(1, len(df) + 1)

        st.session_state.df = df


def move_down(index):

    df = st.session_state.df.copy()

    if index < len(df) - 1:

        temp = df.iloc[index + 1].copy()

        df.iloc[index + 1] = df.iloc[index]
        df.iloc[index] = temp

        df["ordre"] = range(1, len(df) + 1)

        st.session_state.df = df


# ==================================================
# STYLE
# ==================================================
st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}

.player-card {
    background-color: #111111;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 12px;
    border: 2px solid #ff8c00;
}

.player-name {
    color: white;
    font-size: 32px;
    font-weight: bold;
}

.player-order {
    color: #ff8c00;
    font-size: 24px;
    font-weight: bold;
}

.stButton button {
    width: 100%;
    height: 60px;
    font-size: 20px;
    border-radius: 12px;
}

audio {
    width: 100%;
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
# NAVIGATION
# ==================================================
nav1, nav2, nav3 = st.columns([1,2,1])

with nav1:

    if st.button("⬅️ Previous"):

        st.session_state.current_index = max(
            0,
            st.session_state.current_index - 1
        )

        st.rerun()

with nav3:

    if st.button("Next ➡️"):

        st.session_state.current_index = min(
            len(st.session_state.df) - 1,
            st.session_state.current_index + 1
        )

        st.rerun()

st.divider()

# ==================================================
# ACTIVE PLAYER
# ==================================================
player = st.session_state.df.iloc[
    st.session_state.current_index
]

st.markdown(f"""
<div class="player-card">

<div class="player-order">
Ordre #{player.get('ordre', '')}
</div>

<div class="player-name">
{player.get('Nom', '')}
</div>

</div>
""", unsafe_allow_html=True)

# AUDIO
audio_url = player.get("Lien", "")

if audio_url != "":
    st.audio(audio_url)

st.divider()

# ==================================================
# LINEUP
# ==================================================
st.subheader("Lineup")

for i, row in st.session_state.df.iterrows():

    st.markdown("---")

    cols = st.columns([1,4,1,1,2])

    # ORDER
    with cols[0]:

        st.markdown(f"""
        <div class="player-order">
        #{row.get('ordre', '')}
        </div>
        """, unsafe_allow_html=True)

    # NAME
    with cols[1]:

        st.markdown(f"""
        <div class="player-name">
        {row.get('Nom', '')}
        </div>
        """, unsafe_allow_html=True)

    # UP
    with cols[2]:

        if st.button("⬆️", key=f"up_{i}"):

            move_up(i)
            st.rerun()

    # DOWN
    with cols[3]:

        if st.button("⬇️", key=f"down_{i}"):

            move_down(i)
            st.rerun()

    # PLAY
    with cols[4]:

        if st.button("🎵 PLAY", key=f"play_{i}"):

            st.session_state.current_index = i
            st.rerun()

# ==================================================
# SAVE EXCEL
# ==================================================
st.divider()

if st.button("💾 Sauvegarder le lineup"):

    st.session_state.df.to_excel(
        EXCEL_FILE,
        index=False
    )

    st.success("Lineup sauvegardé.")

# ==================================================
# DEBUG TEMPORAIRE
# ==================================================
with st.expander("DEBUG colonnes Excel"):
    st.write(st.session_state.df.columns)
