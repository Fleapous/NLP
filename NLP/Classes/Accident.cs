namespace NLP.Classes;

public class Accident(string url)
{
    //position
    public string? Street;
    public string? Subdistrict;
    public string? District;
    public string? City;
    public string? County;
    public string? State;
    public string? Country;
    public LatLng Coordinates { get; set; } = new(0, 0);
    
    //display info
    public readonly string Url = url;
    public string? Title;
    public DateTime? PublicationDate;
    public DateTime? DateTime;
    public string? Description;
    public string? ExactLocation;
    public int? NumberOfAccidents;
    public char? Period;
    public string? DayOfTheWeek;
    public string? Surface;
    public string? Type;
    public int? Injuries;
    public int? Casualties;
    public int[]? Ages;
    public string? Cause;
    public string? PrimaryVehicle;
    public string? SecondaryVehicle;
    public string? TertiaryVehicle;
    public string[]? OtherVehicles;
    
    public Point ScreenPosition { get; set; } = new(0, 0);
    
    public double Latitude => Coordinates.Lat;
    public double Longitude => Coordinates.Lng;

    public override int GetHashCode()
    {
        return Url.GetHashCode();
    }

    public override bool Equals(object? obj)
    {
        if (obj is not Accident accident)
            return false;
        return accident.Url == Url;
    }
}