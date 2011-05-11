var dashboardConfig = function() {
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
    
    // The primary key of this item in the database
    this.pk = null;
}

Item.prototype.setRaphaelObj = function(raphaelObj) {
    this.raphaelObj = raphaelObj;
    this.raphaelObj.wrapper = this;
};
Item.prototype.setPaper = function(paper) {
    this.paper = (paper === undefined) ? null : paper;
};
Item.prototype.delete = function() {
    this.raphaelObj.remove();
};


// Tile
// ---------------------------------------------------------------------------

function Tile(x, y, quadrant) {
    this.x = (x === undefined) ? null : x;
    this.y = (y === undefined) ? null : y;
    this.quadrant = (quadrant === undefined) ? null : quadrant;
    
    if (this.quadrant.xPositive === false)
        this.x = -this.x;
    if (this.quadrant.yPositive === false)
        this.y = -this.y;
    
    this.offset = {x: 0, y: 0};
    
    this.xOffset = dashboardConfig.xOffset;
    this.yOffset = dashboardConfig.yOffset;
    
    this.setRaphaelObj(dashboardConfig.paper.image(
        dashboardConfig.imagePath + 'tile.png',
        0,
        0,
        dashboardConfig.tileWidth,
        dashboardConfig.tileHeight
    ));
    
    var x = this.quadrant.x,
        y = this.quadrant.y;
    
    x += this.x * dashboardConfig.xOffset;
    y -= this.x * dashboardConfig.yOffset;
    
    x -= this.y * dashboardConfig.xOffset;
    y -= this.y * dashboardConfig.yOffset;
    
    if (this.quadrant.xPositive === false && this.quadrant.yPositive === false)
        y -= dashboardConfig.yOffset;
    if (this.quadrant.xPositive === true && this.quadrant.yPositive === true)
        y += dashboardConfig.yOffset;
    if (this.quadrant.xPositive === false && this.quadrant.yPositive === true)
        x += dashboardConfig.xOffset;
    if (this.quadrant.xPositive === true && this.quadrant.yPositive === false)
        x -= dashboardConfig.xOffset;
    
    this.setOriginPos(x, y);
    
    dashboardConfig.layers['tiles'].addAtPosition(this);
    
    // This tile has no device on instantiation
    this.device = null;
}

Tile.prototype = new Item();
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
            x: this.raphaelObj.attr('x') + dashboardConfig.xOffset,
            y: this.raphaelObj.attr('y')
        },
        left: {
            x: this.raphaelObj.attr('x'),
            y: this.raphaelObj.attr('y') + dashboardConfig.yOffset
        },
        bottom: {
            x: this.raphaelObj.attr('x') + dashboardConfig.xOffset,
            y: this.raphaelObj.attr('y') + 2 * dashboardConfig.yOffset
        },
        right: {
            x: this.raphaelObj.attr('x') + 2 * dashboardConfig.xOffset,
            y: this.raphaelObj.attr('y') + dashboardConfig.yOffset
        }
    };
};
Tile.prototype.addDevice = function(device) {
    this.device = device;
    this.device.tile = this;
    dashboardConfig.layers['devices'].addAtPosition(this.device);
    var tileOrigin = this.getOriginPos();
    this.device.setOriginPos(tileOrigin.x, tileOrigin.y);
}


// Device
// ---------------------------------------------------------------------------

function Device(tile) {
    this.tile = (tile === undefined) ? null : tile;
    this.moving = false;
    this.raphaelObj = null;
    this.connections = new Array();
}
Device.prototype = new Item();
Device.prototype.translate = function(cx, cy) {
    // Translate all the connectiosn for which this device is the root.
    for (var i = 0; i < this.interfaces.length; i++) {
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
    for (var i = 0; i < this.interfaces.length; i++) {
        var connection = this.interfaces[i],
            fromPoint = connection.fromDevice.getOriginPos(),
            toPoint = connection.toDevice.getOriginPos();
        
        connection.raphaelObj.attr(
            'path',
            'M' + fromPoint.x + ' ' + fromPoint.y + 'L' + toPoint.x + ' ' + toPoint.y
        );
    }
};
Device.prototype.connectTo = function(toDevice) {
    var connection = new Connection(this, toDevice);;
    this.connections.push(connection);
    toDevice.connections.push(connection);
    return connection;
};
Device.prototype.deleteSuper = Device.prototype.delete;
Device.prototype.delete = function() {
    this.deleteSuper();
    
    // Delete all of this devices connections with other devices.
    for (var i = 0; i < this.interfaces.length; i++)
        this.interfaces[i].delete();
}


// ServerDevice
// ---------------------------------------------------------------------------

function ServerDevice(pk) {
    this.interfaces = new Array();
    
    this.pk = pk;
    
    this.setRaphaelObj(dashboardConfig.paper.image(
        dashboardConfig.imagePath + 'server.png',
        0, 0,
        72, 96
    ));
    
    this.raphaelObj.onAnimation(function() {
        this.wrapper.updateConnections();
    });
    
    this.xOffset = 37;
    this.yOffset = 74;
}

ServerDevice.prototype = new Device();


// SwitchDevice
// ---------------------------------------------------------------------------

function SwitchDevice(pk) {
    this.interfaces = new Array();
    
    this.pk = pk;
    
    // Device.call(this, tile);
    this.setRaphaelObj(dashboardConfig.paper.image(
        dashboardConfig.imagePath + 'switch.png',
        0, 0,
        90, 76
    ));
    
    this.raphaelObj.onAnimation(function() {
        this.wrapper.updateConnections();
    });
    
    this.xOffset = 45;
    this.yOffset = 47;
}

SwitchDevice.prototype = new Device();


// Quadrant
// ---------------------------------------------------------------------------

function Quadrant(width, height, xPositive, yPositive) {
    this.width = (width === undefined) ? null : width;
    this.height = (height === undefined) ? null : height;
    this.xPositive = (xPositive === undefined) ? null : xPositive;
    this.yPositive = (yPositive === undefined) ? null : yPositive;
    
    this.tiles = new Array(this.width);
    
    this.x = dashboardConfig.origin.x;
    this.y = dashboardConfig.origin.y;
    
    // Add the tiles to the screen
    for (var x = 1; x <= this.width; x++) {
        this.tiles[x] = new Array(this.height);
        for (var y = 1; y <= this.height; y++)
            this.tiles[x][y] = new Tile(x, y, this);
    }
}

Quadrant.prototype.translate = function(cx, cy) {
    for (var x = 1; x <= this.width; x++) {
        for (var y = 1; y <= this.height; y++) {
            this.tiles[x][y].translate(cx, cy);
        }
    }
    this.x += cx;
    this.y += cy;
};


// Connection
// ---------------------------------------------------------------------------

function Connection(fromDevice, toDevice, pk) {
    this.fromDevice = (fromDevice === undefined) ? null : fromDevice;
    this.toDevice = (toDevice === undefined) ? null : toDevice;
    
    this.pk = pk;
    
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
    
    dashboardConfig.layers['connections'].bringToFront(this);
    
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