    /*--------------------------------Search Bar--------------------------------*/

    //search
    var entities_mapping = {};
    d3.csv('data/entities.txt', function(error, data) {
        var entities_nest = d3.nest()
            .key(function(d){return d.entity;})
            .sortKeys(d3.ascending)
            .entries(data);
        var entities = entities_nest 
            .map(function(d){
                return d.key;
            });
        $(function() {
            $("#search").autocomplete({
                source: entities
            });
        });
        entities_nest.forEach(function(d){
            entities_mapping[d.key] = d.values.map(function(d){
                return d.id;
            });
        });
    });

    d3.select("#search").on("search", function() {
        var stories_ids = entities_mapping[this.value]; 
        filtered = map_data.filter(function(s){
            return $.inArray(s.row_index, stories_ids) > -1
           });
        draw_circles(filtered);
        draw_trend(filtered);
    });