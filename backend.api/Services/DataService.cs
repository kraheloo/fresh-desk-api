using ServiceDeskDashboard.API.Models;
using ServiceDeskDashboard.API.Models.DTOs;

namespace ServiceDeskDashboard.API.Services;

public interface IDataService
{
    Task<DataMetricsResponse> GetCountsAsync(string? username, int days = 30);
}

public class DataService : IDataService
{
    private readonly IFreshServiceClient _freshServiceClient;
    private readonly ICsvDataService _csvDataService;
    private readonly ILogger<DataService> _logger;
    private readonly IConfiguration _configuration;

    public DataService(
        IFreshServiceClient freshServiceClient,
        ICsvDataService csvDataService,
        ILogger<DataService> logger,
        IConfiguration configuration)
    {
        _freshServiceClient = freshServiceClient;
        _csvDataService = csvDataService;
        _logger = logger;
        _configuration = configuration;
    }

    public async Task<DataMetricsResponse> GetCountsAsync(string? username, int days = 30)
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

        // Filter and count service requests
        var serviceRequests = tickets.Where(t => t.Type == "Service Request" && 
                                           t.UpdatedAt.HasValue &&
                                           t.UpdatedAt.Value >= cutoffDate).ToList();

        // Apply department filter if needed for incidents
        if (allowedDeptIds != null && allowedDeptIds.Any())
        {
            incidents = incidents.Where(i => i.DepartmentId.HasValue && 
                                            allowedDeptIds.Contains(i.DepartmentId.Value)).ToList();
        }

        // Apply department filter if needed for service requests
        if (allowedDeptIds != null && allowedDeptIds.Any())
        {
            serviceRequests = serviceRequests.Where(i => i.DepartmentId.HasValue && 
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

        // Get 3 oldest open tickets for incidents (status 2 = Open)
        var oldestOpenIncidents = incidents
            .Where(i => i.Status == 2 && i.CreatedAt.HasValue)
            .OrderBy(i => i.CreatedAt)
            .Take(3)
            .Select(i => new TicketDto
            {
                Id = i.Id,
                Subject = i.Subject,
                Status = i.Status,
                StatusName = GetStatusName(i.Status),
                CreatedAt = i.CreatedAt,
                UpdatedAt = i.UpdatedAt,
                Url = $"https://{_configuration["FreshService:InstanceUrl"]}/helpdesk/tickets/{i.Id}"
            })
            .ToList();

        var dataMetrics = new DataMetricsResponse();
        dataMetrics.IncidentCounts = new IncidentCountsResponse
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
            AccessibleDepartments = accessibleDepartments,
            OldestOpenTickets = oldestOpenIncidents
        };

        // Count service requests by status
        var srTotalOpen = serviceRequests.Count(sr => sr.Status == 2);
        var srTotalPending = serviceRequests.Count(sr => sr.Status == 3);
        var srTotalResolved = serviceRequests.Count(sr => sr.Status == 4);
        var srTotalClosed = serviceRequests.Count(sr => sr.Status == 5);
        var srTotalOpenAndPending = srTotalOpen + srTotalPending;
        
        var srTotalTickets = serviceRequests.Count;
        var srTotalResolvedAndClosed = srTotalResolved + srTotalClosed;
        var srResolutionRate = srTotalTickets > 0 ? (double)srTotalResolvedAndClosed / srTotalTickets * 100 : 0;

        // Get 3 oldest open tickets for service requests (status 2 = Open)
        var oldestOpenServiceRequests = serviceRequests
            .Where(sr => sr.Status == 2 && sr.CreatedAt.HasValue)
            .OrderBy(sr => sr.CreatedAt)
            .Take(3)
            .Select(sr => new TicketDto
            {
                Id = sr.Id,
                Subject = sr.Subject,
                Status = sr.Status,
                StatusName = GetStatusName(sr.Status),
                CreatedAt = sr.CreatedAt,
                UpdatedAt = sr.UpdatedAt,
                Url = $"https://{_configuration["FreshService:InstanceUrl"]}/helpdesk/tickets/{sr.Id}"
            })
            .ToList();

        dataMetrics.ServiceCounts = new ServiceCountsResponse
        {
            TotalOpen = srTotalOpen,
            TotalPending = srTotalPending,
            TotalResolved = srTotalResolved,
            TotalClosed = srTotalClosed,
            TotalOpenAndPending = srTotalOpenAndPending,
            ResolutionRate = Math.Round(srResolutionRate, 1),
            Days = days,
            Username = username,
            DepartmentFilterApplied = allowedDeptIds != null && allowedDeptIds.Any(),
            GeneratedAt = DateTime.UtcNow,
            AccessibleDepartments = accessibleDepartments,
            OldestOpenTickets = oldestOpenServiceRequests
        };

        return dataMetrics;
    }

    private static string GetStatusName(int status)
    {
        return status switch
        {
            2 => "Open",
            3 => "Pending",
            4 => "Resolved",
            5 => "Closed",
            _ => "Unknown"
        };
    }
}
