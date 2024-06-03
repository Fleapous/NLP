using System.Globalization;
using Microsoft.JSInterop;
using NLP.Classes;

namespace NLP.Services;

public class MapService(IJSRuntime Js)
{
    public async Task<int> GetZoom()
    {
        return await Js.InvokeAsync<int>("getZoom");
    }

    public async Task ZoomIn()
    {
        await Js.InvokeVoidAsync("zoomIn");
    }

    public async Task ZoomOut()
    {
        await Js.InvokeVoidAsync("zoomOut");
    }

    public async Task AddTestPopup(LatLng coordinates)
    {
        await Js.InvokeVoidAsync("makePopup", coordinates, "test");
    }
    
    public async Task SetView(Position position)
    {
        await Js.InvokeVoidAsync("setView", position.Latitude, position.Longitude, position.Zoom);
    }
    public async Task SetView(double latitude, double longitude, int zoom)
    {
        await Js.InvokeVoidAsync("setView", latitude, longitude, zoom);
    }

    public async Task<Bounds> GetBounds()
    {
        var corners = await Js.InvokeAsync<LatLng[]>("bounds");
        return new Bounds(corners);
    }

    public async Task<(double x, double y)> GetPixelSize()
    {
        var size =  await Js.InvokeAsync<Point>("size");
        return (size.X, size.Y);
    }
    
    public async Task<Point> Project(LatLng coordinates)
    {
        var point = await Js.InvokeAsync<Point>("latLngToPoint", coordinates);
        point.X = Math.Round(point.X, 2);
        point.Y = Math.Round(point.Y, 2);
        return point;
    }
    
    public async Task<(double, double, int?)> GetCurrentPosition()
    {
        var position = await Js.InvokeAsync<LatLng>("getCenter");
        
        int? zoom = null;
        try
        {
            zoom = await GetZoom();
        }
        catch
        {
            //pass
        }
        
        return (position.Lat, position.Lng, zoom);
    }
    
    public async Task ResetPosition()
    {
        await Js.InvokeVoidAsync("resetPosition");
    }
}