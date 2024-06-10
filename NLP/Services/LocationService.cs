using System.Text;
using Blazored.LocalStorage;
using NLP.Classes;

namespace NLP.Services;

public class LocationService
{
    private readonly HttpClient _http;

    public LocationService(HttpClient http, ILocalStorageService localStorage)
    {
        _http = http;
        _http.Timeout = TimeSpan.FromMilliseconds(300);
        _http.DefaultRequestHeaders.UserAgent.ParseAdd("NLP/1.1 (eisenbergeres+2@gmail.com)");
    }

    //public async Task<LatLng?> GetCoordinates(Accident accident)
    //{
    //    if (accident.Longitude != 0 && accident.Latitude != 0)
    //        return null;
    //    
    //    StringBuilder sb = new();
    //    sb.Append("https://nominatim.openstreetmap.org/search.php?");
    //    if (accident.Street is not null)
    //        sb.Append($"&street={accident.Street}");
    //    if(accident.Subdistrict is not null)
    //        sb.Append($"&city={accident.Subdistrict}");
    //    else if (accident.District is not null)
    //        sb.Append($"&city={accident.District}");
    //    else if (accident.City is not null)
    //        sb.Append($"&city={accident.City}");
    //    if (accident.County is not null)
    //        sb.Append($"&county={accident.County}");
    //    if (accident.State is not null)
    //        sb.Append($"&state={accident.State}");
    //    if (accident.Country is not null)
    //        sb.Append($"&country={accident.Country}");
//
    //    sb.Append("&format=jsonv2&limit=1");
    //    var requestUri = sb.ToString();
    //    try
    //    {
    //        var results = await _http.GetFromJsonAsync<List<NominatimLatLng>>(requestUri);
    //        var result = results?.FirstOrDefault();
    //        if (result is null)
    //            throw new Exception();
    //        
    //        return result.ToLatLng();
    //    }
    //    catch
    //    {
    //        throw new ArgumentException(accident.Url);
    //    }
    //}
    
public async Task<LatLng?> GetCoordinates(Accident accident)
{
    if (accident.Longitude != 0 && accident.Latitude != 0)
        return null;
    
    List<Func<Accident, string>> locationBuilders = new()
    {
        a => BuildLocationUrl(a.Street, a.Subdistrict, a.District, a.City, a.County, a.State, a.Country),
        a => BuildLocationUrl(a.Street, null, a.District, a.City, a.County, a.State, a.Country),
        a => BuildLocationUrl(a.Street, null, null, a.City, a.County, a.State, a.Country),
        a => BuildLocationUrl(null, null, a.District, a.City, a.County, a.State, a.Country),
        a => BuildLocationUrl(null, null, null, a.City, a.County, a.State, a.Country),
        a => BuildLocationUrl(null, null, null, null, a.County, a.State, a.Country),
        a => BuildLocationUrl(null, null, null, null, null, a.State, a.Country),
        a => BuildLocationUrl(null, null, null, null, null, null, a.Country),
        a => BuildLocationUrl(null, null, null, null, null, a.State, null),
        a => BuildLocationUrl(null, null, null, null, a.County, null, null),
        a => BuildLocationUrl(a.Street, null, null, null, null, null, null),
    };

    foreach (var builder in locationBuilders)
    {
        var requestUri = builder(accident);
        try
        {
            var results = await _http.GetFromJsonAsync<List<NominatimLatLng>>(requestUri);
            var result = results?.FirstOrDefault();
            if (result != null)
                return result.ToLatLng();
        }
        catch
        {
            // Continue to next iteration if an exception occurs
        }

        await Task.Delay(1000);
    }

    throw new ArgumentException(accident.Url);
}

private string BuildLocationUrl(string? street, string? subdistrict, string? district, string? city, string? county, string? state, string? country)
{
    StringBuilder sb = new();
    sb.Append("https://nominatim.openstreetmap.org/search.php?");
    if (!string.IsNullOrEmpty(street))
        sb.Append($"&street={street}");
    if (!string.IsNullOrEmpty(subdistrict))
        sb.Append($"&city={subdistrict}");
    else if (!string.IsNullOrEmpty(district))
        sb.Append($"&city={district}");
    else if (!string.IsNullOrEmpty(city))
        sb.Append($"&city={city}");
    if (!string.IsNullOrEmpty(county))
        sb.Append($"&county={county}");
    if (!string.IsNullOrEmpty(state))
        sb.Append($"&state={state}");
    if (!string.IsNullOrEmpty(country))
        sb.Append($"&country={country}");
    
    sb.Append("&format=jsonv2&limit=1");
    return sb.ToString();
}
}