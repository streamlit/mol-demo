import pandas as pd
import streamlit as st
from typing import Optional
from streamlit_ketcher import st_ketcher
from chembl_webresource_client.new_client import new_client as ch

ch.image.set_format('svg')
DEFAULT_COMPOUND = "CHEMBL141739"
EBI_URL = "https://www.ebi.ac.uk/chembl/"


def name_to_smiles(name: str) -> str:
    ret = ch.molecule.filter(molecule_synonyms__molecule_synonym__iexact=name).only('molecule_structures')
    return ret[0]["molecule_structures"]["molfile"]


def render_similarity_table(smiles: str, threshold: int) -> Optional[str]:
    colummns = ['molecule_chembl_id', 'similarity', 'pref_name']
    try:
        ret = ch.similarity.filter(smiles=smiles, similarity=threshold).only(colummns)
    except Exception as _:
        ret = None
    if not ret:
        st.warning("No results found")
        return
    ret = [
        {
            "Similarity": float(x["similarity"]),
            "Preferred name": x["pref_name"],
            "ChEMBL ID": f'<a href="{EBI_URL}compound_report_card/{x["molecule_chembl_id"]}/">{x["molecule_chembl_id"]}</a>',
            "Image": f'<img src="{EBI_URL}api/data/image/{x["molecule_chembl_id"]}.svg" height="100px" width="100px">'
        } for x in ret]
    df = pd.DataFrame.from_records(ret)
    styler = df.style.hide_index().format(
        subset=['Similarity'],
        decimal=',', precision=2
    ).bar(
        subset=['Similarity'],
        align="mid",
        cmap="coolwarm").background_gradient(subset=['Image'], cmap="gray", gmap=df['Similarity'], low=1, high=1)
    return styler.to_html(render_links=True)


if "smiles" not in st.session_state:
    st.session_state.smiles = None

st.set_page_config(layout="wide")
st.subheader("🧪 Molecule editor")

chembl_id = st.text_input("ChEMBL ID:", DEFAULT_COMPOUND)
st.session_state.smiles = ch.molecule.filter(chembl_id=chembl_id).only('molecule_structures')[0]["molecule_structures"]["molfile"]

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('☕ Caffeine'):
        st.session_state.smiles = name_to_smiles('Caffeine')
with col2:
    if st.button('🥱 Melatonin'):
        st.session_state.smiles = name_to_smiles('Melatonin')
with col3:
    if st.button('🚬 Nicotine'):
        st.session_state.smiles = name_to_smiles('Nicotine')
editor_column, results_column = st.columns(2)
with editor_column:
    smiles = st_ketcher(st.session_state.smiles)
    similarity_threshold = st.slider("Similarity threshold:", min_value=60, max_value=100)
    st.markdown(f"```{smiles}```")
    with results_column:
        table = render_similarity_table(smiles, similarity_threshold)
        if table:
            st.markdown(f'<div id="" style="overflow:scroll; height:600px;">{table}</div>', unsafe_allow_html=True)

