let map = L.map('map').setView([46.06549996715349, 23.570670843267617], 14);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoieWV0aWJhbGF1cnUiLCJhIjoiY2tqMnl6cWZwNWJ0aDJycWo4ZG41YjNtciJ9.IkhU0PgtFeEYaslj78WO1A'
}).addTo(map);

function create_zones(data) {
    data.forEach(function (e) {
        if (e.shape) {
            //  remove last point
            e.shape.coordinates[0].splice(-1, 1);

            // switch lat / long
            let shape = [];
            e.shape.coordinates[0].forEach(function (longlat) {
               shape.push([longlat[1], longlat[0]])
            });

            L.polygon(shape, {color: e.color}).addTo(map);
        }
    });
}

let towers = {}
function create_towers(data) {
    data.forEach(function(e) {
        towers[e.id] = e
        L.marker([e.location.coordinates[1], e.location.coordinates[0]]).addTo(map);
    })
}
fetch("/api/towers/").then(response => response.json()).then(data => create_towers(data));

function onLocationFound(e) {
    var radius = e.accuracy;

    L.marker(e.latlng).addTo(map)
        .bindPopup("You are within " + radius + " meters from this point").openPopup();

    L.circle(e.latlng, radius).addTo(map);

    //  make a call to get towers by their closest location to you
    fetch("/api/towers/?lat=" + e.latlng[0] + "&lng=" + e.latlng[1])
}

map.on('locationfound', onLocationFound);

function onLocationError(e) {
    alert(e.message);
}

map.on('locationerror', onLocationError);
map.locate({setView: true, maxZoom: 16});