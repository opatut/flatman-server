var cselect = angular.module('cselect', []);

cselect.controller('cselectCtrl', ['$scope', function($scope) {
    this.scope = $scope;

    this.select = function(value) {
        $scope.$apply(function() {
            $scope.selected = value;

        });
    }; 
}]);

cselect.directive('cselect', function() {
    return {
        restrict: 'AE',
        transclude: true,
        replace: false,
        require: 'ngModel',
        // template: '<ng-transclude></ng-transclude>',
        controller: 'cselectCtrl',
        link: function(scope, element, attrs, ngModel, transclude) {
            transclude(scope, function(clone) {
               element.append(clone);
            });

            scope.$watch('selected', function(newValue) {
                if (ngModel.$viewValue !== newValue) {
                    ngModel.$setViewValue(newValue);
                }
            });

            ngModel.$render = function() {
                 scope.selected = ngModel.$viewValue;
            };

        },
    };
});

cselect.directive('cselectOption', function() {
    return {
        restrict: 'A',
        require: '^cselect',
        scope: {
            'cselectOption': '&'
        },
        link: function(scope, element, attrs, cselectCtrl) {
            var value = scope.cselectOption();

            element.on('click', function() {
                cselectCtrl.select(value);
            });

            cselectCtrl.scope.$watch('selected', function($value) {
                if($value === value) {
                    element.addClass('active');
                } else {
                    element.removeClass('active');
                }
            });
        }
    };
})

