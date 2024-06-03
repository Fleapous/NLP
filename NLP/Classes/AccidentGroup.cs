using System.Text;
using Microsoft.Extensions.Primitives;

namespace NLP.Classes;

public class AccidentGroup(LatLng coordinates, IEnumerable<Accident>? accidents = null)
{
    public Point? Position { get; set; }
    public LatLng Coordinates { get; set; } = coordinates;
    public List<Accident> Accidents { get; set; } = accidents?.ToList() ?? [];
    
    public override string ToString()
    {
        StringBuilder sb = new();
        sb.Append(Position);
        sb.Append(",\n[");
        foreach (var accident in Accidents)
            sb.Append(accident + ", ");
        sb.Append(']');
        return sb.ToString();
    }
}