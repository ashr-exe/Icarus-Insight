class AerospaceVisualizationEngine:
    """Engine for generating aerospace data visualizations"""
    
    def __init__(self):
        self.d3_templates = {
            "patent_landscape": self._patent_landscape_template(),
            "citation_network": self._citation_network_template(),
            "technology_timeline": self._technology_timeline_template(),
            "geographic_distribution": self._geographic_distribution_template()
        }
    
    def generate_patent_landscape(self, patent_data):
        """Generate interactive patent landscape visualization"""
        import json
        
        # Process the patent data
        processed_data = []
        
        # Group patents by company (assignee) and IPC code
        company_groups = {}
        
        for patent in patent_data:
            assignee = patent.get('assignee', 'Unknown')
            if assignee not in company_groups:
                company_groups[assignee] = []
            company_groups[assignee].append(patent)
        
        # Process each company group
        for company, patents in company_groups.items():
            # Count patents by IPC code
            ipc_counts = {}
            for patent in patents:
                ipc_codes = patent.get('ipc_codes', [])
                for ipc in ipc_codes:
                    if ipc not in ipc_counts:
                        ipc_counts[ipc] = 0
                    ipc_counts[ipc] += 1
            
            # Add to processed data
            processed_data.append({
                "company": company,
                "total_patents": len(patents),
                "ipc_breakdown": [{"ipc": ipc, "count": count} for ipc, count in ipc_counts.items()]
            })
        
        # Insert the data into the template
        visualization = self.d3_templates["patent_landscape"].replace(
            '"__DATA_PLACEHOLDER__"', 
            json.dumps(processed_data)
        )
        
        return visualization
    
    def generate_citation_network(self, citation_data):
        """Generate interactive citation network"""
        import json
        
        # Format the data for D3.js force-directed graph
        formatted_data = {
            "nodes": citation_data["nodes"],
            "links": citation_data["links"]
        }
        
        # Insert the data into the template
        visualization = self.d3_templates["citation_network"].replace(
            '"__DATA_PLACEHOLDER__"', 
            json.dumps(formatted_data)
        )
        
        return visualization
    
    def generate_comparative_timeline(self, tech_developments):
        """Generate timeline of technology developments"""
        import json
        
        # Process trend data for timeline visualization
        timeline_data = []
        
        for trend in tech_developments:
            for data_point in trend["data"]:
                timeline_data.append({
                    "category": trend["name"],
                    "year": data_point["year"],
                    "value": (data_point["count"] / data_point["total_docs"]) * 100 if data_point["total_docs"] > 0 else 0,
                    "absoluteValue": data_point["count"]
                })
        
        # Insert the data into the template
        visualization = self.d3_templates["technology_timeline"].replace(
            '"__DATA_PLACEHOLDER__"', 
            json.dumps(timeline_data)
        )
        
        return visualization
    
    def _patent_landscape_template(self):
        """Template for patent landscape visualization"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Aerospace Patent Landscape</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; }
                .bar { fill: steelblue; }
                .bar:hover { fill: #003366; }
                .grid line { stroke: #ddd; stroke-opacity: 0.7; shape-rendering: crispEdges; }
                .grid path { stroke-width: 0; }
                .axis text { font-size: 11px; }
                .axis path, .axis line { fill: none; stroke: #000; shape-rendering: crispEdges; }
                .legend { font-size: 12px; }
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                // Data
                const data = "__DATA_PLACEHOLDER__";
                
                // Dimensions
                const margin = {top: 40, right: 150, bottom: 60, left: 80},
                      width = 800 - margin.left - margin.right,
                      height = 500 - margin.top - margin.bottom;
                
                // Create SVG
                const svg = d3.select("#chart")
                    .append("svg")
                      .attr("width", width + margin.left + margin.right)
                      .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                      .attr("transform", `translate(${margin.left},${margin.top})`);
                
                // Add title
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", -20)
                    .attr("text-anchor", "middle")
                    .style("font-size", "16px")
                    .style("font-weight", "bold")
                    .text("Aerospace Patent Landscape by Company");
                
                // Create scales
                const xScale = d3.scaleBand()
                    .domain(data.map(d => d.company))
                    .range([0, width])
                    .padding(0.3);
                
                const yScale = d3.scaleLinear()
                    .domain([0, d3.max(data, d => d.total_patents) * 1.1])
                    .range([height, 0]);
                
                // Color scale for IPC codes
                const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
                
                // Draw bars
                data.forEach(company => {
                    let yOffset = 0;
                    company.ipc_breakdown.forEach(ipc => {
                        svg.append("rect")
                            .attr("x", xScale(company.company))
                            .attr("y", yScale(yOffset + ipc.count))
                            .attr("width", xScale.bandwidth())
                            .attr("height", height - yScale(ipc.count))
                            .attr("fill", colorScale(ipc.ipc))
                            .attr("stroke", "white")
                            .attr("class", "bar")
                            .append("title")
                            .text(`${company.company}\\n${ipc.ipc}: ${ipc.count} patents`);
                        
                        yOffset += ipc.count;
                    });
                });
                
                // Add axes
                svg.append("g")
                    .attr("transform", `translate(0,${height})`)
                    .call(d3.axisBottom(xScale))
                    .selectAll("text")
                        .attr("transform", "rotate(-45)")
                        .style("text-anchor", "end")
                        .attr("dx", "-.8em")
                        .attr("dy", ".15em");
                
                svg.append("g")
                    .call(d3.axisLeft(yScale));
                
                // Add grid lines
                svg.append("g")
                    .attr("class", "grid")
                    .call(d3.axisLeft(yScale)
                        .tickSize(-width)
                        .tickFormat("")
                    );
                
                // Add axis labels
                svg.append("text")
                    .attr("transform", `translate(${width/2}, ${height + 50})`)
                    .style("text-anchor", "middle")
                    .text("Company");
                
                svg.append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", -60)
                    .attr("x", -(height / 2))
                    .attr("text-anchor", "middle")
                    .text("Number of Patents");
                
                // Add legend
                const allIPCs = [];
                data.forEach(company => {
                    company.ipc_breakdown.forEach(ipc => {
                        if (!allIPCs.includes(ipc.ipc)) {
                            allIPCs.push(ipc.ipc);
                        }
                    });
                });
                
                const legend = svg.append("g")
                    .attr("transform", `translate(${width + 20}, 0)`);
                
                allIPCs.forEach((ipc, i) => {
                    const legendRow = legend.append("g")
                        .attr("transform", `translate(0, ${i * 20})`);
                    
                    legendRow.append("rect")
                        .attr("width", 10)
                        .attr("height", 10)
                        .attr("fill", colorScale(ipc));
                    
                    legendRow.append("text")
                        .attr("x", 20)
                        .attr("y", 10)
                        .attr("text-anchor", "start")
                        .style("font-size", "12px")
                        .text(ipc);
                });
            </script>
        </body>
        </html>
        """
    
    def _citation_network_template(self):
        """Template for citation network visualization"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Aerospace Citation Network</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; overflow: hidden; }
                .links line { stroke: #999; stroke-opacity: 0.6; }
                .nodes circle { stroke: #fff; stroke-width: 1.5px; }
                .node-label { font-size: 10px; }
                .paper { fill: #69b3a2; }
                .patent { fill: #4682b4; }
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                // Data
                const data = "__DATA_PLACEHOLDER__";
                
                // Dimensions
                const width = 800,
                      height = 500;
                
                // Create SVG
                const svg = d3.select("#chart")
                    .append("svg")
                      .attr("width", width)
                      .attr("height", height);
                
                // Add title
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", 20)
                    .attr("text-anchor", "middle")
                    .style("font-size", "16px")
                    .style("font-weight", "bold")
                    .text("Aerospace Research Citation Network");
                
                // Create force simulation
                const simulation = d3.forceSimulation(data.nodes)
                    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(20));
                
                // Create links
                const link = svg.append("g")
                    .selectAll("line")
                    .data(data.links)
                    .enter().append("line")
                      .attr("class", "links")
                      .attr("stroke-width", d => Math.sqrt(1));
                
                // Create nodes
                const node = svg.append("g")
                    .selectAll("circle")
                    .data(data.nodes)
                    .enter().append("circle")
                      .attr("class", "nodes")
                      .attr("r", 7)
                      .attr("class", d => d.type)
                      .call(d3.drag()
                          .on("start", dragstarted)
                          .on("drag", dragged)
                          .on("end", dragended));
                
                // Add tooltips
                node.append("title")
                    .text(d => `${d.title}\\n${d.organization}\\n${d.date}`);
                
                // Add node labels
                const labels = svg.append("g")
                    .selectAll("text")
                    .data(data.nodes)
                    .enter().append("text")
                      .attr("class", "node-label")
                      .attr("dx", 12)
                      .attr("dy", ".35em")
                      .text(d => d.title.substring(0, 20) + (d.title.length > 20 ? "..." : ""));
                
                // Add legend
                const legend = svg.append("g")
                    .attr("transform", "translate(20, 40)");
                
                // Patent node
                legend.append("circle")
                    .attr("r", 7)
                    .attr("class", "patent")
                    .attr("cx", 0)
                    .attr("cy", 0);
                
                legend.append("text")
                    .attr("x", 15)
                    .attr("y", 4)
                    .text("Patent");
                
                // Paper node
                legend.append("circle")
                    .attr("r", 7)
                    .attr("class", "paper")
                    .attr("cx", 0)
                    .attr("cy", 25);
                
                legend.append("text")
                    .attr("x", 15)
                    .attr("y", 29)
                    .text("Research paper");
                
                // Update positions on simulation tick
                simulation.on("tick", () => {
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node
                        .attr("cx", d => d.x = Math.max(10, Math.min(width - 10, d.x)))
                        .attr("cy", d => d.y = Math.max(10, Math.min(height - 10, d.y)));
                    
                    labels
                        .attr("x", d => d.x)
                        .attr("y", d => d.y);
                });
                
                // Drag functions
                function dragstarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }
                
                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }
                
                function dragended(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            </script>
        </body>
        </html>
        """
    
    def _technology_timeline_template(self):
        """Template for technology timeline visualization"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Aerospace Technology Timeline</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; }
                .line { fill: none; stroke-width: 3px; }
                .grid line { stroke: #ddd; stroke-opacity: 0.7; shape-rendering: crispEdges; }
                .grid path { stroke-width: 0; }
                .axis text { font-size: 11px; }
                .axis path, .axis line { fill: none; stroke: #000; shape-rendering: crispEdges; }
                .legend-item { font-size: 12px; }
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                // Data
                const data = "__DATA_PLACEHOLDER__";
                
                // Dimensions
                const margin = {top: 40, right: 150, bottom: 60, left: 80},
                      width = 800 - margin.left - margin.right,
                      height = 400 - margin.top - margin.bottom;
                
                // Create SVG
                const svg = d3.select("#chart")
                    .append("svg")
                      .attr("width", width + margin.left + margin.right)
                      .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                      .attr("transform", `translate(${margin.left},${margin.top})`);
                
                // Add title
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", -20)
                    .attr("text-anchor", "middle")
                    .style("font-size", "16px")
                    .style("font-weight", "bold")
                    .text("Technology Trend Evolution Over Time");
                
                // Process data
                const categories = Array.from(new Set(data.map(d => d.category)));
                const years = Array.from(new Set(data.map(d => d.year))).sort();
                
                // Create scales
                const xScale = d3.scalePoint()
                    .domain(years)
                    .range([0, width])
                    .padding(0.5);
                
                const yScale = d3.scaleLinear()
                    .domain([0, 100])
                    .range([height, 0]);
                
                // Color scale
                const colorScale = d3.scaleOrdinal(d3.schemeCategory10)
                    .domain(categories);
                
                // Create line generator
                const line = d3.line()
                    .x(d => xScale(d.year))
                    .y(d => yScale(d.value))
                    .curve(d3.curveMonotoneX);
                
                // Group data by category
                const dataByCategory = {};
                categories.forEach(category => {
                    dataByCategory[category] = data.filter(d => d.category === category);
                });
                
                // Draw lines
                Object.entries(dataByCategory).forEach(([category, values]) => {
                    // Ensure the values are sorted by year
                    values.sort((a, b) => a.year - b.year);
                    
                    svg.append("path")
                        .datum(values)
                        .attr("class", "line")
                        .attr("d", line)
                        .attr("stroke", colorScale(category));
                });
                
                // Add circles for data points
                categories.forEach(category => {
                    svg.selectAll(`.circle-${category.replace(/\\s+/g, '-')}`)
                        .data(dataByCategory[category])
                        .enter().append("circle")
                          .attr("cx", d => xScale(d.year))
                          .attr("cy", d => yScale(d.value))
                          .attr("r", 5)
                          .attr("fill", colorScale(category))
                          .append("title")
                          .text(d => `${d.category} (${d.year})\\nPercentage: ${d.value.toFixed(1)}%\\nCount: ${d.absoluteValue}`);
                });
                
                // Add axes
                svg.append("g")
                    .attr("transform", `translate(0,${height})`)
                    .call(d3.axisBottom(xScale));
                
                svg.append("g")
                    .call(d3.axisLeft(yScale));
                
                // Add grid lines
                svg.append("g")
                    .attr("class", "grid")
                    .call(d3.axisLeft(yScale)
                        .tickSize(-width)
                        .tickFormat("")
                    );
                
                // Add axis labels
                svg.append("text")
                    .attr("transform", `translate(${width/2}, ${height + 40})`)
                    .style("text-anchor", "middle")
                    .text("Year");
                
                svg.append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", -60)
                    .attr("x", -(height / 2))
                    .attr("text-anchor", "middle")
                    .text("Prevalence (%)");
                
                // Add legend
                const legend = svg.append("g")
                    .attr("transform", `translate(${width + 20}, 0)`);
                
                categories.forEach((category, i) => {
                    const legendRow = legend.append("g")
                        .attr("transform", `translate(0, ${i * 20})`);
                    
                    legendRow.append("line")
                        .attr("x1", 0)
                        .attr("y1", 5)
                        .attr("x2", 20)
                        .attr("y2", 5)
                        .attr("stroke-width", 3)
                        .attr("stroke", colorScale(category));
                    
                    legendRow.append("text")
                        .attr("x", 30)
                        .attr("y", 9)
                        .attr("class", "legend-item")
                        .text(category);
                });
            </script>
        </body>
        </html>
        """
    
    def _geographic_distribution_template(self):
        """Template for geographic distribution visualization"""
        # This is a placeholder for future implementation
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Geographic Distribution</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script src="https://d3js.org/d3-geo.v2.min.js"></script>
            <script src="https://d3js.org/d3-geo-projection.v3.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; }
                .countries { fill: #f0f0f0; stroke: #ccc; stroke-width: 0.5px; }
                .points { fill: steelblue; stroke: #fff; stroke-width: 0.5px; }
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                // Placeholder for geographic visualization
                const svg = d3.select("#chart")
                    .append("svg")
                      .attr("width", 800)
                      .attr("height", 500);
                
                svg.append("text")
                    .attr("x", 400)
                    .attr("y", 250)
                    .attr("text-anchor", "middle")
                    .text("Geographic Distribution Visualization (placeholder)");
            </script>
        </body>
        </html>
        """