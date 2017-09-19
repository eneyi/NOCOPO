  !function($) {
    "use strict";

    var GoogleMap = function() {};

 //creates map with street view
    GoogleMap.prototype.createWithStreetview = function ($container, $lat, $lng) {
      return GMaps.createPanorama({
        el: $container,
        lat : $lat,
        lng : $lng
      });
    },
//init
    GoogleMap.prototype.init = function() {
      var $this = this;
      $(document).ready(function(){



        //street view
        $this.createWithStreetview('#panorama',42.3455, -71.0983);


      });
    },
    //init
    $.GoogleMap = new GoogleMap, $.GoogleMap.Constructor = GoogleMap
}(window.jQuery),

//initializing
function($) {
    "use strict";
    $.GoogleMap.init()
}(window.jQuery);