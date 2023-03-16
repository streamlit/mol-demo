import streamlit as st
from streamlit_ketcher import st_ketcher

import utils

DEFAULT_COMPOUND = "CHEMBL141739"

if "smiles" not in st.session_state:
    st.session_state.smiles = None

if "chembl_id" not in st.session_state:
    st.session_state.chembl_id = DEFAULT_COMPOUND

st.set_page_config(layout="wide")
st.subheader("🧪 Molecule editor")

chembl_id = st.text_input("ChEMBL ID:", st.session_state.chembl_id)
st.session_state.smiles = utils.id_to_molecule(chembl_id)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('☕ Caffeine'):
        st.session_state.smiles, st.session_state.chembl_id = utils.name_to_molecule('Caffeine')
with col2:
    if st.button('🥱 Melatonin'):
        st.session_state.smiles, st.session_state.chembl_id = utils.name_to_molecule('Melatonin')
with col3:
    if st.button('🚬 Nicotine'):
        st.session_state.smiles, st.session_state.chembl_id = utils.name_to_molecule('Nicotine')
editor_column, results_column = st.columns(2)
with editor_column:
    smiles = st_ketcher(st.session_state.smiles)
    similarity_threshold = st.slider("Similarity threshold:", min_value=60, max_value=100)
    st.markdown(f"```{smiles}```")
    with results_column:
        table = utils.render_similarity_table(smiles, similarity_threshold)
        if not table:
            st.warning("No results found")
        if table:
            st.markdown(f'<div id="" style="overflow:scroll; height:600px; padding-left: 80px;">{table}</div>',
                        unsafe_allow_html=True)

