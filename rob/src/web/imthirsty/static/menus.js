
var app = angular.module('imthirsty', ['ngResource', 'ui.bootstrap']);

app.controller('BeerMenu',
  ['$scope', 'Regions', 'Styles', 'Brewers', 'Beers', 'Recommendations',
  function($scope, Regions, Styles, Brewers, Beers, Recommendations) {
    // brewer/beer accordion shows one at a time
    $scope.oneAtATime = true;
    
    // data structure for all regions/brewers/beers
    $scope.data = {};
   
    $scope.data.current_region = null;
    $scope.data.regionDisp = "";
    
    $scope.data.regions = Regions.query();
    $scope.data.styles = Styles.query();
    
    $scope.setBrewers = function(region) {
      console.log("! " + region.region_id);
      $scope.data.current_region = region.region_id;
      $scope.data.brewers = Brewers.query({}, { region_id: region.region_id },
        function(res) {
          console.log(res);
        });
        
      $scope.data.regionDisp = region.name
    };
    
    $scope.setBeers = function(brewer_id) {
      console.log("! " + brewer_id);
      $scope.data.current_brewer = brewer_id;
      $scope.data.beers = Beers.query({}, { brewer_id: brewer_id },
        function(res) {
          console.log(res);
        });
    };
    
    $scope.recsByStyle = function(style_id) {
      console.log("! " + style_id);
      $scope.data.current_style = style_id;
      
      beer_id = $scope.data.current_beer
      if (beer_id) {
        $scope.data.recs[style_id] = Recommendations.query({}, { beer_id: beer_id, style_id: style_id },
          function(res) {
            console.log(res);
          });
      }
    };
    
    $scope.data.recs = { 1: [], 2: [], 3: [] }
    $scope.recsByBeer = function(beer_id) {
      console.log("! " + beer_id);
      $scope.data.current_beer = beer_id;
      
      style_id = $scope.data.current_style;
      if (style_id) {
        $scope.data.recs[style_id] = Recommendations.query({}, { beer_id: beer_id, style_id: style_id },
          function(res) {
            console.log(res);
          });
      }
    };

}]);

app.factory('Regions', function($resource){
  return $resource(
      'http://107.170.156.226:5000/brewer_regions',
      {}
    );
});

app.factory('Styles', function($resource){
  return $resource(
      'http://107.170.156.226:5000/styles',
      {}
    );
});

app.factory('Brewers', function($resource){
  return $resource(
      'http://107.170.156.226:5000/brewers/:region_id',
      { region_id: '@region_id' }
    );
});

app.factory('Beers', function($resource){
  return $resource(
      'http://107.170.156.226:5000/beers/:brewer_id',
      { brewer_id: '@brewer_id' }
    );
});

app.factory('Recommendations', function($resource){
  return $resource(
      'http://107.170.156.226:5000/recommend/:beer_id/:style_id',
      { beer_id: '@beer_id', style_id: '@style_id' }
    );
});