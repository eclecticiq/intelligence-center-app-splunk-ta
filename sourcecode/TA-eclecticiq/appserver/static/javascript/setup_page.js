"use strict";

require.config({
    paths: {
        SetupView: "../app/TA-eclecticiq/javascript/views/setup_view",
    },
});

require([
    // Splunk Web Framework Provided files
    "backbone", // From the SplunkJS stack
    "jquery", // From the SplunkJS stack
    "SetupView", // Custom files
],
    function(Backbone, jquery, SetupView) {
    let example_setup_view = new SetupView({
        // Sets the element that will be used for rendering
        el: jquery("#main_container"),
    });

    example_setup_view.render();
});
