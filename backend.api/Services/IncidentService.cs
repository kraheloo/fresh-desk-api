using ServiceDeskDashboard.API.Models;
using ServiceDeskDashboard.API.Models.DTOs;

namespace ServiceDeskDashboard.API.Services;

public interface IIncidentService
{
    Task<IncidentCountsResponse> GetIncidentCountsAsync(string? username, int days = 30);
}

public class IncidentService : IIncidentService
{
    private readonly IFreshServiceClient _freshServiceClient;
    private readonly ICsvDataService _csvDataService;
    private readonly ILogger<IncidentService> _logger;

    public IncidentService(
        IFreshServiceClient freshServiceClient,
        ICsvDataService csvDataService,
        ILogger<IncidentService> logger)
    {
        _freshServiceClient = freshServiceClient;
        _csvDataService = csvDataService;
        _logger = logger;
    }

    public async Task<IncidentCountsResponse> GetIncidentCountsAsync(string? username, int days = 30)
    {
        _logger.LogInformation("Getting incident counts for user: {Username}, days: {Days}", username ?? "ALL", days);

        // Get allowed department IDs
        HashSet<long>? allowedDeptIds = null;
        var accessibleDepartments = new List<DepartmentAccessDto>();

        if (!string.IsNullOrEmpty(username))
        {
            allowedDeptIds = _csvDataService.GetAllowedDepartmentIds(username);
            
            if (allowedDeptIds.Any())
            {
                var departments = _csvDataService.GetDepartments();
                accessibleDepartments = departments
                    .Where(d => allowedDeptIds.Contains(d.Id))
                    .Select(d => new DepartmentAccessDto
                    {
                        DepartmentId = d.Id,
                        DepartmentName = d.Name
                    })
                    .ToList();
            }
        }

        // Fetch tickets
        var cutoffDate = DateTime.UtcNow.AddDays(-days);
        var tickets = await _freshServiceClient.GetTicketsAsync(cutoffDate);

        // Filter and count incidents
        var incidents = tickets.Where(t => t.Type == "Incident" && 
                                           t.UpdatedAt.HasValue &&
                                           t.UpdatedAt.Value >= cutoffDate).ToList();

        // Apply department filter if needed
        if (allowedDeptIds != null && allowedDeptIds.Any())
        {
            incidents = incidents.Where(i => i.DepartmentId.HasValue && 
                                            allowedDeptIds.Contains(i.DepartmentId.Value)).ToList();
        }

        // Count by status
        // Status codes: 2 = Open, 3 = Pending, 4 = Resolved, 5 = Closed
        var totalOpen = incidents.Count(i => i.Status == 2);
        var totalPending = incidents.Count(i => i.Status == 3);
        var totalResolved = incidents.Count(i => i.Status == 4);
        var totalClosed = incidents.Count(i => i.Status == 5);
        var totalOpenAndPending = totalOpen + totalPending;
        
        var totalTickets = incidents.Count;
        var totalResolvedAndClosed = totalResolved + totalClosed;
        var resolutionRate = totalTickets > 0 ? (double)totalResolvedAndClosed / totalTickets * 100 : 0;

        return new IncidentCountsResponse
        {
            TotalOpen = totalOpen,
            TotalPending = totalPending,
            TotalResolved = totalResolved,
            TotalClosed = totalClosed,
            TotalOpenAndPending = totalOpenAndPending,
            ResolutionRate = Math.Round(resolutionRate, 1),
            Days = days,
            Username = username,
            DepartmentFilterApplied = allowedDeptIds != null && allowedDeptIds.Any(),
            GeneratedAt = DateTime.UtcNow,
            AccessibleDepartments = accessibleDepartments
        };
    }
}
