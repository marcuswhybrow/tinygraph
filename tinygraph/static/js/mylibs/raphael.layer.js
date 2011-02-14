Raphael.fn.layer = function(layerName) {
    var layerEndMarker = this.circle(0,0,0);
    layerEndMarker.hide();
    $(layerEndMarker.node).attr('layerId', layerName);
    
    layerEndMarker.bringToFront = function(item) {
        $(item.raphaelObj.node).attr('layer', layerName);
        item.raphaelObj.insertBefore(this);
    };
    
    layerEndMarker.addAtPosition = function(item) {
        var $element = $(item.raphaelObj.node),
            gridPos = item.getGridPos();
        $element
            .attr('layer', layerName)
            .attr('level', gridPos.x + gridPos.y);
        
        $('*[layer="' + $element.attr('layer') + '"][level!="' + $element.attr('level') + '"]').each(function() {
            if (parseInt($(this).attr('level')) > parseInt($element.attr('level'))) {
                item.raphaelObj.insertBefore(this.raphael);
                return false;
            } else {
                item.raphaelObj.insertAfter(this.raphael);
            }
        });
    }
    
    return layerEndMarker;
};