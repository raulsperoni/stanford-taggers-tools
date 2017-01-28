'use strict';

angular.module('krypton.version', [
      'krypton.version.interpolate-filter',
      'krypton.version.version-directive'
])

.value('version', '0.1');
