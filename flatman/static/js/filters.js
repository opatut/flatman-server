var module = angular.module('app.filters', []);

module.filter('gravatar', function() {
    return function(input, size) {
        return "http://www.gravatar.com/avatar/" + input + "?d=identicon&s=" + (size || 32);
    };
});

module.filter('from_to', function() {
    return function(input, mode) {
        var type = (mode == "from" ? input.from_type : input.to_type);
        var user = (mode == "from" ? input.from_user : input.to_user);
        var extern = input.extern_name;

        if (type == "user")
            return user.displayname;
        else if (type == "extern")
            return extern;
        else
            return "Cashbook";
    };
});

module.filter('amount', function() {
    return function(input) {
        return input.toFixed(2);
    };
});