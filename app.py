import os
import streamlit as st
from dotenv import load_dotenv
import asyncio

# Import our custom modules
from query_planner import QueryPlanner
from data_collector import AerospaceDataCollector
from analysis_engine import AerospaceAnalysisEngine
from visualization_engine import AerospaceVisualizationEngine
from api_clients import initialize_api_clients
from utils import generate_research_summary, extract_key_innovations

# Load environment variables
load_dotenv()

    
# Safer way to handle asyncio in Streamlit
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Initialize LLM
try:
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        api_key=os.environ.get("GROQ_API_KEY"),
        model_name="llama-3-70b-8192"
    )
except Exception as e:
    st.error(f"Error initializing LLM: {str(e)}")
    llm = None

# Initialize embeddings and vector db
try:
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")
except Exception as e:
    st.error(f"Error initializing embeddings or vector DB: {str(e)}")
    embeddings = None
    vector_db = None

# Initialize API clients
api_clients = initialize_api_clients()

# Initialize components
query_planner = QueryPlanner(llm)
data_collector = AerospaceDataCollector(api_clients)
analysis_engine = AerospaceAnalysisEngine(llm, vector_db)
visualization_engine = AerospaceVisualizationEngine()

async def conduct_research(query, start_date=None, end_date=None, organizations=None, tech_categories=None):
    """Main research pipeline"""
    # Step 1: Plan the query
    search_params = query_planner.decompose_query(query)
    search_params.update({
        "date_range": (start_date, end_date),
        "organizations": organizations,
        "tech_categories": tech_categories
    })
    
    # Step 2: Collect data
    patents = await data_collector.collect_patents(search_params)
    papers = await data_collector.collect_research_papers(search_params)
    tech_specs = await data_collector.collect_technical_specifications(search_params)
    
    # Step 3: Analyze collected data
    all_documents = patents + papers + tech_specs
    specifications = analysis_engine.extract_technical_specifications(all_documents)
    citation_network = analysis_engine.build_citation_network(all_documents)
    trends = analysis_engine.identify_trends(all_documents, search_params["date_range"])
    
    # Step 4: Generate visualizations
    patent_landscape = visualization_engine.generate_patent_landscape(patents)
    citation_viz = visualization_engine.generate_citation_network(citation_network)
    timeline = visualization_engine.generate_comparative_timeline(trends)
    
    # Step 5: Generate research summary
    summary = generate_research_summary(llm, query, all_documents, trends, specifications)
    
    # Return comprehensive results
    return {
        "summary": summary["executive_summary"],
        "methodology": summary["methodology"],
        "innovations": extract_key_innovations(all_documents),
        "visualizations": {
            "patent_landscape": patent_landscape,
            "citation_network": citation_viz,
            "timeline": timeline
        },
        "detailed_findings": summary["detailed_findings"],
        "raw_data": {
            "patents": patents,
            "papers": papers,
            "specifications": specifications
        }
    }

def create_aerospace_research_interface():
    st.title("AeroResearchAgent")
    
    # Query input
    query = st.text_input("Enter your aerospace research query:")
    
    # Advanced options collapsible
    with st.expander("Advanced Search Options"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        organizations = st.multiselect(
            "Filter by Organizations",
            options=["NASA", "Boeing", "Airbus", "SpaceX", "Lockheed Martin", "Northrop Grumman", 
                    "Blue Origin", "General Electric", "Rolls-Royce", "Safran", "Raytheon"]
        )
        
        tech_categories = st.multiselect(
            "Technology Categories",
            options=["Propulsion", "Materials", "Avionics", "Aerodynamics", "Structures", 
                    "Thermal Protection", "Life Support", "Navigation", "Communication", "Fuels"]
        )
    
    # Execute search button
    if st.button("Research") and query:
        with st.spinner("Conducting aerospace research..."):
            try:
                
                # Use the existing event loop instead
                loop = asyncio.get_event_loop()
                results = loop.run_until_complete(conduct_research(query, start_date, end_date, organizations, tech_categories))
                
                # Display results
                st.subheader("Research Results")
                
                # Executive Summary
                st.markdown("### Executive Summary")
                st.write(results["summary"])
                
                # Methodology
                st.markdown("### Research Methodology")
                st.write(results["methodology"])
                
                # Patent Visualization
                st.markdown("### Patent Landscape")
                st.components.v1.html(results["visualizations"]["patent_landscape"], height=600)
                
                # Citation Network
                st.markdown("### Research Citation Network")
                st.components.v1.html(results["visualizations"]["citation_network"], height=500)
                
                # Technology Timeline
                st.markdown("### Technology Timeline")
                st.components.v1.html(results["visualizations"]["timeline"], height=400)
                
                # Detailed Findings
                st.markdown("### Key Technical Innovations")
                for innovation in results["innovations"]:
                    with st.expander(innovation["title"]):
                        st.write(innovation["description"])
                        st.write(f"Source: {innovation['source']}")
                        st.write(f"Date: {innovation['date']}")
                        st.write(f"Technical Readiness Level: {innovation['trl']}")
                
                # Export options
                st.markdown("### Export Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("Download PDF Report", "Report data", "aerospace_report.pdf")
                with col2:
                    st.download_button("Export Raw Data (CSV)", "CSV data", "aerospace_data.csv")
                with col3:
                    st.download_button("Save Interactive HTML", "HTML data", "aerospace_visualizations.html")
                    
            except Exception as e:
                st.error(f"Error conducting research: {str(e)}")

# Run the application
if __name__ == "__main__":
    create_aerospace_research_interface()