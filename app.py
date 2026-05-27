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
# LOAD EXCEL
# ==================================================
@st.cache_data
def load_data():

    df = pd.read_excel(EXCEL_FILE)

    df.columns = df.columns.str.strip()

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

if "current_player" not in st.session_state:
    st.session_state.current_player = None

# ==================================================
# HEADER
# ==================================================
st.title("⚾ WALK-UP SONGS MANAGER")

st.markdown("## Drag & Drop Lineup")

# ==================================================
# SORTABLE LIST
# ==================================================
names_list = st.session_state.df["Nom"].tolist()

sorted_names = sort_items(
    names_list,
    direction="vertical"
)

# ==================================================
# REBUILD DATAFRAME
# ==================================================
new_df = pd.DataFrame()

for i, name in enumerate(sorted_names):

    row = st.session_state.df[
        st.session_state.df["Nom"] == name
    ].iloc[0]

    row["ordre"] = i + 1

    new_df = pd.concat([
        new_df,
        pd.DataFrame([row])
    ], ignore_index=True)

st.session_state.df = new_df

st.divider()

# ==================================================
# CURRENT PLAYER
# ==================================================
if st.session_state.current_player is not None:

    player_row = st.session_state.df[
        st.session_state.df["Nom"]
        == st.session_state.current_player
    ].iloc[0]

    st.markdown(f"""
    ### 🎵 Lecture en cours
    ## {player_row['Nom']}
    """)

    st.audio(player_row["Lien"])

st.divider()

# ==================================================
# PLAY BUTTONS
# ==================================================
st.subheader("Lineup")

for i, row in st.session_state.df.iterrows():

    cols = st.columns([1,5,2])

    with cols[0]:
        st.markdown(f"### #{i+1}")

    with cols[1]:
        st.markdown(f"### {row['Nom']}")

    with cols[2]:

        if st.button(
            "🎵 PLAY",
            key=f"play_{i}"
        ):

            st.session_state.current_player = row["Nom"]

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
