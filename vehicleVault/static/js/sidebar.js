document.addEventListener("DOMContentLoaded", function () {

    const toggleBtn = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");

    // Open sidebar
    toggleBtn.addEventListener("click", function () {

        sidebar.classList.toggle("active");
        overlay.classList.toggle("active");

    });

    // Close sidebar when clicking overlay
    overlay.addEventListener("click", function () {

        sidebar.classList.remove("active");
        overlay.classList.remove("active");

    });

});

// document.addEventListener("DOMContentLoaded", function () {

//     const toggleBtn = document.getElementById("menu-toggle");
//     const sidebar = document.getElementById("sidebar");

//     if(toggleBtn && sidebar){

//         toggleBtn.addEventListener("click", function () {

//             sidebar.classList.toggle("active");

//         });

//     }

// });