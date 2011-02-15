var dashboardConfig = dc = function() {
    this.imagePath = '';
    
    // Tile size and spacing
    this.tileWidth = 128;
    this.tileHeight = 100;
    this.tileSeparation = 2;
    
    // These should only change if the tile shape is redisigned
    this.xOffset = this.tileWidth / 2;
    this.yOffset = this.tileHeight - 20;
    
    // How many tiles there should be in the grid
    this.gridWidth = null;
    this.gridHeight = null;
    
    this.paper = null;
};


// Item
// ---------------------------------------------------------------------------

function Item(paper) {
    this.setPaper(paper);
}

Item.prototype.setRaphaelObj = function(raphaelObj) {
    this.raphaelObj = raphaelObj;
    this.raphaelObj.onAnimation(function() {
        this.wrapper.updateConnections();
    });
    this.raphaelObj.wrapper = this;
};
Item.prototype.setPaper = function(paper) {
    this.paper = (paper === undefined) ? null : paper;
};


// Tile
// ---------------------------------------------------------------------------

function Tile(x, y) {
    this.x = (x === undefined) ? null : x;
    this.y = (y === undefined) ? null : y;
    
    this.xPos = 0;
    this.yPos = 0;
    
    this.setRaphaelObj(dashboardConfig.paper.image(
        dashboardConfig.imagePath + 'tile.png',
        this.getPos().x, this.getPos().y,
        dashboardConfig.tileWidth,
        dashboardConfig.tileHeight
    ));
    
    // This tile has no device on instantiation
    this.device = null;
    
    this.xOffset = dashboardConfig.xOffset;
    this.yOffset = dashboardConfig.yOffset / 2;
}

Tile.prototype = new Item();
Tile.prototype.getPos = function() {
  return {
      x: (this.y * dashboardConfig.xOffset) + (this.y * dashboardConfig.tileSeparation) - (this.x * dashboardConfig.tileSeparation) - (this.x * dashboardConfig.xOffset),
      y: (this.x * dashboardConfig.yOffset / 2) + (this.x * dashboardConfig.tileSeparation / 2)  + (this.y * dashboardConfig.tileSeparation / 2) + (this.y * dashboardConfig.yOffset / 2)
  };
};
Tile.prototype.translate = function(cx, cy) {
    if (this.device != null)
        this.device.translate(cx, cy);
    this.raphaelObj.translate(cx, cy);
};
Tile.prototype.getGridPos = function() {
    return {x: this.x, y: this.y};
};
Tile.prototype.getOriginPos = function() {
    return {
        x: this.raphaelObj.attr('x') + this.xOffset,
        y: this.raphaelObj.attr('y') + this.yOffset
    };
};
Tile.prototype.setOriginPos = function(x, y) {
    this.raphaelObj.attr({
        x: x - this.xOffset,
        y: y - this.yOffset
    });
}
Tile.prototype.getPoints = function() {
    return {
        top: {
            x: this.raphaelObj.attr('x') + this.xOffset,
            y: this.raphaelObj.attr('y')
        },
        left: {
            x: this.raphaelObj.attr('x'),
            y: this.raphaelObj.attr('y') + this.yOffset
        },
        bottom: {
            x: this.raphaelObj.attr('x') + this.xOffset,
            y: this.raphaelObj.attr('y') + 2 * this.yOffset
        },
        right: {
            x: this.raphaelObj.attr('x') + 2 * this.xOffset,
            y: this.raphaelObj.attr('y') + this.yOffset
        }
    };
};
Tile.prototype.addDevice = function(device) {
    this.device = device;
    this.device.tile = this;
    var tileOrigin = this.getOriginPos();
    this.device.setOriginPos(tileOrigin.x, tileOrigin.y);
}


// Device
// ---------------------------------------------------------------------------

function Device(tile) {
    this.tile = (tile === undefined) ? null : tile;
    
    this.moving = false;
    
    this.raphaelObj = null;
}
Device.prototype = new Item();
Device.prototype.translate = function(cx, cy) {
    // Translate all the connectiosn for which this device is the root.
    for (var i in this.interfaces) {
        var connection = this.interfaces[i];
        
        if (connection.fromDevice === this)
            connection.translate(cx, cy);
    }
    // Translate the Raphael object this class wraps.
    this.raphaelObj.translate(cx, cy);
};
Device.prototype.getGridPos = function() {
    return this.tile.getGridPos();
};
Device.prototype.getOriginPos = function() {
    return {
        x: this.raphaelObj.attr('x') + this.xOffset,
        y: this.raphaelObj.attr('y') + this.yOffset
    };
};
Device.prototype.setOriginPos = function(x, y) {
    this.raphaelObj.attr({
        x: x - this.xOffset,
        y: y - this.yOffset
    });
};
Device.prototype.setHighlighted = function(highlight) {
    if (highlight)
        this.raphaelObj.animate({opacity: 0.5}, 100);
    else
        this.raphaelObj.animate({opacity: 1}, 100);
};
Device.prototype.updateConnections = function() {
    for (var i in this.interfaces) {
        var connection = this.interfaces[i],
            fromPoint = connection.fromDevice.getOriginPos(),
            toPoint = connection.toDevice.getOriginPos();
        
        connection.raphaelObj.attr(
            'path',
            'M' + fromPoint.x + ' ' + fromPoint.y + 'L' + toPoint.x + ' ' + toPoint.y
        );
    }
};


// ServerDevice
// ---------------------------------------------------------------------------

function ServerDevice(tile) {
    this.interfaces = new Array();
    
    // Device.call(this, tile);
    this.setRaphaelObj(dashboardConfig.paper.image(
        dashboardConfig.imagePath + 'server.png',
        0, 0,
        72, 96
    ));
    
    this.xOffset = 37;
    this.yOffset = 74;
}

ServerDevice.prototype = new Device();


// SwitchDevice
// ---------------------------------------------------------------------------

function SwitchDevice(tile) {
    this.interfaces = new Array();
    
    // Device.call(this, tile);
    this.setRaphaelObj(dashboardConfig.paper.image(
        dashboardConfig.imagePath + 'switch.png',
        0, 0,
        90, 76
    ));
    
    this.xOffset = 45;
    this.yOffset = 47;
}

SwitchDevice.prototype = new Device();


// function Quadrant(width, height) {
//     this.width = (width === undefined) ? null : width;
//     this.height = (height === undefined) ? null : height;
//     
//     for (var i = 0; i < width; i++) {
//         for (var j = 0; j < height; j++) {
//             // Create each tile
//         }
//     }
// }


// Connection
// ---------------------------------------------------------------------------

function Connection(fromDevice, toDevice) {
    this.fromDevice = (fromDevice === undefined) ? null : fromDevice;
    this.toDevice = (toDevice === undefined) ? null : toDevice;
    
    var fromPoint = fromDevice.getOriginPos(),
        toPoint = toDevice.getOriginPos();
    
    this.setRaphaelObj(dashboardConfig.paper.path(
        'M' + fromPoint.x + ' ' + fromPoint.y +
        'L' + toPoint.x + ' ' + toPoint.y
    ));
    
    this.raphaelObj.attr({
        'stroke-width': 5,
        'stroke-linecap': 'round'
    });
    
    this.fromDevice.interfaces.push(this);
    this.toDevice.interfaces.push(this);
};

Connection.prototype = new Item();
Connection.prototype.getOtherDevice = function(device) {
    return this.fromDevice == device ? toDevice : fromDevice;
}
Connection.prototype.translate = function(cx, cy) {
    this.raphaelObj.translate(cx, cy);
};