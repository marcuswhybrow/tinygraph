Raphael.fn.layer = function(layerName) {
    var layerEndMarker = this.circle(0,0,0);
    layerEndMarker.hide();
    $(layerEndMarker.node).attr('layerId', layerName);
    
    layerEndMarker.bringToFront = function(element) {
        $(element.node).attr('layer', layerName);
        element.insertBefore(this);
    };
    
    layerEndMarker.addAtPosition = function(element) {
        var $element = $(element.node);
        $element
            .attr('layer', layerName)
            .attr('level', element.getGridX() + element.getGridY());
        
        $('*[layer="' + $element.attr('layer') + '"][level!="' + $element.attr('level') + '"]').each(function() {
            if (parseInt($(this).attr('level')) > parseInt($element.attr('level'))) {
                element.insertBefore(this.raphael);
                return false;
            } else {
                element.insertAfter(this.raphael);
            }
        });
    }
    
    return layerEndMarker;
};