var module = angular.module("app.navigation", []);

module.controller('NavigationController', ['$scope', '$location', function ($scope, $location) {
    $scope.groups = [
        { 
            title: "General",
            items: [
                {title: "Dashboard", icon: "home", url: "/"}, 
                {title: "Account", icon: "cogs", url: "/account"}, 
                {title: "Logout", icon: "sign-out", url: "/"}
            ]
        }, 
        {
            title: "Group",
            items: [
                {title: "Members", icon: "users", url: "/members"}, 
                {title: "Shopping", icon: "shopping-cart", url: "/shopping"}, 
                {title: "Money", icon: "money", url: "/money"}, 
                {title: "Tasks", icon: "tasks", url: "/tasks"}, 
                {title: "Settings", icon: "wrench", url: "/"}
            ]
        }
    ];

    $scope.navClass = function (page) {
        var currentRoute = $location.path() || '/home';
        return page === currentRoute ? 'active' : '';
    };
}]);