/* If browser back button was used, flush cache */
(function () {
    window.onpageshow = function (event) {
        if (event.persisted) {
            $("#divRegisterComponent").load(location.href + " #divRegisterComponent");
            $("#ulUserStatus").load(location.href + " #ulUserStatus");

        }
    };
})();