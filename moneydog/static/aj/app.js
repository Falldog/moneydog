'use strict'

angular.module('moneydogApp', ['datePicker'])
  .config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  });


