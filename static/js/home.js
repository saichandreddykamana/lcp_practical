let dashboard_dropdown = document.getElementsByClassName('dashboard-dropdown-icon')[0].onclick = function(){
        $("div.dashboard").toggleClass( "hide");
        $("span.dashboard-dropdown-icon").toggleClass("plus").toggleClass("minus");
}

let table_dropdown = document.getElementsByClassName('table-dropdown-icon')[0].onclick = function(){
        $("div.table").toggleClass( "hide");
        $("span.table-dropdown-icon").toggleClass("plus").toggleClass("minus");
}

let hideOtherOptions = function(){
    let dropdown = document.getElementsByClassName('dropdown-content');
    for(let i = 0 ; i < dropdown.length; i++){
        if(dropdown[i].classList.contains('show-menu')){
            dropdown[i].classList.remove('show-menu');
        }
    }
}

let showOptions = function(menu_index){
    $("div.dropdown-content:eq(" + menu_index + ")").toggleClass("show-menu");
}

$('.data-menu').click(function(){
    hideOtherOptions();
    showOptions($(this).index('.data-menu'));
});
