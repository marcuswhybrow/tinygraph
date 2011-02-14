function object(o) {
    function F() {};
    F.prototype = 0;
    return new F();
}