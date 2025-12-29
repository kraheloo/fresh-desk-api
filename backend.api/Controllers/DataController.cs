using Microsoft.AspNetCore.Mvc;
using ServiceDeskDashboard.API.Models.DTOs;
using ServiceDeskDashboard.API.Services;

namespace ServiceDeskDashboard.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DataController : ControllerBase
{
    private readonly IDataService _dataService;
    private readonly ILogger<DataController> _logger;

    public DataController(IDataService dataService, ILogger<DataController> logger)
    {
        _dataService = dataService;
        _logger = logger;
    }

    [HttpGet("counts")]
    public async Task<ActionResult<IncidentCountsResponse>> GetIncidentCounts(
        [FromQuery] string? username = null,
        [FromQuery] int days = 30)
    {
        try
        {
            _logger.LogInformation("Getting incident counts for user: {Username}, days: {Days}", username ?? "ALL", days);
            
            if (days < 1 || days > 365)
            {
                return BadRequest("Days must be between 1 and 365");
            }

            var result = await _dataService.GetCountsAsync(username, days);
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting incident counts");
            return StatusCode(500, "Error retrieving incident counts");
        }
    }
}
