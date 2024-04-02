let map;

function makeMap() {
    map = L.map('map');
    map.setView([23.765, 90.39], 14);
    L.tileLayer('https://tile.thunderforest.com/atlas/{z}/{x}/{y}.png?apikey=e2eea972ca8a4976919463f377a38408', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        lang: 'en'
    }).addTo(map);
    
    map.zoomControl.remove();
    
    map.setMinZoom(12);
    
    var corner1 = L.latLng(23.9179, 90.2623),
        corner2 = L.latLng(23.6326, 90.6411),
        bounds = L.latLngBounds(corner1, corner2);
    map.setMaxBounds(bounds);
}

function makePopup(latitude, longitude, headline) {
    var marker = L.marker([latitude, longitude]).addTo(map);
    marker.bindPopup(headline);
}

function zoomIn() {
    map.zoomIn(1, true);
}

function zoomOut() {
    map.zoomOut(1, true);
}

function getCenter() {
    return map.getCenter().toString();
}

function getZoom() {
    return map.getZoom();
}

function setView(latitude, longitude, zoom) {
    map.flyTo([latitude, longitude], 18, {
        pan: {
            animate: true,
            duration: 4,
            easeLinearity: 0.1
        }
    });
}

function resetPosition() {
    map.flyTo([23.765, 90.39], 14, {
        pan: {
            animate: true,
            duration: 2,
            easeLinearity: 0.1
        }
    });
}