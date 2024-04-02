namespace NLP.Classes;

public class Accident(double latitude, double longitude, string headline)
{
    public double Longitude { get; set; } = longitude;
    public double Latitude { get; set; } = latitude;
    public string Headline { get; set; } = headline;
}