var app = angular.module("app", [
    "ngRoute", 
    "ngAnimate",
    "ngResource",
    "app.filters",
    "cselect",
    "ui.bootstrap"
]);

app.controller('NavigationController', ['$scope', '$location', '$http', 'User', function ($scope, $location, $http, User) {
    $scope.navigation = {
        main: { 
            title: "General",
            items: [
                {title: "Account", icon: "cogs", url: "#/account"}, 
                {title: "Logout", icon: "sign-out", url: "/logout"}
            ]
        }, 
        group: {
            title: "Group",
            items: [
                {title: "Dashboard", icon: "home", url: "#/"}, 
                {title: "Members", icon: "users", url: "#/members"}, 
                {title: "Shopping", icon: "shopping-cart", url: "#/shopping"}, 
                {title: "Money", icon: "money", url: "#/money"}, 
                {title: "Tasks", icon: "tasks", url: "#/tasks"}, 
                {title: "Settings", icon: "wrench", url: "#/settings"}
            ]
        }
    };

    $scope.navClass = function (url) {
        var currentRoute = $location.path() || '/home';
        if(url=="#/") return url == "#"+currentRoute ? 'active' : '';
        return _.string.startsWith(currentRoute, url.substring(1)) ? 'active' : '';
    };

    User.self(function(data) {
        $scope.user = data[0];
    });

    $http.get('/api/group')
        .success(function(data, status, headers, config) {
            $scope.group = data;
        });
}]);

app.controller('ShoppingItemController', ["$scope", "$modal", function($scope, $modal) {
    $scope.open = function (size) {
        var modalInstance = $modal.open({
            templateUrl: '/templates/add-shopping-item.html',
            controller: 'ModalInstanceCtrl',
            size: size,
            resolve: {
                items: function () {
                    return $scope.items;
                }
            }
        });

        modalInstance.result.then(function (selectedItem) {
            $scope.selected = selectedItem;
        }, function () {
            // $log.info('Modal dismissed at: ' + new Date());
        });
    };
}]);

app.controller('ModalInstanceCtrl', ["$scope", "$modalInstance", function($scope, $modalInstance) {
    $scope.ok = function () {
        $modalInstance.close($scope.selected.item);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}]);

app.config(["$routeProvider", "$httpProvider", function($routeProvider, $httpProvider) {
    $routeProvider
        .when('/', {
            templateUrl : '/templates/dashboard.html',
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

app.factory('User', ['$resource', function($resource) {
    return $resource('/api/user/:id?', {}, {
        self: { method:'GET', params:{id:'self'}, isArray:true, cache: true}
    });
}]);

app.factory('Group', ['$resource', '$q', 'User', function($resource, $q, User) {
    return $resource('/api/group/:id', {}, {
        own: { method:'GET', params:{id: 'own'}, isArray:true, cache: true}
    });
}]);

app.factory('Task', ['$resource', '$q', function($resource, $q) {
    return $resource('/api/task/:id', {}, {
        own_group: { method:'GET', params:{id: ''}, isArray: true, cache: true},
        own: { method:'GET', params:{id: 'own'}, isArray: true, cache: true}
    });
}]);

app.factory('ShoppingItem', ['$resource', '$q', function($resource, $q) {
    return $resource('/api/shopping_item/:itemId', {
        itemId:'@id'
    }, {
        query: { method:'GET', params:{itemId: 'default'}, isArray: true, cache: true},
        add: { method:'PUT' }
    });
}]);

app.factory('ShoppingCategory', ['$resource', '$q', function($resource, $q) {
    return $resource('/api/shopping_category/:id', {}, {
        query: { method:'GET', params:{id: ''}, isArray: true, cache: true}
    });
}]);

app.factory('Transaction', ['$resource', '$q', function($resource, $q) {
    return $resource('/api/transaction/:id', {}, {
        query: { method:'GET', params:{id: ''}, isArray: true, cache: true}
    });
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
                $window.location.replace("/login");
            }
            return response || $q.when(response);
        }
    };
}]);

app.controller('DashboardController', ["$scope", function($scope) {
}]);

app.controller('AccountController', ["$scope", function($scope) {
    $scope.title = "Account";
}]);

app.controller('MembersController', ["$scope", "$http", "Group", function($scope, $http, Group) {
    Group.own().$promise.then(function(resource) {
        resource.get(function(group) {
            $scope.members = group.members;
        });
    });
}]);

app.controller('TasksController', ["$scope", "$http", "$routeParams", "$location", "$rootScope", "Task", function($scope, $http, $routeParams, $location, $rootScope, Task) {
    $scope.task = null;

    Task.own_group().$promise.then(function(tasks) {
        console.log("GOt tasks", tasks);
        $scope.tasks = tasks;
    });
        // if($routeParams.id) {
        //     $scope.setCurrentTask(_.find($scope.tasks, function(task) { return task.id == $routeParams.id; }));
        // }

    // $scope.setCurrentTask = function(task) {
    //     $scope.task = task;
    //     $rootScope.title = task.title;
    //     $location.path("/tasks/" + task.id);
    // }

}]);

app.controller('MoneyController', ["$scope", "$http", function($scope, $http) {
    $scope.transactions = [];
}]);

app.controller('ShoppingController', ["$scope", "$timeout", "$http", 'ShoppingItem', 'ShoppingCategory', function($scope, $timeout, $http, ShoppingItem, ShoppingCategory) {
    $scope.items = [];
    $scope.categories = [];

    $scope.current_category = 'all';
    $scope.editing = new ShoppingItem;

    $scope.togglePurchased = function(item) {
        item.updating = true;

        return $timeout(function(){
            item.updating = false;
        }, 100);
    };

    $scope.setCategory = function(category) {
        $scope.current_category = category;
    };

    $scope.setEditing = function(item) {
        if($scope.editing == item) return;
        $scope.editing = item;
        if(item) {
            $(".item-title").focus();
        }
    };

    $scope.updating = 0;
    $scope.saveItem = function(item, explicit) {
        if(!item) return;

        if(!item.id) { // create
            if(!explicit) return;
            $scope.updating += 1;
            ShoppingItem.add(item).$promise.then(function(item) {
                $scope.items.push(item);
            })['finally'](function() {
                return $timeout(function() {
                    $scope.updating -= 1;
                }, 100);
            });
            $scope.editing = new ShoppingItem;
        } else { // update
            $scope.updating += 1;
            if(explicit) {
                $scope.editing = new ShoppingItem;
            }
            ShoppingItem.save(item).$promise.then(function(item) {
            })['finally'](function() {
                return $timeout(function() {
                    $scope.updating -= 1;
                }, 100);
            });
        }
    };

    // Change currently selected category when we move an item to another one
    $scope.itemChangeCategory = function(category) {
        if($scope.current_category != "all") {
            $scope.current_category = _.find($scope.categories, function(c) { return c.id == $scope.editing.category_id; });
        }
    };

    // Returns all the items in the category
    $scope.getItems = function(category) {
        if(category == 'all') return $scope.items;
        var id = (category ? category.id : 0);
        return _.filter($scope.items, function(i) { return i.category_id == id; });
    };

    ShoppingItem.query().$promise.then(function(items) {
        $scope.items = items;
    });

    ShoppingCategory.query().$promise.then(function(categories) {
        $scope.categories = categories;
    });

}]);


function ng(name) {
    return angular.element(document.body).injector().get(name);
}