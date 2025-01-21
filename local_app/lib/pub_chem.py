"""Helpers for working with data from PubChem, a free database of chemical information.

https://pubchem.ncbi.nlm.nih.gov/
"""

from functools import cache
from typing import Any

import httpx
import re

PUBCHEM_BASE_URI = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"


@cache
def _pubchem_get(url: str) -> dict[str, Any]:
    return httpx.get(f"{PUBCHEM_BASE_URI}{url}").json()


def _get_compound_string_prop(
    compound_json: dict[str, Any],
    label: str,
    name: str | None = None,
) -> str | None:
    matching_props = [
        p
        for p in compound_json["props"]
        if p["urn"]["label"] == label and (not name or (p["urn"]["name"] == name))
    ]
    if matching_props:
        return matching_props[0]["value"]["sval"]
    return None


# Just look for a single chemical, as a trivial example
def search(query: str, limit: int = 1) -> list[dict[str, Any]]:
    url = f"name/{query}/cids/JSON?MaxRecords={limit}"
    result_json = _pubchem_get(url)
    if "IdentifierList" not in result_json:
        return []
    result_ids = result_json["IdentifierList"]["CID"]
    return [{"cid": cid, **get_by_cid(cid)} for cid in result_ids]


# Example: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON
def get_by_cid(cid: str) -> dict[str, Any]:
    result_json = _pubchem_get(f"cid/{cid}/JSON")
    synonyms_json = _pubchem_get(f"cid/{cid}/synonyms/JSON")["InformationList"]
    r = re.compile(r"\d+-\d+-\d+")  # search for cas number by format
    cas_num = list(filter(r.match, synonyms_json["Information"][0]["Synonym"]))[0]
    name = synonyms_json["Information"][0]["Synonym"][0]
    compound_json = result_json["PC_Compounds"][0]
    smiles = _get_compound_string_prop(compound_json, label="SMILES", name="Canonical")
    molecular_formula = _get_compound_string_prop(
        compound_json, label="Molecular Formula"
    )

    return {
        "cid": cid,
        "name": name,
        "casNum": cas_num,
        "smiles": smiles,
        "molecularFormula": molecular_formula,
    }


def image_url(cid: str) -> str:
    return f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
