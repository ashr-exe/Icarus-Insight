class QueryPlanner:
    def __init__(self, llm):
        self.llm = llm
        self.aerospace_ipc_codes = {
            "B64": "Aircraft, aviation, cosmonautics",
            "B64C": "Aeroplanes; Helicopters",
            "B64D": "Equipment for fitting in or to aircraft",
            "B64F": "Ground or aircraft-carrier-deck installations",
            "B64G": "Cosmonautics; Vehicles or equipment therefor",
            "F02K": "Jet propulsion plants",
            "F03H": "Producing a reactive propulsive thrust",
            "G01C": "Measuring distances, levels or bearings; Surveying; Navigation",
            "G01S": "Radio direction-finding, navigation",
            "G05D1": "Control of position or course in two dimensions or three dimensions"
        }
    
    def decompose_query(self, user_query):
        """Break down a complex aerospace research query into searchable components"""
        if self.llm is None:
            # Fallback if LLM is not available
            return self._fallback_decompose(user_query)
        
        try:
            prompt = f"""
            Decompose the following aerospace research query into searchable components:
            
            Query: {user_query}
            
            Identify:
            1. Key technical terms (list of 3-8 terms)
            2. Relevant aerospace subsystems (list 2-4)
            3. Potential IPC/CPC codes from this list: {list(self.aerospace_ipc_codes.keys())}
            4. Date range of interest (if implied)
            5. Relevant companies/organizations (list if implied)
            
            Format your response as a Python dictionary with keys: "keywords", "subsystems", "ipc_codes", "implied_date_range", "organizations"
            """
            
            response = self.llm.invoke(prompt)
            
            # Parse the response to extract a dictionary
            try:
                # Try to execute the response as Python code (safely)
                import ast
                result = ast.literal_eval(response)
                if not isinstance(result, dict):
                    raise ValueError("Response is not a dictionary")
                return result
            except:
                # Fallback to regex parsing if that fails
                return self._parse_response_with_regex(response)
        except Exception as e:
            print(f"Error in decompose_query: {str(e)}")
            return self._fallback_decompose(user_query)
    
    def _fallback_decompose(self, user_query):
        """Fallback method if LLM is unavailable or fails"""
        # Extract keywords from the query
        words = user_query.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in ['what', 'when', 'where', 'which', 'research', 'find', 'about', 'with', 'that', 'this', 'these', 'those']]
        
        # Default search parameters
        return {
            "keywords": keywords[:5],  # Limit to 5 keywords
            "subsystems": [],
            "ipc_codes": ["B64G"],  # Default to cosmonautics
            "implied_date_range": ("2010-01-01", "2024-12-31"),  # Default to recent decade
            "organizations": []
        }
    
    def _parse_response_with_regex(self, response):
        """Parse LLM response with regex if structured parsing fails"""
        import re
        
        result = {
            "keywords": [],
            "subsystems": [],
            "ipc_codes": [],
            "implied_date_range": None,
            "organizations": []
        }
        
        # Extract keywords
        keyword_match = re.search(r'keywords.*?[\[{]([^}\]]+)[}\]]', response, re.DOTALL)
        if keyword_match:
            keywords_str = keyword_match.group(1)
            result["keywords"] = [k.strip().strip('"\'') for k in keywords_str.split(',')]
        
        # Extract IPC codes
        ipc_match = re.search(r'ipc_codes.*?[\[{]([^}\]]+)[}\]]', response, re.DOTALL)
        if ipc_match:
            ipc_str = ipc_match.group(1)
            result["ipc_codes"] = [k.strip().strip('"\'') for k in ipc_str.split(',')]
        
        # Extract organizations
        org_match = re.search(r'organizations.*?[\[{]([^}\]]+)[}\]]', response, re.DOTALL)
        if org_match:
            org_str = org_match.group(1)
            result["organizations"] = [k.strip().strip('"\'') for k in org_str.split(',')]
        
        return result
    
    def generate_search_strategy(self, components):
        """Create optimal search strategies for different data sources"""
        # Generate search strings for different APIs
        strategies = {}
        
        # Google Patents search strategy
        patent_keywords = " OR ".join([f'"{kw}"' for kw in components["keywords"]])
        ipc_codes = " OR ".join([f'cpc:"{code}"' for code in components["ipc_codes"]])
        
        strategies["google_patents"] = f'({patent_keywords}) AND ({ipc_codes})'
        
        # arXiv search strategy
        arxiv_query = " AND ".join([f'"{kw}"' for kw in components["keywords"]])
        
        categories = []
        # Map subsystems to arXiv categories
        subsystem_to_category = {
            "propulsion": "physics.flu-dyn",
            "materials": "cond-mat.mtrl-sci",
            "aerodynamics": "physics.flu-dyn",
            "structures": "physics.app-ph",
            "avionics": "eess.SP"
        }
        
        for subsystem in components.get("subsystems", []):
            if subsystem.lower() in subsystem_to_category:
                categories.append(subsystem_to_category[subsystem.lower()])
        
        if categories:
            arxiv_cat_filter = " OR ".join([f'cat:{cat}' for cat in categories])
            strategies["arxiv"] = f'({arxiv_query}) AND ({arxiv_cat_filter})'
        else:
            strategies["arxiv"] = arxiv_query
        
        return strategies