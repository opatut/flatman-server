var module = angular.module("app.navigation", []);

module.controller('NavigationController', ['$scope', '$location', '$http', function ($scope, $location, $http) {
    $scope.groups = [
        { 
            title: "General",
            items: [
                {title: "Dashboard", icon: "home", url: "#/"}, 
                {title: "Account", icon: "cogs", url: "#/account"}, 
                {title: "Logout", icon: "sign-out", url: "/logout"}
            ]
        }, 
        {
            title: "Group",
            items: [
                {title: "Members", icon: "users", url: "#/members"}, 
                {title: "Shopping", icon: "shopping-cart", url: "#/shopping"}, 
                {title: "Money", icon: "money", url: "#/money"}, 
                {title: "Tasks", icon: "tasks", url: "#/tasks"}, 
                {title: "Settings", icon: "wrench", url: "#/settings"}
            ]
        }
    ];

    $scope.navClass = function (url) {
        var currentRoute = $location.path() || '/home';
        return url.substring(1) === currentRoute ? 'active' : '';
    };

    $http.get('/api/user')
        .success(function(data, status, headers, config) {
            $scope.user = data;
        });

    $http.get('/api/group')
        .success(function(data, status, headers, config) {
            $scope.group = data;
        });
}]);