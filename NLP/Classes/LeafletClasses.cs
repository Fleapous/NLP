namespace NLP.Classes;

public class LeafletEventArgs
{
    public string Type { get; set; }
    public Object Target { get; set; }
    public Object Source { get; set; }
    public Object PropagatedFrom { get; set; }
}
public class LeafletResizeEventArgsArgs(Point oldSize, Point newSize) : LeafletEventArgs
{
    public Point OldSize { get; set; } = oldSize;
    public Point NewSize { get; set; } = newSize;
}

public class LeafletMouseEventArgsArgs(LatLng latLng, Point containerPoint) : LeafletEventArgs
{
    public LatLng LatLng { get; set; } = latLng;
    public Point ContainerPoint { get; set; } = containerPoint;
}

public class LatLng(double lat, double lng)
{
    public double Lat { get; set; } = lat;
    public double Lng { get; set; } = lng;
    
    public override string ToString()
    {
        return $"[{Lat}, {Lng}]";
    }
}

public class NominatimLatLng(double lat, double lon)
{
    public double Lat { get; set; } = lat;
    public double Lon { get; set; } = lon;

    public LatLng ToLatLng()
    {
        return new LatLng(Lat, Lon);
    }
}

public class Point(double x, double y)
{
    public double X { get; set; } = x;
    public double Y { get; set; } = y;

    public override string ToString()
    {
        return $"[{X}, {Y}]";
    }
}

public class Bounds(LatLng[] corners)
{
    public LatLng NorthWest { get; set; } = corners[0];
    public LatLng SouthEast { get; set; } = corners[1];

    public bool Contains(LatLng coordinates)
    {
        return coordinates.Lat <= NorthWest.Lat &&
               coordinates.Lat >= SouthEast.Lat &&
               coordinates.Lng >= NorthWest.Lng &&
               coordinates.Lng <= SouthEast.Lng;
    }
    
    public (double dx, double dy) GetSize()
    {
        var dx = SouthEast.Lng - NorthWest.Lng;
        var dy = NorthWest.Lat - SouthEast.Lat;
        return (dx, dy);
    }

    public (double lat, double lng) Project(LatLng coordinates)
    {
        var lat = NorthWest.Lat - coordinates.Lat;
        var lng = coordinates.Lng - NorthWest.Lng;
        return (lat, lng);
    }
    
    public override string ToString()
    {
        return $"[{NorthWest}, {SouthEast}]";
    }
}