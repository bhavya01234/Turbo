import turbopuffer
import voyageai
from typing import List, Dict, Any
from datetime import datetime

class CandidateSearch:
    def __init__(
        self, 
        turbopuffer_key: str,
        voyage_key: str,
        namespace: str = "search-test-v4"
    ):
        self.tpuf = turbopuffer.Turbopuffer(
            api_key=turbopuffer_key,
            region="aws-us-west-2"
        )
        self.voyage = voyageai.Client(api_key=voyage_key)
        self.namespace = self.tpuf.namespace(namespace)
        print("Successfully initialized CandidateSearch")

    def parse_experience(self, exp_str: str) -> Dict[str, str]:
        """Parse experience string into components"""
        parts = exp_str.split("::")
        exp_dict = {}
        for part in parts:
            if "_" in part:
                key, value = part.split("_", 1)
                exp_dict[key] = value
        return exp_dict

    def calculate_years_experience(self, experiences: List[str]) -> int:
        """Calculate total years of relevant experience"""
        total_years = 0
        current_year = 2024  # Current year for calculation
        
        for exp in experiences:
            exp_dict = self.parse_experience(exp)
            
            # Check explicit years
            if 'yrs' in exp_dict:
                try:
                    years = int(exp_dict['yrs'])
                    total_years += years
                except ValueError:
                    continue
            
            # Calculate from start/end dates
            if 'start' in exp_dict and exp_dict['start'].isdigit():
                start_year = int(exp_dict['start'])
                if 'end' in exp_dict and exp_dict['end'].isdigit():
                    end_year = int(exp_dict['end'])
                else:
                    end_year = current_year
                total_years += end_year - start_year
                
        return total_years

    def check_degree_requirements(self, candidate: Dict, required_degrees: List[str]) -> bool:
        """Check if candidate has required degrees"""
        if not required_degrees:
            return True
        
        if not hasattr(candidate, 'deg_degrees'):
            return False
            
        candidate_degrees = [d.lower() for d in candidate.deg_degrees]
        return any(deg.lower() in candidate_degrees for deg in required_degrees)

    def check_experience_requirements(self, candidate: Dict, min_years: int) -> bool:
        """Check if candidate meets minimum experience requirements"""
        if not min_years:
            return True
            
        if not hasattr(candidate, 'experience'):
            return False
            
        total_years = self.calculate_years_experience(candidate.experience)
        return total_years >= min_years

    def score_relevance(self, candidate: Dict, relevant_keywords: List[str], role_type: str = None) -> float:
        """Score candidate based on keyword relevance and role-specific criteria"""
        score = 0.0
        
        # Base relevance scoring
        if hasattr(candidate, 'exp_titles'):
            for title in candidate.exp_titles:
                if any(keyword.lower() in title.lower() for keyword in relevant_keywords):
                    score += 2.0

        if hasattr(candidate, 'rerankSummary'):
            summary_lower = candidate.rerankSummary.lower()
            for keyword in relevant_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in summary_lower:
                    # Weight recent experience more heavily
                    if "current" in summary_lower or "present" in summary_lower:
                        score += 1.5
                    else:
                        score += 1.0

        # Role-specific scoring
        if role_type == "lawyer":
            if hasattr(candidate, 'experience'):
                legal_keywords = ["counsel", "legal", "law", "attorney", "litigation"]
                for exp in candidate.experience:
                    if any(keyword in exp.lower() for keyword in legal_keywords):
                        score += 1.5
                        
        elif role_type == "banker":
            if hasattr(candidate, 'experience'):
                banking_keywords = ["investment banking", "m&a", "private equity", "capital markets"]
                for exp in candidate.experience:
                    if any(keyword in exp.lower() for keyword in banking_keywords):
                        score += 1.5

        return score

    def vector_search(self, query: str, top_k: int = 50) -> List[Dict]:
        """Perform semantic search using vector similarity"""
        try:
            response = self.voyage.embed(query, model="voyage-3")
            query_embedding = response.embeddings[0]
            
            print(f"Generated embedding of length: {len(query_embedding)}")
            
            results = self.namespace.query(
                rank_by=("vector", "ANN", query_embedding),
                top_k=top_k,
                include_attributes=True
            )
            
            return results.rows
        except Exception as e:
            print(f"Error in vector search: {str(e)}")
            raise

    def search(
        self,
        query: str,
        hard_criteria: Dict[str, Any],
        soft_criteria: Dict[str, Any],
        role_type: str = None,
        n_results: int = 10
    ) -> List[str]:
        """
        Main search pipeline
        """
        print(f"Searching with query: {query}")
        
        # Initial semantic search with larger pool
        candidates = self.vector_search(query, top_k=150)
        print(f"Found {len(candidates)} initial candidates")
        
        # Filter by hard criteria
        filtered_candidates = []
        for candidate in candidates:
            if (self.check_degree_requirements(candidate, hard_criteria.get('required_degrees')) and
                self.check_experience_requirements(candidate, hard_criteria.get('min_years'))):
                filtered_candidates.append(candidate)
        
        print(f"Found {len(filtered_candidates)} candidates after hard criteria")
        
        # Score candidates
        scored_candidates = []
        for candidate in filtered_candidates:
            relevance_score = self.score_relevance(
                candidate, 
                soft_criteria.get('relevant_experience', []),
                role_type=role_type
            )
            scored_candidates.append((candidate, relevance_score))
        
        # Sort by score
        ranked = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
        
        # Print top candidates for debugging
        print("\nTop candidates:")
        for candidate, score in ranked[:3]:
            print(f"ID: {candidate.id}, Name: {candidate.name}, Score: {score}")
        
        # Return top N candidate IDs
        return [candidate.id for candidate, _ in ranked[:n_results]]
