# type: ignore
from typing import Any

from benchling_sdk.apps.framework import App
from benchling_sdk.helpers.serialization_helpers import fields
from benchling_sdk.models import (
    Molecule,
    MoleculeCreate,
    MoleculeStructure,
    MoleculeStructureStructureFormat,
)

from local_app.lib.logger import get_logger

logger = get_logger()


def create_molecule(app: App, chemical_result: dict[str, Any]) -> Molecule:
    logger.debug("Chemical to create: %s", chemical_result)
    molecule_structure = MoleculeStructure(
        structure_format=MoleculeStructureStructureFormat.SMILES,
        value=chemical_result["smiles"],
    )
    config = app.config_store.config_by_path
    # .required().value_str() are only needed for type safety checks like MyPy
    # If type safety isn't a concern:
    # `app.config_store.config_by_path(["Molecule Schema", "Molecular Weight"]).value`
    molecular_weight_field = (
        config(["Molecule Schema", "Molecular Weight"]).required().value_str()
    )
    mono_isotopic_field = (
        config(["Molecule Schema", "MonoIsotopic"]).required().value_str()
    )
    formula = config(["Molecule Schema", "Formula"]).required().value_str()
    cas_num = config(["Molecule Schema", "CAS Number"]).required().value_str()
    smiles_raw = config(["Molecule Schema", "SMILES"]).required().value_str()
    molecule_create = MoleculeCreate(
        chemical_structure=molecule_structure,
        name=chemical_result["name"],
        aliases=[f"cid:{chemical_result['cid']}"],
        folder_id=config(["Sync Folder"]).required().value_str(),
        schema_id=config(["Molecule Schema"]).required().value_str(),
        fields=fields(
            {
                molecular_weight_field: {"value": chemical_result["molecularWeight"]},
                mono_isotopic_field: {"value": chemical_result["monoisotopic"]},
                formula: {"value": chemical_result["molecularFormula"]},
                cas_num: {"value": chemical_result["casNum"]},
                smiles_raw: {"value": chemical_result["smiles"]},
            },
        ),
    )
    return app.benchling.molecules.create(molecule_create)
