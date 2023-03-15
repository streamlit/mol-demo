import pandas as pd
import streamlit as st
from streamlit_ketcher import st_ketcher
from chembl_webresource_client.new_client import new_client as ch

ch.image.set_format('svg')
DEFAULT_MOL = "C[N+]1=CC=C(/C2=C3\C=CC(=N3)/C(C3=CC=CC(C(N)=O)=C3)=C3/C=C/C(=C(\C4=CC=[N+](C)C=C4)C4=N/C(=C(/C5=CC=CC(C(N)=O)=C5)C5=CC=C2N5)C=C4)N3)C=C1"
EBI_URL = "https://www.ebi.ac.uk/chembl/"


def name_to_smiles(name: str) -> str:
    ret = ch.molecule.filter(molecule_synonyms__molecule_synonym__iexact=name).only('molecule_structures')
    return ret[0]["molecule_structures"]["canonical_smiles"]


def render_similarity_table(smiles: str, threshold: int) -> str:
    colummns = ['molecule_chembl_id', 'similarity', 'pref_name']
    ret = ch.similarity.filter(smiles=smiles, similarity=threshold).only(colummns)
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
    st.session_state.smiles = DEFAULT_MOL

st.set_page_config(layout="wide")
st.subheader("🧪 Molecule editor")

molecule = st.text_input(
    "Molecule from [SMILES](https://en.wikipedia.org/wiki/Simplified_molecular-input_line-entry_system) string:",
    DEFAULT_MOL)
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
    st.session_state["smiles"] = st_ketcher(st.session_state.smiles)
    st.markdown(f"`{st.session_state.smiles}`")
    similarity_threshold = st.slider("Similarity threshold:", min_value=60, max_value=100)
    with results_column:
        table = render_similarity_table(st.session_state.smiles, similarity_threshold)
        st.markdown(f'<div id="" style="overflow:scroll; height:600px;">{table}</div>', unsafe_allow_html=True)

