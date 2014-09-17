var app = angular.module("app", [
    "ngRoute", 
    "app.navigation",
    "app.filters",
    "cselect"
]);

app.config(["$routeProvider", "$httpProvider", function($routeProvider, $httpProvider) {
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

    $httpProvider.interceptors.push('AuthInterceptor');
}]);

app.factory("AuthInterceptor", ["$window", "$q", function ($window, $q) {
    return {
        request: function(config) {
            config.headers = config.headers || {};
            if (AUTH_TOKEN) {
                config.headers.Authorization = AUTH_TOKEN;
            }
            return config || $q.when(config);
        },
        responseError: function(response) {
            console.log("RESPONSE", response.status);
            if (response.status === 401) {
                // $window.location.replace("/login");
                console.log("Redirect to Login");
            }
            return response || $q.when(response);
        }
    };
}]);

app.factory('groupData', ["$http", "$q", function ($http, $q) {
    var group = null;

    return function() {
        var d = $q.defer();

        if(group) {
            d.resolve(group);
        } else {
            $http.get('/api/group').
                success(function(data, status, headers, config) {
                    group = data;
                    d.resolve(group);
                });
        }

        return d.promise;
    };
}]);

app.controller('DashboardController', ["$scope", function($scope) {
    $scope.title = "Home";
}]);

app.controller('AccountController', ["$scope", function($scope) {
    $scope.title = "Account";
}]);

app.controller('MembersController', ["$scope", "$http", "groupData", function($scope, $http, groupData) {
    groupData().then(function(data) {
        $scope.members = data.members;
    });
}]);

app.controller('TasksController', ["$scope", "$http", "$routeParams", "$location", "$rootScope", "groupData", function($scope, $http, $routeParams, $location, $rootScope, groupData) {
    $scope.current_task = null;

    groupData().then(function(data) {
        $scope.tasks = data.tasks;
        if($routeParams.id) {
            $scope.setCurrentTask(_.find($scope.tasks, function(task) { return task.id == $routeParams.id; }));
        }
    });

    $scope.setCurrentTask = function(task) {
        $scope.current_task = task;
        $rootScope.title = task.title;
        $location.path("/tasks/" + task.id);
    }

}]);

app.controller('MoneyController', ["$scope", "$http", "groupData", function($scope, $http, groupData) {
    $scope.transactions = [];

    groupData().then(function(data) {
        $scope.transactions = data.transactions;
    });
}]);

app.controller('ShoppingController', ["$scope", "$timeout", "$http", "groupData", function($scope, $timeout, $http, groupData) {
    $scope.items = [];
    $scope.categories = [];

    $scope.togglePurchased = function(item) {
        item.updating = true;

        return $timeout(function(){
            item.updating = false;
        }, 300);
    };


    groupData().then(function(data) {
        $scope.items = data.shopping_items;
        $scope.categories = data.shopping_categories;
    });
}]);