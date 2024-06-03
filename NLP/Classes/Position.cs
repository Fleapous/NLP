namespace NLP.Classes;

public class Position(double latitude, double longitude, int? zoom = null)
{
    public double Latitude { get; set; } = latitude;
    public double Longitude { get; set; } = longitude;
    public int? Zoom { get; set; } = zoom;
}