namespace ServiceDeskDashboard.API.Models.DTOs;

/// <summary>
/// DTO for user information
/// </summary>
public class UserDto
{
    public string Username { get; set; } = string.Empty;
}

/// <summary>
/// Wrapper DTO for combined data responses. This is the main response object from the API to the client
/// </summary>
public class DataMetricsResponse
{
    public IncidentCountsResponse IncidentCounts { get; set; } = new();
    public ServiceCountsResponse ServiceCounts { get; set; } = new();
}

/// <summary>
/// DTO for ticket details
/// </summary>
public class TicketDto
{
    public long Id { get; set; }
    public string? Subject { get; set; }
    public int Status { get; set; }
    public string StatusName { get; set; } = string.Empty;
    public DateTime? CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
    public string? Url { get; set; }
}

/// <summary>
/// DTO for incident counts response
/// </summary>
public class IncidentCountsResponse
{
    public int TotalOpen { get; set; }
    public int TotalPending { get; set; }
    public int TotalResolved { get; set; }
    public int TotalClosed { get; set; }
    public int TotalOpenAndPending { get; set; }
    public int TotalCompleted { get; set; }
    public int TotalInProgress { get; set; }
    public int TicketsRaised { get; set; }
    public double ResolutionRate { get; set; }
    public int Days { get; set; }
    public string? Username { get; set; }
    public bool DepartmentFilterApplied { get; set; }
    public DateTime GeneratedAt { get; set; }
    public List<DepartmentAccessDto> AccessibleDepartments { get; set; } = new();
    public List<TicketDto> OldestOpenTickets { get; set; } = new();
}

/// <summary>
/// DTO for service counts response
/// </summary>
public class ServiceCountsResponse
{
    public int TotalOpen { get; set; }
    public int TotalPending { get; set; }
    public int TotalResolved { get; set; }
    public int TotalClosed { get; set; }
    public int TotalOpenAndPending { get; set; }
    public int TotalCompleted { get; set; }
    public int TotalInProgress { get; set; }
    public int TicketsRaised { get; set; }
    public double ResolutionRate { get; set; }
    public int Days { get; set; }
    public string? Username { get; set; }
    public bool DepartmentFilterApplied { get; set; }
    public DateTime GeneratedAt { get; set; }
    public List<DepartmentAccessDto> AccessibleDepartments { get; set; } = new();
    public List<TicketDto> OldestOpenTickets { get; set; } = new();
}

/// <summary>
/// DTO for department access information
/// </summary>
public class DepartmentAccessDto
{
    public long DepartmentId { get; set; }
    public string DepartmentName { get; set; } = string.Empty;
}
