using System.Diagnostics;
using System.Globalization;
using MudBlazor;
using MudBlazor.Charts;
using Newtonsoft.Json;
using NLP.Classes;
using NLP.Components.Dialogs;
using Position = NLP.Classes.Position;

namespace NLP.Components.Pages;

public partial class Home
{
    private List<Accident> Accidents { get; set; } = [];
    private List<Accident> FilteredAccidents { get; set; } = [];
    private List<Accident> DisplayAccidents { get; set; } = [];
    private List<AccidentGroup> DisplayGroups { get; set; } = [];
    private Queue<Accident> NewAccidents { get; set; } = [];
    private int AccidentCount { get; set; }
    private HashSet<string> TriedUrls { get; set; } = [];
    private Position OriginalPosition { get; set; } = new(23.765, 90.39, 14);
    private Position BoundCorner1 { get; } = new(23.90, 90.25);
    private Position BoundCorner2 { get; } = new(23.63, 90.64);
    private const int MinZoom = 9;
    private const int MaxZoom = 19;
    private Bounds CurrentBounds { get; set; } = default!;
    private int LoadingOffset = 0;
    private Task<List<Accident>> AccidentsLoading { get; set; }
    private const string JsonPath = "./loaded_accidents.json";
    private const string FilePath = "./accidents.csv";
    private Dictionary<string, Filter> Filters { get; set; } = [];
    private HashSet<string> Days { get; set; } = [];
    private HashSet<string> Surfaces { get; set; } = [];
    private HashSet<string> Types { get; set; } = [];
    private HashSet<string> Causes { get; set; } = [];
    private (double X, double Y) MapSize { get; set; }
    
    private bool Zooming { get; set; }
    public bool InjuriesOnly { get; set; }
    public bool CasualtiesOnly { get; set; }
    public bool ManualOnly { get; set; }
    public string ManualUrl { get; set; }

