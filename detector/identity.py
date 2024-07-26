import os
from typing import List

import pandas as pd


def get_name(deep_face_identities: List[pd.DataFrame]) -> str | None:
    if len(deep_face_identities) == 0:
        return None

    closest_identity = deep_face_identities[0]['identity']

    if len(closest_identity) == 0:
        return None

    closest_identity_path = closest_identity[0]
    _, identity_file = os.path.split(closest_identity_path)

    name = identity_file.split('-')[-2]
    return name
