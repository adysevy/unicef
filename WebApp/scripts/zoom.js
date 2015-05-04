//zoom and pan
    var zoom = d3.behavior.zoom()
        .on("zoom",function() {
            g.attr("transform","translate("+ 
                d3.event.translate.join(",")+")scale("+d3.event.scale+")");
            g.selectAll("circle")
                .attr("d", path.projection(projection));
            g.selectAll("path")  
                .attr("d", path.projection(projection)); 
    });
         
    svg.call(zoom);