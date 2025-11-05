import requests
from typing import List, Dict

def evaluate_results(
    config_path: str,
    object_ids: List[str],
    email: str
) -> Dict:
    """
    Evaluate search results using the provided endpoint
    """
    response = requests.post(
        "https://mercor-dev--search-eng-interview.modal.run/evaluate",
        headers={
            "Content-Type": "application/json",
            "Authorization": email
        },
        json={
            "config_path": config_path,
            "object_ids": object_ids
        }
    )
    return response.json()
