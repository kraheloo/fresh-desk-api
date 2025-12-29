namespace ServiceDeskDashboard.API.Models;

using System.Text.Json.Serialization;

public class Department
{
    public long Id { get; set; }
    public string Name { get; set; } = string.Empty;
}

public class Perimeter
{
    public int Id { get; set; }
    public string PerimeterName { get; set; } = string.Empty;
    public long BuId { get; set; }
    public string BuName { get; set; } = string.Empty;
}

public class UserAcl
{
    public string User { get; set; } = string.Empty;
    public string AccessLevel { get; set; } = string.Empty;
    public int Id { get; set; }
}

public class FreshServiceTicket
{
    [JsonPropertyName("id")]
    public long Id { get; set; }
    
    [JsonPropertyName("type")]
    public string? Type { get; set; }
    
    [JsonPropertyName("status")]
    public int Status { get; set; }
    
    [JsonPropertyName("department_id")]
    public long? DepartmentId { get; set; }
    
    [JsonPropertyName("updated_at")]
    public DateTime? UpdatedAt { get; set; }
    
    [JsonPropertyName("subject")]
    public string? Subject { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime? CreatedAt { get; set; }
}
