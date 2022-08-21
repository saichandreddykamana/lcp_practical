let dashboard_dropdown = document.getElementsByClassName('dashboard-dropdown-icon')[0].onclick = function(){
        $("div.dashboard").toggleClass( "hide");
        $("span.dashboard-dropdown-icon").toggleClass("plus").toggleClass("minus");
}

let table_dropdown = document.getElementsByClassName('table-dropdown-icon')[0].onclick = function(){
        $("div.table").toggleClass( "hide");
        $("span.table-dropdown-icon").toggleClass("plus").toggleClass("minus");
}

let search_dropdown = document.getElementsByClassName('search-dropdown-icon')[0].onclick = function(){
        $("div.search").toggleClass( "hide");
        $("span.search-dropdown-icon").toggleClass("plus").toggleClass("minus");
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

function loadChart(array, seasons){
    var chartData = [];
    array = JSON.parse(array);
    chartData.push(['Pupils', 'School Name']);

    for(let i = 0 ; i < array.length; i++){
        let arr = [];
        arr.push(array[i]['School name']);
        arr.push(array[i].Pupils);
        chartData.push(arr);
    }

    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(function(){
        var data = google.visualization.arrayToDataTable(chartData);
        var options = {title: 'Number of pupils in each schools'};
        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
            chart.draw(data, options);
    });
}

function loadBar(array){
    var chartData = [];
    array = JSON.parse(array);
    chartData.push(["Season", "Pupils"]);

    for(let i = 0 ; i < array.length; i++){
        let arr = [];
        arr.push(array[i]['Season']);
        arr.push(array[i].Pupils);
        chartData.push(arr);
    }
    google.charts.load("current", {packages:['bar']});
    google.charts.setOnLoadCallback(function() {
          var data = google.visualization.arrayToDataTable(chartData);
          var options = {
          width: 350,
          legend: { position: 'none' },
          chart: {
            title: 'Number of pupils born in each season',
            subtitle: 'pupils by number' },
          axes: {
            x: {
              0: { side: 'top', label: 'White to move'} // Top x-axis.
            }
          },
          bar: { groupWidth: "60%" }
        };
          var chart = new google.charts.Bar(document.getElementById("columnchart_values"));
          chart.draw(data, google.charts.Bar.convertOptions(options));
    });
}