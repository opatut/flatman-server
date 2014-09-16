var app = angular.module("app", [
    "ngRoute", 
    "app.navigation",
    "app.filters",
    "cselect"
]);

app.config(function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl : '/templates/test.html',
            controller : 'DashboardController'
        })
        .when('/members', {
            templateUrl : '/templates/members.html',
            controller : 'MembersController'
        })
        .when('/money', {
            templateUrl : '/templates/money.html',
            controller : 'MoneyController'
        })
        .when('/shopping', {
            templateUrl : '/templates/shopping.html',
            controller : 'ShoppingController'
        })
        .when('/account', {
            templateUrl : '/templates/test.html',
            controller : 'AccountController'
        })
        .when('/tasks/:id?', {
            templateUrl : '/templates/tasks.html',
            controller : 'TasksController'
        });
});

app.controller('DashboardController', function($scope) {
    $scope.title = "Home";
});

app.controller('AccountController', function($scope) {
    $scope.title = "Account";
});

app.controller('MembersController', function($scope, $http) {
    $scope.members = [];

    $http.post('/api/group').
        success(function(data, status, headers, config) {
            $scope.members = data.members;
        });
});

app.controller('TasksController', function($scope, $http, $routeParams) {
    $scope.tasks = [];
    $scope.current_task = null;

    $http.post('/api/group').
        success(function(data, status, headers, config) {
            $scope.tasks = data.tasks;


            console.log($routeParams);
        });
});

app.controller('MoneyController', function($scope, $http) {
    $scope.transactions = [];

    $http.post('/api/group').
        success(function(data, status, headers, config) {
            $scope.transactions = data.transactions;
        });
});

app.controller('ShoppingController', function($scope, $timeout, $http) {
    $scope.items = [];
    $scope.categories = [];

    $scope.togglePurchased = function(item) {
        item.updating = true;

        return $timeout(function(){
            item.updating = false;
        }, 300);
    };


    $http.post('/api/group').
        success(function(data, status, headers, config) {
            $scope.items = data.shopping_items;
            $scope.categories = data.shopping_categories;
        });
});