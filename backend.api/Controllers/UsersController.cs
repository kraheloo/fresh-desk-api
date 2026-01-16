using Microsoft.AspNetCore.Mvc;
using ServiceDeskDashboard.API.Models.DTOs;
using ServiceDeskDashboard.API.Services;

namespace ServiceDeskDashboard.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IDataProvider _dataProvider;
    private readonly ILogger<UsersController> _logger;

    public UsersController(IDataProvider dataProvider, ILogger<UsersController> logger)
    {
        _dataProvider = dataProvider;
        _logger = logger;
    }

    [HttpGet]
    public ActionResult<List<UserDto>> GetUsers()
    {
        try
        {
            var users = _dataProvider.GetAllUsers();
            var userDtos = users.Select(u => new UserDto { Username = u }).ToList();
            
            _logger.LogInformation("Retrieved {Count} users", userDtos.Count);
            return Ok(userDtos);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving users");
            return StatusCode(500, "Error retrieving users");
        }
    }
}
