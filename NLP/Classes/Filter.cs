namespace NLP.Classes;

public class Filter(object? value, Func<Accident, bool> predicate)
{
    public object? Value { get; } = value;
    private Func<Accident, bool> Predicate { get; set; } = predicate;
    public bool Invoke(Accident accident) => Predicate.Invoke(accident);

    public override string ToString()
    {
        return Value?.ToString() ?? string.Empty;
    }
}