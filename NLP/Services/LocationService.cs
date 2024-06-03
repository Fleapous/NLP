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

    public async Task<LatLng?> GetCoordinates(Accident accident)
    {
        if (accident.Longitude != 0 && accident.Latitude != 0)
            return null;
        
        StringBuilder sb = new();
        sb.Append("https://nominatim.openstreetmap.org/search.php?");
        if (accident.Street is not null)
            sb.Append($"&street={accident.Street}");
        if(accident.Subdistrict is not null)
            sb.Append($"&city={accident.Subdistrict}");
        else if (accident.District is not null)
            sb.Append($"&city={accident.District}");
        else if (accident.City is not null)
            sb.Append($"&city={accident.City}");
        //if (accident.County is not null)
        //    sb.Append($"&county={accident.County}");
        //if (accident.State is not null)
        //    sb.Append($"&state={accident.State}");
        if (accident.Country is not null)
            sb.Append($"&country={accident.Country}");

        sb.Append("&format=jsonv2&limit=1");
        var requestUri = sb.ToString();
        try
        {
            var results = await _http.GetFromJsonAsync<List<NominatimLatLng>>(requestUri);
            var result = results?.FirstOrDefault();
            if (result is null)
                throw new Exception();
            
            return result.ToLatLng();
        }
        catch
        {
            throw new ArgumentException(accident.Url);
        }
    }
}