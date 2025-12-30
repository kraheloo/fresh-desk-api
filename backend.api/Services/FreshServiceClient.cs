using ServiceDeskDashboard.API.Models;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace ServiceDeskDashboard.API.Services;

public interface IFreshServiceClient
{
    Task<List<FreshServiceTicket>> GetTicketsAsync(DateTime updatedSince, int maxPages = 50);
}

public class FreshServiceClient : IFreshServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;
    private readonly ILogger<FreshServiceClient> _logger;

    public FreshServiceClient(HttpClient httpClient, IConfiguration configuration, ILogger<FreshServiceClient> logger)
    {
        _httpClient = httpClient;
        _configuration = configuration;
        _logger = logger;

        var apiKey = _configuration["FreshService:ApiKey"] ?? throw new InvalidOperationException("FreshService API key not configured");
        var baseUrl = _configuration["FreshService:ApiBaseUrl"] ?? throw new InvalidOperationException("FreshService base URL not configured");

        // Ensure base URL ends with / for proper path concatenation
        if (!baseUrl.EndsWith("/"))
        {
            baseUrl += "/";
        }

        _httpClient.BaseAddress = new Uri(baseUrl);
        
        var authToken = Convert.ToBase64String(Encoding.ASCII.GetBytes($"{apiKey}:X"));
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", authToken);
        _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public async Task<List<FreshServiceTicket>> GetTicketsAsync(DateTime updatedSince, int maxPages = 50)
    {
        var allTickets = new List<FreshServiceTicket>();
        var page = 1;
        const int perPage = 100;

        var updatedSinceStr = updatedSince.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ");

        _logger.LogInformation("Fetching tickets updated since: {UpdatedSince}", updatedSinceStr);

        while (page <= maxPages)
        {
            try
            {
                // Remove leading slash since BaseAddress now has trailing slash
                // Include fields parameter to ensure we get subject and other required fields
                var url = $"tickets?per_page={perPage}&page={page}&updated_since={updatedSinceStr}&include=requester,stats";
                _logger.LogInformation("Requesting URL: {BaseAddress}{Url}", _httpClient.BaseAddress, url);
                var response = await _httpClient.GetAsync(url);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("HTTP {StatusCode}: {ErrorContent}", response.StatusCode, errorContent);
                }
                
                response.EnsureSuccessStatusCode();

                var content = await response.Content.ReadAsStringAsync();
                var jsonDoc = JsonDocument.Parse(content);

                List<FreshServiceTicket> tickets;
                
                if (jsonDoc.RootElement.ValueKind == JsonValueKind.Array)
                {
                    tickets = JsonSerializer.Deserialize<List<FreshServiceTicket>>(content) ?? new List<FreshServiceTicket>();
                }
                else if (jsonDoc.RootElement.TryGetProperty("tickets", out var ticketsProperty))
                {
                    tickets = JsonSerializer.Deserialize<List<FreshServiceTicket>>(ticketsProperty.GetRawText()) ?? new List<FreshServiceTicket>();
                }
                else
                {
                    tickets = new List<FreshServiceTicket>();
                }

                if (!tickets.Any())
                {
                    _logger.LogInformation("No more tickets found on page {Page}", page);
                    break;
                }

                allTickets.AddRange(tickets);
                _logger.LogInformation("Page {Page}: Retrieved {Count} tickets (Total: {Total})", 
                    page, tickets.Count, allTickets.Count);

                if (tickets.Count < perPage)
                {
                    break;
                }

                page++;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching tickets on page {Page}", page);
                break;
            }
        }

        _logger.LogInformation("Total tickets retrieved: {Total}", allTickets.Count);
        return allTickets;
    }
}
