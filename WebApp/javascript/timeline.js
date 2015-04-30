/*----------------------Global Variables - Trend Chart-----------------------*/

    //defining the size for the graph
    var margin_trend = {top: 20, right: 20, bottom: 30, left: 50};
    var width_trend = 900 - margin_trend.left - margin_trend.right;
    var height_trend = 120 - margin_trend.top - margin_trend.bottom;

    var x = d3.time.scale()
        .range([0, width_trend]);

    var y = d3.scale.linear()
        .range([height_trend, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .ticks(4)
        .orient("left");

    //defining a function which gets a string and parse it into a real date type
    var parseDate = d3.time.format("%m/%d/%y").parse;

    //defining a line function which gets our stories_by_date data and returns x and y
    // arrays in the mapping defined above
    var line = d3.svg.line()
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d.values); });

    var stories_by_date;

    /*----------------------End Global Variables - Trend Chart-----------------------*/ 

    //drawing the trend chart
    function draw_trend(filtered_data) {

        //removing the current SVG of the trend graph
        d3.select("#trend").select("svg").remove();

        //creating a new SVG in the proper size
        var svg_trend = d3.select("#trend").append("svg")
            .attr("width", width_trend + margin_trend.left + margin_trend.right)
            .attr("height", height_trend + margin_trend.top + margin_trend.bottom)
            .append("g")
            .attr("transform", "translate(" + margin_trend.left + "," + margin_trend.top + ")");

        //creating a nested data structure out of the filtered data
        // var stories_by_date = d3.nest()
        stories_by_date = d3.nest()
            .key(function(d) { return (d.date.substring(0, 8));})
            .rollup(function(d) { 
               return d3.sum(d, function(g) {return 1; });
            }).entries(filtered_data);

        //adding a real (not string) date field to stories_by_date
        stories_by_date.forEach(function(d){
            d.date = parseDate(d.key);
        });

        //sort the data according to the date field
        stories_by_date.sort(function(a, b){
            if (a.date<b.date){
                return -1;
            }
            if (b.date<a.date){
                return 1;
            }
            return 0;
        });
    
        //defining the axes
        x.domain(d3.extent(stories_by_date, function(d) { return d.date; }));
        y.domain(d3.extent(stories_by_date, function(d) { return d.values; }));

        //adding the axes to the trend SVG
        svg_trend.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height_trend + ")")
            .call(xAxis);

        svg_trend.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0-margin_trend.left)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("# Stories");

        //drawing the line accrording to stories_by_date
        //using the line function defined in the global scope   
        svg_trend.append("path")
            .attr("class", "line")
            .attr("d", line(stories_by_date));  
    // }        
        // starting timeline brush here
        var brush = d3.svg.brush()
            .x(x)
            .extent([100, 700])
            .on("brushstart", brushstart)
            .on("brush", brushmove)
            .on("brushend", brushend);
        var arc = d3.svg.arc()
            .outerRadius(height_trend / 2)
            .startAngle(0)
            .endAngle(function(d, i) { return i ? -Math.PI : Math.PI; });
        var brushg = svg_trend.append('g')
            .attr('class', 'brush')
            // .style('fill', '#1CACE2')
            .call(brush);
        brushg.selectAll(".resize").append("path")
            .attr("transform", "translate(0," +  height_trend / 2 + ")")
            .attr("d", arc)
            .style("opacity", "0.7");
        brushg.selectAll("rect")
            .attr("height", height_trend);

        // initializing css styling for brush and line segments
        brushstart();
        brushmove();
        function brushstart() {
            svg.classed("selecting", true);
          }
        function brushmove() {
            var s = brush.extent();
            // circle.classed("selected", function(d) { return s[0] <= d && d <= s[1]; });
          }
        function brushend() {
            svg.classed("selecting", !d3.event.target.empty());
          }
        //ending timeline brush 
    }   