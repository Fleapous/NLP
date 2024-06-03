let map;

function makeMap(
    base_latitude = 23.765, 
    base_longitude = 90.39, 
    base_zoom = 14, 
    min_zoom = 12,
    max_zoom = 19,
    use_bounds = true,
    bounds_corner_1_latitude = 23.9179, 
    bounds_corner_1_longitude = 90.2623, 
    bounds_corner_2_latitude = 23.6326, 
    bounds_corner_2_longitude = 90.6411) {

    map = L.map('map')
    map.setView([base_latitude, base_longitude], base_zoom);
    
    L.tileLayer('https://tile.thunderforest.com/atlas/{z}/{x}/{y}.png?apikey=e2eea972ca8a4976919463f377a38408', {
        maxZoom: max_zoom,
        minZoom: min_zoom,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        lang: 'en'
    }).addTo(map);
    
    map.zoomControl.remove();
    
    if(use_bounds)
    {
        var corner1 = L.latLng(bounds_corner_1_latitude, bounds_corner_1_longitude),
            corner2 = L.latLng(bounds_corner_2_latitude, bounds_corner_2_longitude),
            bounds = L.latLngBounds(corner1, corner2);
        map.setMaxBounds(bounds);
    }
}

function makePopup(latlang, headline) {
    var marker = L.marker(latlang).addTo(map);
    marker.bindPopup(headline);
}

function zoomIn() {
    map.zoomIn(1, true);
}

function zoomOut() {
    map.zoomOut(1, true);
}

function getCenter() {
    return map.getCenter();
}

function getZoom() {
    return map.getZoom();
}

function setView(latitude, longitude, zoom) {
    map.flyTo([latitude, longitude], zoom, {
        pan: {
            animate: true,
            duration: 4,
            easeLinearity: 0.1
        }
    });
}

function size() {
    return map.getSize();
}

function bounds() {
    let bounds = map.getBounds();
    let northWest = bounds.getNorthWest();
    let southEast = bounds.getSouthEast();
    return [northWest, southEast];
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

function latLngToPoint(latLng) {
    return map.latLngToContainerPoint(latLng);
}

function subscribeToMapEvent(dotNetObject) {
    map.on('move', function() {
        dotNetObject.invokeMethodAsync('OnMapMove');
    });
    map.on('zoomstart', function() {
        dotNetObject.invokeMethodAsync('OnMapMove');
    });
    map.on('zoom', function() {
        dotNetObject.invokeMethodAsync('OnMapMove');
    });
    map.on('moveend', function() {
        dotNetObject.invokeMethodAsync('OnMapMoveEnd');
    });
    map.on('zoomend', function() {
        dotNetObject.invokeMethodAsync('OnMapMoveEnd');
    });
    map.on('resize', function(event) {
        dotNetObject.invokeMethodAsync('OnMapResize', event.newSize);
    });
    return "success";
}

function subscribe(dotNetObject) {
    map.on('zoomstart', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "ZoomStarted", null);
    });
    map.on('zoom', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "Zoomed", null);
    });
    map.on('zoomend', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "ZoomEnded", null);
    });
    map.on('resize', function(args) {
        dotNetObject.invokeMethodAsync('InvokeAsync', "Resized", args.newSize);
    });
    map.on('viewreset', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "ViewReset", null);
    });
    map.on('load', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "Loaded", null);
    });
    map.on('movestart', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "MoveStarted", null);
    });
    map.on('move', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "Moved", null);
    });
    map.on('moveend', function() {
        dotNetObject.invokeMethodAsync('InvokeAsync', "MoveEnded", null);
    });
    //map.on('click', function(args) {
    //    dotNetObject.invokeMethodAsync('InvokeAsync', "Clicked", args);
    //});
    //map.on('dblclick', function(args) {
    //    dotNetObject.invokeMethodAsync('InvokeAsync', "DoubleClicked", args);
    //});
    //map.on('mousedown', function(args) {
    //    dotNetObject.invokeMethodAsync('InvokeAsync', "MouseDown", args);
    //});
    //map.on('mouseup', function(args) {
    //    dotNetObject.invokeMethodAsync('InvokeAsync', "MouseUp", args);
    //});
    //map.on('mouseover', function(args) {
    //    dotNetObject.invokeMethodAsync('InvokeAsync', "MouseOver", args);
    //});
    //map.on('mouseout', function(args) {
    //    dotNetObject.invokeMethodAsync('InvokeAsync', "MouseOut", args);
    //});
}
function isMapInitialized() {
    return map != null;
}