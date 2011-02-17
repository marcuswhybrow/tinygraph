(function($) {
    
    // jQuery methods
    $.extend({
        stateBindings: {
            // Stores the current state
            state: null,
            
            // Stores the list of jQuery obejcts which the plugin is managing
            objects: [],
            
            // A method to set the state, and as a result of doing so, alter
            // the bindings active on the managed objects.
            setState: function(newState) {
                var previousState = $.stateBindings.state;
                var i, j, events, eventName, handler;
                
                // For each object this plugin is managing bindings for
                for (i = 0; i < $.stateBindings.objects.length; i++) {
                    var $obj = $.stateBindings.objects[i];
                    
                    // Remove the bindings for the previous state
                    if (previousState != null) {
                        events = $obj.stateBindings[previousState];
                        for (eventName in events) {
                            for (j in events[eventName]) {
                                handler = events[eventName][j];
                                $obj.unbind(eventName, handler);
                            }
                        }
                    }
                    
                    // Add the bindings for the new state
                    events = $obj.stateBindings[newState];
                    for (eventName in events) {
                        for (j in events[eventName]) {
                            handler = events[eventName][j];
                            $obj.bind(eventName, handler);
                        }
                    }
                }
                
                $.stateBindings.state = newState;
            }
        }
    });
    
    // jQuery object methods
    $.fn.extend({
        stateBindings: function(bindings) {
            
            // For each element which this method is executed upon
            return this.each(function() {
                
                // Get the jQuery object and add to it an attribute for
                // storing all of the possible bindings it has
                var $this = $(this);
                $this.stateBindings = {};
                
                // For each state provided
                for (var stateName in bindings) {
                    $this.stateBindings[stateName] = {};
                    
                    // For each event provided for this state
                    var events = bindings[stateName];
                    for (var eventName in events) {
                        // handlers could be an array of functions or a single
                        // function
                        var handlers = events[eventName];
                        
                        // Ensures we always store an array (even if a single
                        // function was provided.)
                        var functionList;
                        if (handlers instanceof Array) {
                            functionList = handlers;
                        } else {
                            functionList = [handlers];
                        }
                        
                        // Stores the handler functions inside of the jQuery
                        // object
                        $this.stateBindings[stateName][eventName] = functionList;
                    }
                }
                
                // Adds the jQuery object to the list of objects the plugin
                // will manage bindings for.
                $.stateBindings.objects.push($this);
            });
        }
    });
})(jQuery);