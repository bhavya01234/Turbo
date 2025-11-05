from src.search_engine import CandidateSearch
from typing import List, Dict
import json
import requests

def evaluate_results(config_path: str, object_ids: List[str], email: str) -> Dict:
    """Evaluate search results"""
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

def test_searches():
    # Initialize search engine
    searcher = CandidateSearch(
        turbopuffer_key='tpuf_wTbagsVtzNmVfzDm48lNeszzJdTaCOUF',
        voyage_key='pa-vNEmoJfc5evP_SSvpxIAj3uFzs9dfppEZkpx-3kOFZy'
    )

    # Search configurations
    queries = {
        "tax_lawyer": {
            "query": "Experienced tax lawyer with corporate transaction expertise and IRS audit experience",
            "hard_criteria": {
                "required_degrees": ["jd"],
                "min_years": 3
            },
            "soft_criteria": {
                "relevant_experience": [
                    "tax", "corporate", "M&A", "transaction", "legal", "IRS", "audit"
                ]
            },
            "config_path": "tax_lawyer.yml",
            "role_type": "lawyer"
        },
        "banker": {
            "query": "Healthcare investment banker with M&A and private equity experience",
            "hard_criteria": {
                "min_years": 2,
                "required_degrees": ["mba"]
            },
            "soft_criteria": {
                "relevant_experience": [
                    "healthcare", "investment banking", "M&A", "private equity",
                    "mergers", "acquisitions", "capital markets"
                ]
            },
            "config_path": "bankers.yml",
            "role_type": "banker"
        }
    }

    # Test each query
    for role, config in queries.items():
        print(f"\nTesting search for {role}...")
        results = searcher.search(
            query=config["query"],
            hard_criteria=config["hard_criteria"],
            soft_criteria=config["soft_criteria"],
            role_type=config["role_type"],
            n_results=10
        )
        print(f"Found {len(results)} results")
        print("Result IDs:", json.dumps(results, indent=2))
        
        # Evaluate results
        if len(results) > 0:
            print("\nEvaluating results...")
            try:
                evaluation = evaluate_results(
                    config_path=config["config_path"],
                    object_ids=results,
                    email="bhavyamalik2020@gmail.com"
                )
                print("Average final score:", evaluation.get("average_final_score"))
                print("\nDetailed scores:")
                print(json.dumps(evaluation.get("average_soft_scores", []), indent=2))
                print("\nHard criteria pass rates:")
                print(json.dumps(evaluation.get("average_hard_scores", []), indent=2))
            except Exception as e:
                print(f"Error during evaluation: {str(e)}")

if __name__ == "__main__":
    try:
        test_searches()
    except Exception as e:
        print(f"Error in test: {str(e)}")
