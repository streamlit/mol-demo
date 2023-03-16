import streamlit as st
from streamlit_ketcher import st_ketcher

import utils
import target_predictions

DEFAULT_COMPOUND = "CHEMBL141739"

if "molfile" not in st.session_state:
    st.session_state.molfile = None

if "chembl_id" not in st.session_state:
    st.session_state.chembl_id = DEFAULT_COMPOUND

st.set_page_config(layout="wide")
st.subheader("🧪 Molecule editor")

chembl_id = st.text_input("ChEMBL ID:", st.session_state.chembl_id)
st.session_state.molfile = utils.id_to_molecule(chembl_id)

famous_molecules = [('☕', 'Caffeine'), ('🥱', 'Melatonin'), ('🚬', 'Nicotine')]
for molecule, column in zip(famous_molecules, st.columns(len(famous_molecules))):
    with column:
        emoji, name = molecule
        if st.button(f'{emoji} {name}'):
            st.session_state.molfile, st.session_state.chembl_id = utils.name_to_molecule(name)

editor_column, results_column = st.columns(2)
similar_smiles = []
with editor_column:
    smiles = st_ketcher(st.session_state.molfile)
    similarity_threshold = st.slider("Similarity threshold:", min_value=60, max_value=100)
    st.markdown(f"```{smiles}```")
    with results_column:
        similar_molecules = utils.find_similar_molecules(smiles, similarity_threshold)
        table = utils.render_similarity_table(similar_molecules)
        similar_smiles = utils.get_similar_smiles(similar_molecules)
        if not table:
            st.warning("No results found")
        if table:
            st.markdown(f'<div id="" style="overflow:scroll; height:600px; padding-left: 80px;">{table}</div>',
                        unsafe_allow_html=True)

if similar_smiles:
    if st.button("🔮 Predict targets"):
        preds = target_predictions.predict_all(similar_smiles)
        table = utils.render_target_predictions_table(preds)
        st.markdown(table, unsafe_allow_html=True)