    protected override void OnInitialized()
    {
        AccidentsLoading = LoadAccidents();
        var awaiter = AccidentsLoading.GetAwaiter();
        awaiter.OnCompleted(() =>
        {
            FilteredAccidents = Accidents = AccidentsLoading.Result;
            foreach (var day in Accidents
                         .Where(a => a.DayOfTheWeek is not null)
                         .Select(a => a.DayOfTheWeek!))
                Days.Add(day);
            
            foreach (var surface in Accidents
                         .Where(a => a.Surface is not null)
                         .Select(a => a.Surface!))
                Surfaces.Add(surface);
            
            foreach (var type in Accidents
                         .Where(a => a.Type is not null)
                         .Select(a => a.Type!))
                Types.Add(type);
            
            foreach (var cause in Accidents
                         .Where(a => a.Cause is not null)
                         .Select(a => a.Cause!))
                Causes.Add(cause);

            SelectedDateRange = new DateRange(Accidents.Min(a => a.DateTime), Accidents.Max(a => a.DateTime));
        });
    }

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            TriedUrls = await LocalStorage.GetItemAsync<HashSet<string>>("tried_urls") ?? [];
        }
    }

    private DateTime? ParseDateTime(string text)
    {
        text = string.Join("", text.ToCharArray().Where(char.IsNumber));
        if (text.Length is not (8 or 12))
            return null;
        
        DateTime dateTime = new();
        
        if (text.Length >= 8)
        {
            var year = int.Parse(text[..4]);
            var month = int.Parse(text[4..6]);
            var day = int.Parse(text[6..8]);
            dateTime = new DateTime(year, month, day);
        }

        if (text.Length == 12)
        {
            var hours = int.Parse(text[8..10]);
            var minutes = int.Parse(text[10..12]);
            dateTime = dateTime.AddHours(hours).AddMinutes(minutes);
        }

        return dateTime;
    }
    
    private async Task<Accident?> ParseAccident(string[] fields)
    {
        if (fields[0] is "NA")
            return null;

        var textInfo = CultureInfo.GetCultureInfo("en-EN").TextInfo;
        var accident = new Accident(fields[0]);
        await Task.Run(() =>
        {
            fields = fields.ToArray();
            for(var i = 0; i < fields.Length; i++)
                if (i > 4)
                    fields[i] = textInfo.ToTitleCase(fields[i]);
            
            if (fields[1] is not "NA" && fields[1].Length != 0)
            {
                var success = DateTime.TryParse(fields[1], out var dateTime);
                if (success)
                    accident.PublicationDate = dateTime.ToLocalTime();
                else
                    Console.WriteLine($"Could not parse date: {fields[1]}", ConsoleColor.Red);
            }

            if (fields[3] is not "NA" && fields[3].Length != 0)
                accident.Title = fields[3];
            if (fields[4] is not "NA" && fields[4].Length != 0)
                accident.Description = fields[4];
            if (fields[5] is not "NA" && fields[5].Length != 0)
            {
                var success = int.TryParse(fields[5], out var count);
                if (success)
                    accident.NumberOfAccidents = count;
                else
                    Console.WriteLine($"Could not parse NoA: {fields[5]}", ConsoleColor.Red);
            }

            if (fields[6] is not "NA" && fields[6].Length != 0)
                accident.Period = fields[6][0];
            if (fields[7] is not "NA" && fields[7].Length != 0)
                accident.DayOfTheWeek = fields[7];
            if (fields[8] is not "NA" && fields[8].Length != 0)
                accident.ExactLocation = accident.Street = fields[8];
            if (fields[9] is not "NA" && fields[9].Length != 0)
                accident.State = fields[9];
            if (fields[10] is not "NA" && fields[10].Length != 0)
                accident.County = fields[10];
            if (fields[11] is not "NA" && fields[11].Length != 0)
                accident.District = fields[11];
            if (fields[12] is not "NA" && fields[12].Length != 0)
                accident.Subdistrict = fields[12];
            if (fields[13] is not "NA" && fields[13].Length != 0)
                accident.Surface = fields[13];
            if (fields[14] is not "NA" && fields[14].Length != 0)
                accident.Country = fields[14];
            if (fields[15] is not "NA" && fields[15].Length != 0)
                accident.Type = fields[15];
            if (fields[16] is not "NA" && fields[16].Length != 0)
            {
                var success = int.TryParse(fields[16], out var count);
                if (success)
                    accident.Casualties = count;
                else
                    Console.WriteLine($"Could not parse casualties: {fields[16]}", ConsoleColor.Red);
            }

            if (fields[17] is not "NA" && fields[17].Length != 0)
            {
                var success = int.TryParse(fields[17], out var count);
                if (success)
                    accident.Injuries = count;
                else
                    Console.WriteLine($"Could not parse injuries: {fields[17]}", ConsoleColor.Red);
            }

            if (fields[18] is not "NA" && fields[18].Length != 0)
                accident.Cause = fields[18];
            if (fields[19] is not "NA" && fields[19].Length != 0)
                accident.PrimaryVehicle = fields[19];
            if (fields[20] is not "NA" && fields[20].Length != 0)
                accident.SecondaryVehicle = fields[20];
            if (fields[21] is not "NA" && fields[21].Length != 0)
                accident.TertiaryVehicle = fields[21];
            if (fields[22] is not "NA" && fields[22].Length != 0)
                accident.OtherVehicles = [fields[22]];
            if (fields[23] is not "NA" && fields[23].Substring(1, fields[23].Length - 2).Length != 0)
            {
                var ages = new List<int>();
                var agesString = fields[23].Trim();
                
                agesString = agesString
                    .Substring(1, agesString.Length - 2);
                
                var ageStrings = agesString
                    .Split(',')
                    .Select(s => s.Trim())
                    .Where(s => s.Length > 0);
                
                foreach (var ageString in ageStrings)
                {
                    var success = int.TryParse(ageString, out var age);
                    if (success)
                        ages.Add(age);
                    else
                        Console.WriteLine($"Could not parse ages: {ageString} {fields[23]}", ConsoleColor.Red);
                }

                accident.Ages = ages.ToArray();
            }

            if (fields[24] is not "NA" && fields[24].Length != 0)
            {
                var dateTime = ParseDateTime(fields[24]);
                if (dateTime is not null)
                    accident.DateTime = dateTime.Value.ToLocalTime();
                else
                    Console.WriteLine($"Could not parse date: {fields[24]}", ConsoleColor.Red);
            }
        });
        return accident;
    }

    private async Task<List<Accident>> LoadAccidentsFromJson()
    {
        if (!File.Exists(JsonPath))
            return [];
        var json = await File.ReadAllTextAsync(JsonPath);
        var accidents = JsonConvert.DeserializeObject<List<Accident>>(json);
        return accidents ?? [];
    }

    private async Task<List<Accident>> LoadAccidents()
    {
        var accidents = await LoadAccidentsFromJson();
        var uri = Path.GetFullPath(FilePath);
        var tasks = new List<Task<Accident?>>();
        if (File.Exists(uri))
        {
            using var sr = new StreamReader(uri);
            _ = await sr.ReadLineAsync();
            while (await sr.ReadLineAsync() is { } line)
            {
                var fields = line.Split(';');
                if (fields.Length < 25)
                    continue;
                var task = ParseAccident(fields);
                tasks.Add(task);
            }
        }
        else
            Console.WriteLine("The file does not exist.");

        _ = InvokeAsync(StateHasChanged);

        await Task.WhenAll(tasks);
        var newAccidents = tasks
            .Select(t => t.Result)
            .OfType<Accident>()
            .Where(a => !accidents.Contains(a))
            .ToList();
        AccidentCount = tasks.Count;
        var awaiter = GetCoordinates(newAccidents).GetAwaiter();
        awaiter.OnCompleted(SaveAccidentsToJson);
        return accidents;
    }

    private async Task SaveAccidentsToJsonAsync()
    {
        var json = JsonConvert.SerializeObject(Accidents);
        await File.WriteAllTextAsync(JsonPath, json);
    }

    private void SaveAccidentsToJson()
    {
        var json = JsonConvert.SerializeObject(Accidents);
        File.WriteAllText(JsonPath, json);
    }

    private async Task GetCoordinates(IEnumerable<Accident> accidents)
    {
        NewAccidents = new Queue<Accident>(accidents);
        while (NewAccidents.Count > 0)
        {
            var accident = NewAccidents.Dequeue();
            if (TriedUrls.Contains(accident.Url))
                continue;
            LoadingOffset = 1;
            LatLng? coords = null;
            try
            {
                coords = await LocationService.GetCoordinates(accident);
            }
            catch (ArgumentException ex)
            {
                TriedUrls.Add(ex.Message);
                await LocalStorage.SetItemAsync("tried_urls", TriedUrls);
            }
            
            if (coords is not null)
            {
                accident.Coordinates = coords;
                Accidents.Add(accident);
            }

            await Task.Delay(1000);
            await SaveAccidentsToJsonAsync();
            LoadingOffset = 0;
            _ = InvokeAsync(StateHasChanged);
        }
    }

    private static string GetPositionString(Point position)
    {
        var top = (position.Y - 56).ToString(CultureInfo.InvariantCulture);
        var left = (position.X - 28).ToString(CultureInfo.InvariantCulture);
        //return $"top: {top}px; left: {left}px";
        return $"transform: translate({left}px, {top}px); ";
    }

    private async Task<List<AccidentGroup>> GetGroups(List<Accident> accidents)
    {
        var bounds = CurrentBounds;
        var divisor = 4;
        var dy = Math.Round((bounds.NorthWest.Lat - bounds.SouthEast.Lat) / divisor, 2);
        var dx = Math.Round((bounds.SouthEast.Lng - bounds.NorthWest.Lng) / (divisor * 9.0 / 16.0), 2);
        var query = accidents.AsQueryable();
        var grouping = query.GroupBy(a =>
            new
            {
                X = Math.Ceiling(a.Coordinates.Lng / dx),
                Y = Math.Ceiling(a.Coordinates.Lat / dy)
            }
        );
        var groups = grouping.Select(g =>
            new AccidentGroup(
                new LatLng(
                    g.Average(a => a.Coordinates.Lat),
                    g.Average(a => a.Coordinates.Lng)
                ),
                g.ToList()
            )
        ).ToList();
        foreach (var group in groups)
        {
            group.Position = await MapService.Project(group.Coordinates);
        }

        return groups.ToList();
    }

    public void OnMapResized(Point newSize)
    {
        MapSize = (newSize.X, newSize.Y);
        Console.WriteLine(MapSize);
    }

    private async Task AccidentHovered(Accident accident)
    {
        Zooming = true;
        await MapService.SetView(accident.Latitude, accident.Longitude, 18);
    }

    private async Task AccidentTabUnhovered()
    {
        //Zooming = false;
        //await MapService.SetView(OriginalPosition.Latitude, OriginalPosition.Longitude, OriginalPosition.Zoom ?? 14);
    }

    private async Task AccidentTabHovered()
    {
        var (latitude, longitude, zoom) = await MapService.GetCurrentPosition();
        var point = await MapService.Project(new LatLng(latitude, longitude));
        Console.WriteLine(point);
        OriginalPosition = new Position(latitude, longitude, zoom);
    }

    private async Task OnMapMoved()
    {
        foreach (var group in DisplayGroups)
        {
            group.Position = await MapService.Project(group.Coordinates);
        }

        _ = InvokeAsync(StateHasChanged);
    }

    private async Task OnMapLoaded()
    {
        await AccidentsLoading;
        MapSize = await MapService.GetPixelSize();
        CurrentBounds = await MapService.GetBounds();
        DisplayAccidents = FilteredAccidents.Where(a => CurrentBounds.Contains(a.Coordinates)).ToList();
        foreach (var accident in DisplayAccidents)
        {
            accident.ScreenPosition = await MapService.Project(accident.Coordinates);
        }

        DisplayGroups = await GetGroups(DisplayAccidents);

        StateHasChanged();
    }

    private async Task OnZoomEnded()
    {
        if(!Zooming)
            DisplayGroups = await GetGroups(DisplayAccidents);
    }

    private async Task OnMapMoveEnded()
    {
        if(!Zooming)
            CurrentBounds = await MapService.GetBounds();
        DisplayAccidents = FilteredAccidents.Where(a => CurrentBounds.Contains(a.Coordinates)).ToList();
        foreach (var accident in DisplayAccidents)
        {
            accident.ScreenPosition = await MapService.Project(accident.Coordinates);
        }

        DisplayGroups = await GetGroups(DisplayAccidents);

        StateHasChanged();
    }

    private async Task ShowPopup(AccidentGroup group)
    {
        var options = new DialogOptions
        {
            Position = DialogPosition.Custom,
            NoHeader = true,
            FullWidth = true,
            ClassBackground = "",
            MaxWidth = MaxWidth.ExtraSmall
        };

        var parameters = new DialogParameters<PopupDialog>
        {
            { x => x.Group, group },
            { x => x.Height, (int)MapSize.Y }
        };

        await DialogService.ShowAsync<PopupDialog>("", parameters, options);
    }
    
    private void DayChanged(string? day)
    {
        var filter = new Filter(
            day,
            a => a.DayOfTheWeek == day
        );
        Filters.Remove("Day");
        if(day is not null)
            Filters.Add("Day", filter);

        ApplyFilters();
    }
    
    private void SurfaceChanged(string? surface)
    {
        var filter = new Filter(
            surface,
            a => a.Surface == surface
        );
        Filters.Remove("Surface");
        if(surface is not null)
            Filters.Add("Surface", filter);

        ApplyFilters();
    }
    
    private void TypeChanged(string? type)
    {
        var filter = new Filter(
            type,
            a => a.Type == type
        );
        Filters.Remove("Type");
        if(type is not null)
            Filters.Add("Type", filter);

        ApplyFilters();
    }
    
    private void CauseChanged(string? cause)
    {
        var filter = new Filter(
            cause,
            a => a.Cause == cause
        );
        Filters.Remove("Cause");
        if(cause is not null)
            Filters.Add("Cause", filter);

        ApplyFilters();
    }

    private void ValueChanged(string name, string? value, Func<Accident, bool> predicate)
    {
        var filter = new Filter(
            value,
            predicate
        );
        Filters.Remove(name);
        if(value is not null)
            Filters.Add(name, filter);
        
        ApplyFilters();
    }

    private HashSet<string> GetUnique(Func<Accident, string?> property) =>
        [..Accidents.Select(property).OfType<string>()];
    
    private void ApplyFilters() => FilteredAccidents = Accidents.Where(a => Filters.All(f => f.Value.Invoke(a))).ToList();
    
    private void InjuriesOnlyChanged(bool check)
    {
        InjuriesOnly = check;
        if (InjuriesOnly)
            Filters.Add("Injuries", new Filter(true, a => a.Injuries > 0));
        else
            Filters.Remove("Injuries");
        ApplyFilters();
    }
    
    private void CasualtiesOnlyChanged(bool check)
    {
        CasualtiesOnly = check;
        if (CasualtiesOnly)
            Filters.Add("Casualties", new Filter(true, a => a.Casualties > 0));
        else
            Filters.Remove("Casualties");
        ApplyFilters();
    }

    private async Task RowClicked(Accident accident)
    {
        await MapService.SetView(accident.Latitude, accident.Longitude, 16);
    }

    private void ManualOnlyChanged(bool check)
    {
        ManualOnly = check;
        if (ManualOnly)
            Filters.Add("Manual", new Filter(true, a => a.IsManual));
        else
            Filters.Remove("Manual");
        ApplyFilters();
    }

    private bool ManualUrlLoading { get; set; } = false;
    public bool FiltersExpanded { get; set; }
    public DateRange? SelectedDateRange { get; set; }


    private async Task<int> RunPython(string command)
    {
        var process = new Process();

        process.StartInfo.FileName = "cmd.exe";
        process.StartInfo.Arguments = "/c " + command;
        process.StartInfo.RedirectStandardOutput = true;
        process.StartInfo.RedirectStandardError = true;
        process.StartInfo.UseShellExecute = false;
        process.StartInfo.CreateNoWindow = true;

        process.Start();
        
        await process.WaitForExitAsync();
        return process.ExitCode;
    }

    private async Task AddManualClick()
    {
        ManualUrlLoading = true;
        await InvokeAsync(StateHasChanged);
        _ = Task.Run(async () =>
        {
            var url = ManualUrl;

            Snackbar.Add("Article scraping and processing...", Severity.Info);
            var exitCode = await RunPython($"python3 main.py {url}");
            Snackbar.Add("Article scraped and processed.", Severity.Info);
            exitCode = await RunPython($"python3 clean.py");
            Snackbar.Add("Output cleaned.", Severity.Success);
            if (exitCode != 0)
            {
                Console.WriteLine("Command failed with exit code: " + exitCode);
                Snackbar.Add("Error", Severity.Error);
            }
            else
            {
                ManualUrl = string.Empty;
                var uri = Path.GetFullPath("./cleaned_output.csv");
                if (File.Exists(uri))
                {
                    using var sr = new StreamReader(uri);
                    _ = await sr.ReadLineAsync();
                    while (await sr.ReadLineAsync() is { } line)
                    {
                        var fields = line.Split(';');
                        if (fields.Length < 25)
                            continue;
                        var accident = await ParseAccident(fields);
                        Snackbar.Add("Data parsed", Severity.Success);
                        if (accident is not null)
                        {
                            accident.IsManual = true;
                            if (NewAccidents.Count == 0)
                            {
                                Snackbar.Add("Geolocation in progress...", Severity.Info);
                                var coordinates = await LocationService.GetCoordinates(accident);
                                if (coordinates is not null)
                                {
                                    accident.Coordinates = coordinates;
                                    Snackbar.Add("Geolocation successful!", Severity.Success);
                                }
                                else
                                    Snackbar.Add($"Geolocation failed! Data: {accident.Street} {accident.Subdistrict} {accident.District} {accident.City} {accident.County} {accident.State} {accident.Country}", Severity.Info);
                                Accidents.Add(accident);
                            }
                            else
                            {
                                NewAccidents.Enqueue(accident);
                                Snackbar.Add("Added to geolocation queue", Severity.Info);
                            }
                            AccidentCount++;
                        }
                        else
                        {
                            Snackbar.Add("Error", Severity.Error);
                        }
                    }
                }
                else
                    Snackbar.Add("The file does not exist", Severity.Error);
            }

            Snackbar.Add("Done.", Severity.Success);
            ManualUrlLoading = false;
            StateHasChanged();
        });
    }

    public string GetFilterValue(string name) =>
        Filters.ContainsKey(name) ? Filters[name].ToString() : string.Empty;
    
    private void SelectedDateRangeChanged(DateRange? dateRange)
    {
        SelectedDateRange = dateRange;
        Filters.Remove("Date");
        if(dateRange is not null)
            Filters.Add("Date", 
                new Filter(
                    dateRange,
                    a => a.DateTime > dateRange.Start && a.DateTime < dateRange.End
                )
            ); 
        
        ApplyFilters();
    }
}