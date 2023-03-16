import onnxruntime
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

FP_SIZE = 1024
RADIUS = 2

# load the model
ort_session = onnxruntime.InferenceSession("chembl_32_multitask.onnx")


def calc_morgan_fp(smiles):
    mol = Chem.MolFromSmiles(smiles)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(
        mol, RADIUS, nBits=FP_SIZE)
    a = np.zeros((0,), dtype=np.float32)
    Chem.DataStructs.ConvertToNumpyArray(fp, a)
    return a


def format_preds(preds, targets):
    preds = np.concatenate(preds).ravel()
    np_preds = [(tar, pre) for tar, pre in zip(targets, preds)]
    dt = [('chembl_id', '|U20'), ('pred', '<f4')]
    np_preds = np.array(np_preds, dtype=dt)
    np_preds[::-1].sort(order='pred')
    return np_preds


def predict(smiles):
    # calculate the FPs
    descs = calc_morgan_fp(smiles)

    # run the prediction
    ort_inputs = {ort_session.get_inputs()[0].name: descs}
    preds = ort_session.run(None, ort_inputs)

    # example of how the output of the model can be formatted
    return format_preds(preds, [o.name for o in ort_session.get_outputs()])


def predict_all(smiles):
    preds = []
    for smile in smiles:
        preds.append(predict(smile))
    return np.concatenate(preds)
