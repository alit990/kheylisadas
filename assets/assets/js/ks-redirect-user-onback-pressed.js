(function () {
    window.onpageshow = function (event) {
        if (event.persisted) {
            window.location.replace("/user");
            $("#divLoginForm").load(location.href + " #divLoginForm");
        }
    };
})();