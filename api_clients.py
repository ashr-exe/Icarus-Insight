import os
import aiohttp
import asyncio
import json
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GooglePatentsAPI:
    """Client for Google Patents API (simulated as no true free API exists)"""
    def __init__(self):
        self.base_url = "https://patents.google.com/xhr/query"
        
    async def search(self, keywords=None, ipc_codes=None, date_range=None, assignees=None):
        """Search for patents matching the criteria"""
        # Build the query
        query_parts = []
        
        if keywords:
            if isinstance(keywords, list):
                query_parts.append("(" + " OR ".join(keywords) + ")")
            else:
                query_parts.append(keywords)
        
        if ipc_codes:
            if isinstance(ipc_codes, list):
                ipc_query = " OR ".join([f'cpc:"{code}"' for code in ipc_codes])
            else:
                ipc_query = f'cpc:"{ipc_codes}"'
            query_parts.append(f"({ipc_query})")
        
        if assignees:
            if isinstance(assignees, list):
                assignee_query = " OR ".join([f'assignee:"{company}"' for company in assignees])
            else:
                assignee_query = f'assignee:"{assignees}"'
            query_parts.append(f"({assignee_query})")
        
        if date_range:
            start_date, end_date = date_range
            if start_date and end_date:
                if isinstance(start_date, str):
                    start_date_str = start_date
                else:
                    start_date_str = start_date.strftime("%Y-%m-%d")
                
                if isinstance(end_date, str):
                    end_date_str = end_date
                else:
                    end_date_str = end_date.strftime("%Y-%m-%d")
                
                query_parts.append(f"(publication_date:{start_date_str}T00:00:00Z TO {end_date_str}T23:59:59Z)")
        
        query = " AND ".join(query_parts)
        
        # Since we don't have a real Google Patents API, we'll simulate results
        # In a real implementation, this would make an HTTP request
        
        # Mock data - replace with actual API call in production
        sample_patents = self._generate_sample_patents(query)
        return sample_patents
    
    def _generate_sample_patents(self, query):
        """Generate sample patent data for demonstration purposes"""
        # Parse query to extract keywords for more realistic samples
        keywords = []
        ipc_codes = []
        
        if "cpc:" in query:
            import re
            ipc_matches = re.findall(r'cpc:"([^"]+)"', query)
            ipc_codes = ipc_matches
        
        keyword_parts = query.split(" AND ")
        for part in keyword_parts:
            if "cpc:" not in part and "assignee:" not in part and "publication_date:" not in part:
                # This is likely the keywords part
                clean_part = part.replace("(", "").replace(")", "").replace(" OR ", " ")
                keywords.extend(clean_part.split())
        
        # Generate sample patents based on extracted information
        patents = []
        for i in range(1, 11):  # Generate 10 sample patents
            keywords_subset = ' '.join(keywords[:min(3, len(keywords))])
            if not keywords_subset:
                keywords_subset = "aerospace innovation"
                
            ipc_code = ipc_codes[0] if ipc_codes else "B64G"
            
            patent = {
                "id": f"US{10000000 + i*111}A1",
                "title": f"Advanced {keywords_subset.title()} System",
                "abstract": f"A novel system for {keywords_subset} that improves efficiency and performance in aerospace applications.",
                "assignee": self._get_random_assignee(),
                "inventors": [self._get_random_inventor(), self._get_random_inventor()],
                "publication_date": self._get_random_date(2010, 2023),
                "filing_date": self._get_random_date(2005, 2020),
                "ipc_codes": [ipc_code],
                "claims_count": 10 + i,
                "citation_count": i * 3,
                "url": f"https://patents.google.com/patent/US{10000000 + i*111}A1/en"
            }
            patents.append(patent)
        
        return patents
    
    def _get_random_assignee(self):
        """Return a random aerospace company name"""
        companies = [
            "Boeing", "Airbus", "Lockheed Martin", "SpaceX", "NASA", 
            "Northrop Grumman", "General Electric Aviation", "Rolls-Royce", 
            "Raytheon Technologies", "Safran", "Blue Origin", "United Technologies"
        ]
        import random
        return random.choice(companies)
    
    def _get_random_inventor(self):
        """Return a random inventor name"""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily"]
        last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson"]
        
        import random
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _get_random_date(self, start_year, end_year):
        """Return a random date between start_year and end_year"""
        import random
        from datetime import datetime, timedelta
        
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_days = random.randrange(days_between_dates)
        
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime("%Y-%m-%d")


