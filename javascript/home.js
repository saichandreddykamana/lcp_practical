let dashboard_dropdown = document.getElementsByClassName('dashboard-dropdown-icon')[0].onclick = function(){
        $( "div.dashboard" ).toggleClass( "show");
        $("span.dashboard-dropdown-icon").toggleClass("minus").toggleClass("plus");  
    }

dashboard_dropdown();
