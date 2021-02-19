let button = document.getElementById("rules")
button.addEventListener("click", function (e) {
    console.log("triggered");
    window.location.href = "https://google.com";
})

let map = L.map('map').setView([46.06549996715349, 23.570670843267617], 14);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoieWV0aWJhbGF1cnUiLCJhIjoiY2tqMnl6cWZwNWJ0aDJycWo4ZG41YjNtciJ9.IkhU0PgtFeEYaslj78WO1A'
}).addTo(map);

zones = [];
towers = [];

function create_zones(data) {
    data.forEach(function (e) {
        //  remove last point
        e.shape.coordinates[0].splice(-1, 1);

        // switch lat / long
        let shape = [];
        e.shape.coordinates[0].forEach(function (longlat) {
           shape.push([longlat[1], longlat[0]])
        });

        let poly = L.polygon(shape, {color: e.color})
        zones.push(poly);
        poly.addTo(map);
    });
}

function create_towers(data) {
    data.forEach(function(e) {
        let tower = L.marker([e.location.coordinates[1], e.location.coordinates[0]]);
        towers.push(tower);
        tower.addTo(map);
    })
}

let category = document.getElementById("category")
let teamCategory = category.dataset.teamCategory;

fetch("/api/zones/?category=" + teamCategory).then(response => response.json()).then(data => create_zones(data));
fetch("/api/towers/").then(response => response.json()).then(data => create_towers(data));

