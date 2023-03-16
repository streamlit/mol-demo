import pandas as pd
from typing import Optional, Tuple

from chembl_webresource_client.new_client import new_client as ch

EBI_URL = "https://www.ebi.ac.uk/chembl/"


def name_to_molecule(name: str) -> Tuple[str, str]:
    columns = ['molecule_chembl_id', 'molecule_structures']
    ret = ch.molecule.filter(molecule_synonyms__molecule_synonym__iexact=name).only(columns)
    best_match = ret[0]
    return best_match["molecule_structures"]["molfile"], best_match["molecule_chembl_id"]


def id_to_molecule(chembl_id: str) -> Tuple[str, str]:
    return ch.molecule.filter(chembl_id=chembl_id).only('molecule_structures')[0]["molecule_structures"]["molfile"]


def style_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    return df.style.hide_index().format(
        subset=['Similarity'],
        decimal=',', precision=2
    ).bar(
        subset=['Similarity'],
        align="mid",
        cmap="coolwarm"
    ).applymap(lambda x: 'background-color: #aaaaaa', subset=['Image'])


def style_predictions(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    return df.style.hide_index().format(
        subset=['Prediction'],
        decimal=',', precision=2
    ).bar(
        subset=['Prediction'],
        align="mid",
        cmap="plasma_r",
        vmax=1.0,
        vmin=0.8
    )


def render_chembl_url(chembl_id: str) -> str:
    return f'<a href="{EBI_URL}compound_report_card/{chembl_id}/">{chembl_id}</a>'


def render_chembl_img(chembl_id: str) -> str:
    return f'<img src="{EBI_URL}api/data/image/{chembl_id}.svg" height="100px" width="100px">'


def render_row(row):
    return {
        "Similarity": float(row["similarity"]),
        "Preferred name": row["pref_name"],
        "ChEMBL ID": render_chembl_url(row["molecule_chembl_id"]),
        "Image": render_chembl_img(row["molecule_chembl_id"])
    }


def render_target(target):
    return {
        "Prediction": float(target["pred"]),
        "ChEMBL ID": render_chembl_url(target["chembl_id"])
    }


def find_similar_molecules(smiles: str, threshold: int):
    columns = ['molecule_chembl_id', 'similarity', 'pref_name', 'molecule_structures']
    try:
        return ch.similarity.filter(smiles=smiles, similarity=threshold).only(columns)
    except Exception as _:
        return None


def render_similarity_table(similar_molecules) -> Optional[str]:
    records = [render_row(row) for row in similar_molecules]
    df = pd.DataFrame.from_records(records)
    styled = style_table(df)
    return styled.to_html(render_links=True)


def render_target_predictions_table(predictions) -> Optional[str]:
    df = pd.DataFrame(predictions)
    records = [render_target(target) for target in
               df.sort_values(by=['pred'], ascending=False).head(20).to_dict('records')]
    df = pd.DataFrame.from_records(records)
    styled = style_predictions(df)
    return styled.to_html(render_links=True)


def get_similar_smiles(similar_molecules):
    return [mol["molecule_structures"]["canonical_smiles"] for mol in similar_molecules]