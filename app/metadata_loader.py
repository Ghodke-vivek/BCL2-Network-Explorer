import pandas as pd
import re
import os


# =========================================
# LOAD METADATA FILE
# =========================================

def load_metadata():

    metadata_folder = "data/metadata"

    files = os.listdir(metadata_folder)

    excel_files = [
        f for f in files
        if f.endswith(".xlsx")
    ]

    if len(excel_files) == 0:

        raise FileNotFoundError(
            "No metadata Excel file found "
            "inside data/metadata/"
        )

    metadata_path = os.path.join(
        metadata_folder,
        excel_files[0]
    )

    df = pd.read_excel(metadata_path)

    metadata_dict = {}

    for _, row in df.iterrows():

        kegg_id = str(
            row["KEGG_ID"]
        ).strip()

        metadata_dict[kegg_id] = {

            "Names": row.get(
                "Names",
                ""
            ),

            "EC_Number": row.get(
                "EC_Number",
                ""
            ),

            "Ortholog_IDs": row.get(
                "Ortholog_IDs",
                ""
            ),

            "HSA_IDs": row.get(
                "HSA_IDs",
                ""
            ),

            "Compound_IDs": row.get(
                "Compound_IDs",
                ""
            ),

            "HSA_Symbols": row.get(
                "HSA_Symbols",
                ""
            ),

            "HSA_Biological_Names": row.get(
                "HSA_Biological_Names",
                ""
            ),

            "Compound_Biological_Names_Symbol": row.get(
                "Compound_Biological_Names_Symbol",
                ""
            ),

            "UniProt_IDs": row.get(
                "UniProt_IDs",
                ""
            ),

            "GO_IDs": row.get(
                "GO_IDs",
                ""
            ),

            "GO_Labels": row.get(
                "GO_Labels",
                ""
            )
        }

    return metadata_dict


# =========================================
# EXTRACT KEGG IDS
# =========================================

def extract_kegg_ids(kegg_string):

    if pd.isna(kegg_string):
        return []

    kegg_string = str(kegg_string)

    matches = re.findall(
        r'K\d+|C\d+|D\d+|G\d+',
        kegg_string
    )

    return list(set(matches))
