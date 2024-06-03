using System.Drawing;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using NLP.Classes;
using Point = NLP.Classes.Point;

namespace NLP.Components;

public partial class Map : ComponentBase
{
    [Parameter] public EventCallback ZoomStarted { get; set; }
    [Parameter] public EventCallback Zoomed { get; set; }
    [Parameter] public EventCallback ZoomEnded { get; set; }
    [Parameter] public EventCallback<Point> Resized { get; set; }
    [Parameter] public EventCallback ViewReset { get; set; }
    [Parameter] public EventCallback Loaded { get; set; }
    [Parameter] public EventCallback MoveStarted { get; set; }
    [Parameter] public EventCallback Moved { get; set; }
    [Parameter] public EventCallback MoveEnded { get; set; }
    [Parameter] public EventCallback<LeafletMouseEventArgsArgs> Clicked { get; set; }
    [Parameter] public EventCallback<LeafletMouseEventArgsArgs> DoubleClicked { get; set; }
    [Parameter] public EventCallback<LeafletMouseEventArgsArgs> MouseDown { get; set; }
    [Parameter] public EventCallback<LeafletMouseEventArgsArgs> MouseUp { get; set; }
    [Parameter] public EventCallback<LeafletMouseEventArgsArgs> MouseEntered { get; set; }
    [Parameter] public EventCallback<LeafletMouseEventArgsArgs> MouseLeft { get; set; }
    [Parameter] public Position InitialPosition { get; set; } = new(23.765, 90.39, 14);
    [Parameter] public int MinZoom { get; set; } = 0;
    [Parameter] public int MaxZoom { get; set; } = 20;
    [Parameter] public Position[]? Bounds { get; set; }

    private JsonSerializerOptions JsonOptions = new JsonSerializerOptions {PropertyNameCaseInsensitive = true};
    
    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (!firstRender)
            return;

        await Initialize();
        var reference = DotNetObjectReference.Create(this);
        await Js.InvokeVoidAsync("subscribe", reference);
    }

    private async Task Initialize()
    {
        var useBounds = Bounds?.Length == 2;
        Position? corner1 = null, corner2 = null;
        if (useBounds)
        {
            corner1 = Bounds!.First();
            corner2 = Bounds!.Last();
        }
        
        await Js.InvokeVoidAsync("makeMap", 
            InitialPosition.Latitude, 
            InitialPosition.Longitude, 
            InitialPosition.Zoom ?? 14, 
            MinZoom,
            MaxZoom, 
            useBounds,
            corner1?.Latitude, 
            corner1?.Longitude, 
            corner2?.Latitude,
            corner2?.Longitude
        );

        await Loaded.InvokeAsync();
    }
    
    [JSInvokable]
    public async Task InvokeAsync(string callbackName, object args)
    {
        var property = GetType().GetProperty(callbackName, BindingFlags.Public | BindingFlags.Instance);
        if (property is null)
            throw new ArgumentException($"No callback found with the name {callbackName}", nameof(callbackName));

        var callback = property.GetValue(this);

        switch (callback)
        {
            case EventCallback eventCallback:
                await eventCallback.InvokeAsync(null);
                break;
            case EventCallback<Point> pointEventCallback:
                try
                {
                    var point = JsonSerializer.Deserialize<Point>(args.ToString()!, JsonOptions);
                    await pointEventCallback.InvokeAsync(point);
                }
                catch
                {
                    Console.WriteLine($"Deserialization failed: {args}", Color.Red);
                }
                break;
        }
    }
    
}