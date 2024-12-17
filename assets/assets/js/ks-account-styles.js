document.addEventListener('DOMContentLoaded', (event) => {

    var listItems = document.getElementsByTagName("li");
    for (var i = 0; i < listItems.length; i++) {
        listItems[i].classList.add("text-danger");
    }

});