namespace ServiceDeskDashboard.API.Models.DTOs;

public class UserDto
{
    public string Username { get; set; } = string.Empty;
}

public class IncidentCountsResponse
{
    public int TotalOpen { get; set; }
    public int TotalPending { get; set; }
    public int TotalResolved { get; set; }
    public int TotalClosed { get; set; }
    public int TotalOpenAndPending { get; set; }
    public double ResolutionRate { get; set; }
    public int Days { get; set; }
    public string? Username { get; set; }
    public bool DepartmentFilterApplied { get; set; }
    public DateTime GeneratedAt { get; set; }
    public List<DepartmentAccessDto> AccessibleDepartments { get; set; } = new();
}

public class DepartmentAccessDto
{
    public long DepartmentId { get; set; }
    public string DepartmentName { get; set; } = string.Empty;
}
