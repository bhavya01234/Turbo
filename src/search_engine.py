import turbopuffer
import voyageai
from typing import List, Dict, Any

class CandidateSearch:
    def __init__(
        self, 
        turbopuffer_key: str,
        voyage_key: str,
        namespace: str = "search-test-v4"
    ):
        # Initialize clients
        self.tpuf = turbopuffer.Turbopuffer(
            api_key=turbopuffer_key,
            region="aws-us-west-*"
        )
        self.voyage = voyageai.Client(api_key=voyage_key)
        self.namespace = self.tpuf.namespace(namespace)

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        response = self.voyage.embed(query, model="voyage-3")
        return response.embeddings[0]

    def vector_search(self, query: str, top_k: int = 50) -> List[Dict]:
        """Perform semantic search using vector similarity"""
        query_embedding = self.embed_query(query)
        
        results = self.namespace.query(
            rank_by=("vector", "ANN", query_embedding),
            top_k=top_k,
            include_attributes=True
        )
        
        return results.rows

    def score_candidate(self, candidate: Dict, criteria: Dict) -> float:
        """Score candidate based on matching criteria"""
        score = 0.0
        
        # Experience scoring
        if "relevant_experience" in criteria and hasattr(candidate, "exp_titles"):
            relevant_keywords = criteria["relevant_experience"]
            for title in candidate.exp_titles:
                if any(keyword.lower() in title.lower() for keyword in relevant_keywords):
                    score += 2.0

        # Education scoring
        if "required_degrees" in criteria and hasattr(candidate, "deg_degrees"):
            if any(deg.lower() in [d.lower() for d in candidate.deg_degrees] 
                  for deg in criteria["required_degrees"]):
                score += 3.0

        # Experience years scoring
        if "min_years" in criteria and hasattr(candidate, "exp_years"):
            exp_years = [int(yr) for yr in candidate.exp_years if yr.isdigit()]
            if exp_years and max(exp_years) >= criteria["min_years"]:
                score += 2.0

        return score

    def search(
        self,
        query: str,
        hard_criteria: Dict[str, Any],
        soft_criteria: Dict[str, Any],
        n_results: int = 10
    ) -> List[str]:
        """Main search pipeline"""
        # Initial vector search
        candidates = self.vector_search(query, top_k=100)
        
        # Score candidates
        scored_candidates = [
            (candidate, self.score_candidate(candidate, {**hard_criteria, **soft_criteria}))
            for candidate in candidates
        ]
        
        # Sort by score
        ranked = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
        
        # Return top N candidate IDs
        return [candidate["_id"] for candidate, _ in ranked[:n_results]]