class USPTOOpenDataAPI:
    """Client for USPTO Open Data API"""
    def __init__(self):
        self.base_url = "https://developer.uspto.gov/ibd-api/v1/application/grants"
    
    async def search(self, keywords=None, ipc_codes=None, date_range=None, assignees=None):
        """Search for patents from USPTO"""
        # In a real implementation, this would make API requests to USPTO
        # For now, we'll just return empty results as placeholder
        return []


class ArxivAPI:
    """Client for arXiv API"""
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def search(self, search_query, max_results=10, categories=None):
        """Search arXiv for papers matching the query"""
        query_params = {
            "search_query": search_query,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query_params["search_query"] = f"({query_params['search_query']}) AND ({cat_query})"
        
        # Simulate API call
        sample_papers = self._generate_sample_papers(query_params["search_query"], max_results)
        return sample_papers
    
    def _generate_sample_papers(self, query, max_results=10):
        """Generate sample arXiv papers for demonstration"""
        # Extract potential keywords from query
        import re
        keywords = re.findall(r'"([^"]+)"', query)
        if not keywords:
            keywords = query.split()
        
        # Generate papers
        papers = []
        for i in range(1, max_results + 1):
            # Use keywords to make titles more realistic
            keyword = keywords[i % len(keywords)] if keywords else "aerospace"
            
            paper = {
                "id": f"2310.{10000 + i}",
                "title": f"Advanced {keyword.title()} Methods for Aerospace Applications",
                "summary": f"We present novel {keyword} techniques applicable to aerospace engineering, focusing on improved efficiency and performance.",
                "authors": [self._get_random_author(), self._get_random_author()],
                "published": self._get_random_date(2015, 2023),
                "updated": self._get_random_date(2015, 2023),
                "category": self._get_random_category(),
                "arxiv_url": f"https://arxiv.org/abs/2310.{10000 + i}",
                "pdf_url": f"https://arxiv.org/pdf/2310.{10000 + i}.pdf"
            }
            papers.append(paper)
        
        return papers
    
    def _get_random_author(self):
        """Return a random author name"""
        first_names = ["Wei", "Maria", "Hassan", "Sophie", "Jun", "Alexandra", "Karthik", "Elena"]
        last_names = ["Zhang", "Rodriguez", "Al-Farsi", "Müller", "Tanaka", "Ivanova", "Patel", "Dubois"]
        
        import random
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _get_random_category(self):
        """Return a random arXiv category relevant to aerospace"""
        categories = [
            "physics.flu-dyn", "cond-mat.mtrl-sci", "cs.RO", "physics.app-ph", 
            "eess.SP", "astro-ph.IM", "math.OC", "cs.CV"
        ]
        
        import random
        return random.choice(categories)
    
    def _get_random_date(self, start_year, end_year):
        """Return a random date between start_year and end_year"""
        import random
        from datetime import datetime, timedelta
        
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_days = random.randrange(days_between_dates)
        
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime("%Y-%m-%d")


class SemanticScholarAPI:
    """Client for Semantic Scholar API"""
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/v1/paper"
        self.api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    
    async def search(self, query, limit=10):
        """Search for papers on Semantic Scholar"""
        # In a real implementation, make API requests
        # For now, return empty list
        return []


class NASATechportAPI:
    """Client for NASA Techport API"""
    def __init__(self):
        self.base_url = "https://techport.nasa.gov/api"
    
    async def search(self, query):
        """Search NASA Techport for technology information"""
        # In a real implementation, make API requests
        # For now, return empty list
        return []


def initialize_api_clients():
    """Initialize all API clients and return them as a dictionary"""
    return {
        "google_patents": GooglePatentsAPI(),
        "uspto": USPTOOpenDataAPI(),
        "arxiv": ArxivAPI(),
        "semantic_scholar": SemanticScholarAPI(),
        "nasa": NASATechportAPI()
    }