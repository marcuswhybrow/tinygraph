(function($) {
    var $window = $(window);

    // Accepts a function or an array of functions an calls an
    // anonymous function with each as the only argument.
    function iterate(handlerInput, f) {
        if (handlerInput instanceof Array) {
            for (var i = 0; i < handlerInput.length; i++) {
                f(handlerInput[i]);
            }
        } else {
            f(handlerInput);
        }
    }
    
    Array.prototype.contains = function(obj) {
        var i = this.length;
        while (i--) {
            if (this[i] === obj) {
                return true;
            }
        }
        return false;
    };
    
    Array.prototype.remove = function(element) {
        for (var i = 0; i < this.length; i++) {
            if (this[i] === element) {
                this.splice(i, 1);
            }
        }
    }
    
    Array.prototype.subtract = function(element) {
        // Create a new version of the array
        var a = this.slice();
        a.remove(element);
        return a;
    }
    
    function getNames(str) {
        if (str.length === 0)
            return [];
        
        return str.split(' ');
    }
    
    function forStates($obj, states, f) {
        for (var i = 0; i < states.length; i++) {
            var state = states[i];
            var events = $obj.stateBindings[state];
            for (eventName in events) {
                handlers = events[eventName];
                iterate(handlers, function(handler) {
                    f(eventName+'.stateBindings.'+state, handler);
                });
            }
        }
    }
    
    function subtract(arrayOne, arrayTwo) {
        var newArray = new Array();
        var count = 0;
        for (var i = 0; i < arrayOne.length; i++) {
            if (! arrayTwo.contains(arrayOne[i])) {
                newArray[count++] = arrayOne[i];
            }
        }
        return newArray;
    }

    // jQuery methods
    $.extend({
        stateBindings: {
            // Stores the current state
            activeStates: [],

            // Stores the list of jQuery obejcts which the plugin is managing
            objects: [],

            liveObjects: [],
            
            hierarchySeparator: '>',

            // A method to set the state, and as a result of doing so, alter
            // the bindings active on the managed objects.
            setState: function(newState) {
                var newStates;
                if (newState instanceof Array) {
                    newStates = newState;
                } else {
                    newStates = getNames(newState);
                }
                var previousStates = $.stateBindings.activeStates;
                var i, j, events, eventName, handlers;
                
                var statesToDisable = subtract(previousStates, newStates);
                var statesToEnable = subtract(newStates, previousStates);

                // Handle the live bindings
                for(i = 0; i < $.stateBindings.liveObjects.length; i++) {
                    var $liveObj = $.stateBindings.liveObjects[i];
                    
                    forStates($liveObj, statesToDisable, function(eventName, handler) {
                        $liveObj.die(eventName, handler);
                    });
                    
                    forStates($liveObj, statesToEnable, function(eventName, handler) {
                        $liveObj.live(eventName, handler);
                    });
                }

                // Handle the normal bindings
                for (i = 0; i < $.stateBindings.objects.length; i++) {
                    var $obj = $.stateBindings.objects[i];
                    
                    forStates($obj, statesToDisable, function(eventName, handler) {
                        $obj.unbind(eventName, handler);
                    });
                    
                    forStates($obj, statesToEnable, function(eventName, handler) {
                        $obj.bind(eventName, handler);
                    });
                }
                
                $.stateBindings.activeStates = newStates;
                
                for (var i = 0; i < statesToDisable.length; i++) {
                    $window.trigger(statesToDisable[i]+'.stateDisabled');
                }
                
                for (var i = 0; i < statesToEnable.length; i++) {
                    $window.trigger(statesToEnable[i]+'.stateEnabled');
                }
            },
            
            // Actives a state, as long as its parent state is already active
            addState: function(state) {
                if ($.stateBindings.activeStates.contains(state)) {
                    return true;
                } else {
                    
                    // Find the right most hirerarchy separator character
                    var rightMostIndex = -1;
                    while(true) {
                        var index = state.indexOf(this.hierarchySeparator, rightMostIndex+1);
                        if (index > -1)
                            rightMostIndex = index;
                        else
                            break;
                    }
                    
                    var parentState = state.substr(0, rightMostIndex);
                    if (rightMostIndex == -1 || $.stateBindings.isEnabled(parentState)) {
                        var newStates = $.stateBindings.activeStates.concat([state]);
                        $.stateBindings.setState(newStates);
                        return true;
                    }
                }
                return false;
            },
            
            // Removes any state which starts with the given state name
            removeState: function(state) {
                if ($.stateBindings.isEnabled(state)) {
                    var newStates = $.stateBindings.activeStates.subtract(state);
            
                    // Also remove any child states of this state.
                    var tmpStates = new Array();
                    var count = 0;
                    for (var i = 0; i < newStates.length; i++) {
                        if (newStates[i].indexOf(state+this.hierarchySeparator) != 0)
                            tmpStates[count++] = newStates[i];
                    }
            
                    $.stateBindings.setState(tmpStates);
                    return true;
                }
                return false;
            },
            
            toggleState: function(state) {
                if ($.stateBindings.activeStates.contains(state)) {
                    return $.stateBindings.removeState(state) === false;
                } else {
                    return $.stateBindings.addState(state);
                }
            },
            
            isEnabled: function(state) {
                return $.stateBindings.activeStates.contains(state);
            }
        }
    });

    // jQuery object methods
    $.fn.extend({
        stateBindings: function(bindings, options) {
            var stateName, stateNames, finalBindings, events, eventName,
                eventNames, finalEvents;
            
            // Split apart state and event names.
            finalBindings = {};
            for (stateName in bindings) {
                stateNames = getNames(stateName);
                for (var i = 0; i < stateNames.length; i++) {
                    events = bindings[stateName];
                    finalEvents = {};
                    for(eventName in events) {
                        eventNames = getNames(eventName);
                        for (var j = 0; j < eventNames.length; j ++) {
                            finalEvents[eventNames[j]] =
                                bindings[stateName][eventName];
                        }
                    }
                    finalBindings[stateNames[i]] = finalEvents;
                }
            }
            
            var defaults = {
                live: false
            };
            
            var opts = $.extend(defaults, options);
            
            if (opts.live === true) {
                this.stateBindings = finalBindings;
                $.stateBindings.liveObjects.push(this);
            } else {
                // For each element which this method is executed upon
                return this.each(function() {
                    var $this = $(this);
                    $this.stateBindings = finalBindings;
                    $.stateBindings.objects.push($this);
                });
            }
        }
    });
})(jQuery);