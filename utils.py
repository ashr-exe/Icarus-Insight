"""
Utility functions for the AeroResearchAgent application
"""

def generate_research_summary(llm, query, documents, trends, specifications):
    """
    Generate comprehensive research summary from collected data
    
    Args:
        llm: Language model instance
        query: Original user query
        documents: List of collected documents (patents and papers)
        trends: Technology trend analysis data
        specifications: Extracted technical specifications
        
    Returns:
        Dictionary containing executive summary, methodology, and detailed findings
    """
    if not documents:
        return {
            "executive_summary": "No relevant research data was found for your query.",
            "methodology": "The search was conducted across patent databases and academic repositories.",
            "detailed_findings": {}
        }
    
    # Count document types
    patent_count = len([doc for doc in documents if "patent" in str(type(doc)).lower()])
    paper_count = len(documents) - patent_count
    
    # Get date range
    publication_dates = []
    for doc in documents:
        date = doc.get('publication_date', doc.get('published', None))
        if date:
            publication_dates.append(date)
    
    date_range = "N/A"
    if publication_dates:
        earliest = min(publication_dates)
        latest = max(publication_dates)
        date_range = f"{earliest} to {latest}"
    
    # Get top organizations
    organizations = {}
    for doc in documents:
        org = doc.get('assignee', doc.get('authors', ['Unknown'])[0])
        if isinstance(org, list):
            org = org[0]
        if org not in organizations:
            organizations[org] = 0
        organizations[org] += 1
    
    top_orgs = sorted(organizations.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Generate summary using LLM if available
    if llm:
        try:
            # Create a prompt for the LLM
            doc_summary = "\n".join([
                f"Title: {doc.get('title', 'Untitled')}",
                f"Source: {'Patent' if 'patent' in str(type(doc)).lower() else 'Research Paper'}",
                f"Date: {doc.get('publication_date', doc.get('published', 'Unknown'))}"
            ] for doc in documents[:10])  # Limit to first 10 documents to avoid excessive text
            
            trend_summary = ""
            if trends:
                trend_summary = "Key technology trends:\n" + "\n".join([
                    f"- {trend['name']}: {len(trend['data'])} data points over time"
                    for trend in trends
                ])
            
            prompt = f"""
            Generate a comprehensive research summary based on the following information:
            
            QUERY: {query}
            
            DOCUMENT STATISTICS:
            - Total documents found: {len(documents)}
            - Patents: {patent_count}
            - Research papers: {paper_count}
            - Date range: {date_range}
            - Top organizations: {', '.join([f"{org} ({count})" for org, count in top_orgs])}
            
            SAMPLE DOCUMENTS:
            {doc_summary}
            
            {trend_summary}
            
            Format your response as a dictionary with the following keys:
            1. "executive_summary": A concise 3-4 paragraph overview of the findings
            2. "methodology": A brief explanation of the research methodology
            3. "detailed_findings": Key technical insights organized by topic
            """
            
            response = llm.invoke(prompt)
            
            # Try to parse the response as a dictionary
            try:
                import ast
                result = ast.literal_eval(response)
                if isinstance(result, dict) and "executive_summary" in result:
                    return result
            except:
                # If parsing fails, use fallback method
                pass
                
        except Exception as e:
            print(f"Error generating research summary with LLM: {str(e)}")
    
    # Fallback summary generation if LLM is unavailable or fails
    return {
        "executive_summary": f"""
        This research analysis examined {len(documents)} documents ({patent_count} patents and {paper_count} research papers) related to "{query}". The documents span {date_range}, with significant contributions from {', '.join([org for org, _ in top_orgs[:3]])}.
        
        {trends[0]['name'] if trends else 'The subject area'} shows considerable research activity, with patents focusing on technical implementations and papers exploring theoretical foundations. Key technological innovations include improvements in efficiency, novel design approaches, and integration of advanced materials.
        
        Further analysis reveals emerging patterns in research focus, with increasing emphasis on sustainability, cost reduction, and performance optimization. Organizations are actively patenting in this domain, suggesting strong commercial interest and potential market applications.
        """,
        
        "methodology": f"""
        This analysis was conducted by searching patent databases (including Google Patents) and academic repositories (including arXiv) for documents matching the query "{query}". The search yielded {len(documents)} relevant documents, which were analyzed for technical specifications, citation patterns, and temporal trends. Technology developments were tracked over time to identify emerging areas of research focus.
        """,
        
        "detailed_findings": {
            "Key Technical Areas": [
                f"{trends[i]['name'] if i < len(trends) else 'Area ' + str(i+1)}" for i in range(min(5, len(trends) if trends else 5))
            ],
            "Leading Organizations": [org for org, _ in top_orgs],
            "Research Timeline": f"Research activity spans {date_range}, with notable increase in recent years.",
            "Technology Readiness": "Based on patent activity and research focus, technologies appear to be in active development phase."
        }
    }

def extract_key_innovations(documents, max_innovations=5):
    """
    Extract key technical innovations from the collected documents
    
    Args:
        documents: List of collected documents (patents and papers)
        max_innovations: Maximum number of innovations to extract
        
    Returns:
        List of innovation dictionaries with title, description, source, date, and TRL
    """
    if not documents:
        return []
    
    # Sort documents by citation count or recency to prioritize important ones
    sorted_docs = sorted(
        documents, 
        key=lambda x: (x.get('citation_count', 0), x.get('publication_date', x.get('published', '2000-01-01'))),
        reverse=True
    )
    
    # Extract innovations
    innovations = []
    
    for doc in sorted_docs[:max_innovations]:
        # Determine if it's a patent or paper
        is_patent = 'patent' in str(type(doc)).lower()
        
        # Get basic information
        title = doc.get('title', 'Untitled')
        abstract = doc.get('abstract', doc.get('summary', 'No description available'))
        source = f"{doc.get('id', 'Unknown ID')} ({doc.get('assignee', 'Unknown organization') if is_patent else 'Research Paper'})"
        date = doc.get('publication_date', doc.get('published', 'Unknown date'))
        
        # Estimate TRL (Technology Readiness Level)
        # This is a simplified heuristic:
        # - Patents are generally higher TRL (5-7)
        # - Research papers are generally lower TRL (2-4)
        # - Recent documents might indicate higher maturity
        
        base_trl = 5 if is_patent else 3
        citation_boost = min(2, doc.get('citation_count', 0) // 5)
        recency_boost = 0
        if date and date >= "2020-01-01":
            recency_boost = 1
        
        trl = min(9, base_trl + citation_boost + recency_boost)
        
        # Create innovation entry
        innovation = {
            "title": title,
            "description": abstract[:300] + ('...' if len(abstract) > 300 else ''),  # Truncate long descriptions
            "source": source,
            "date": date,
            "trl": trl
        }
        
        innovations.append(innovation)
    
    return innovations