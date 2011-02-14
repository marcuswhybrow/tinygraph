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
};

function Item(paper) {
    this.paper = (paper === undefined) ? null : paper;
}

function Tile(paper, x, y) {
    this.constructor(paper);
    this.x = (x === undefined) ? null : x;
    this.y = (y === undefined) ? null : y;
    
    this.xPos = 0;
    this.yPos = 0;
    
    // Create the image for this tile
    this.image = this.paper.image(
        dashboardConfig.imagePath + 'tile.png',
        this.getPos().x, this.getPos().y,
        dashboardConfig.tileWidth,
        dashboardConfig.tileHeight
    );
    
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
    this.image.translate(cx, cy);
};
Tile.prototype.getGridPos = function() {
    return {x: this.x, y: this.y};
};
Tile.prototype.getOriginPos = function() {
    return {
        x: this.image.attr('x') + this.xOffset,
        y: this.image.attr('y') + this.yOffset
    };
};
Tile.prototype.setOriginPos = function(x, y) {
    this.image.attr({
        x: x - this.xOffset,
        y: y - this.yOffset
    });
}
Tile.prototype.getPoints = function() {
    return {
        top: {
            x: this.image.attr('x') + this.xOffset,
            y: this.image.attr('y')
        },
        left: {
            x: this.image.attr('x'),
            y: this.image.attr('y') + this.yOffset
        },
        bottom: {
            x: this.image.attr('x') + this.xOffset,
            y: this.image.attr('y') + 2 * this.yOffset
        },
        right: {
            x: this.image.attr('x') + 2 * this.xOffset,
            y: this.image.attr('y') + this.yOffset
        }
    };
};

function Device(paper, tile) {
    this.constructor(paper);
    this.tile = (tile === undefined) ? null : tile;
}

Device.prototype = new Item();


function ServerDevice(paper, tile) {
    this.constructor(paper, tile);
    this.image = this.paper.image(
        dashboardConfig.imagePath + 'images/server.png',
        0, 0,
        72, 96
    );
}

ServerDevice.prototype = new Device();


function SwitchDevice(paper, tile) {
    this.constructor(paper, tile);
    this.image = this.paperimage(
        'images/switch.png',
        0, 0,
        90, 76
    );
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


Raphael.fn.ServerDevice = ServerDevice;
Raphael.fn.SwitchDevice = SwitchDevice;