using ServiceDeskDashboard.API.Models;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;
using System.Text;

namespace ServiceDeskDashboard.API.Services;

public interface IDataProvider
{
    List<Department> GetDepartments();
    List<Perimeter> GetPerimeters();
    List<UserAcl> GetUserAcls();
    List<string> GetAllUsers();
    HashSet<long> GetAllowedDepartmentIds(string username);
}

public class CsvDataService : IDataProvider
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<CsvDataService> _logger;
    private List<Department>? _departments;
    private List<Perimeter>? _perimeters;
    private List<UserAcl>? _userAcls;

    public CsvDataService(IConfiguration configuration, ILogger<CsvDataService> logger)
    {
        _configuration = configuration;
        _logger = logger;
    }

    public List<Department> GetDepartments()
    {
        if (_departments != null && _departments.Count > 0) return _departments;

        var path = _configuration["CsvPaths:Departments"] ?? "../data/departments.csv";
        var fullPath = Path.GetFullPath(path);

        _logger.LogInformation("Loading departments from: {Path}", fullPath);

        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            Encoding = Encoding.UTF8,
            HasHeaderRecord = true,
        };

        // detectEncodingFromByteOrderMarks = true handles UTF-8 BOM
        using var reader = new StreamReader(fullPath, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
        using var csv = new CsvReader(reader, config);

        _departments = new List<Department>();
        csv.Read();
        csv.ReadHeader();

        while (csv.Read())
        {
            if (long.TryParse(csv.GetField("ID"), out long id))
            {
                _departments.Add(new Department
                {
                    Id = id,
                    Name = csv.GetField("Name") ?? string.Empty
                });
            }
        }

        _logger.LogInformation("Loaded {Count} departments", _departments.Count);
        return _departments;
    }

    public List<Perimeter> GetPerimeters()
    {
        if (_perimeters != null && _perimeters.Count > 0) return _perimeters;

        var path = _configuration["CsvPaths:Perimeters"] ?? "../data/perimeters.csv";
        var fullPath = Path.GetFullPath(path);

        _logger.LogInformation("Loading perimeters from: {Path}", fullPath);

        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            Encoding = Encoding.UTF8,
            HasHeaderRecord = true,
        };

        // detectEncodingFromByteOrderMarks = true handles UTF-8 BOM
        using var reader = new StreamReader(fullPath, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
        using var csv = new CsvReader(reader, config);

        _perimeters = new List<Perimeter>();
        csv.Read();
        csv.ReadHeader();

        while (csv.Read())
        {
            if (int.TryParse(csv.GetField("Id"), out int id) &&
                long.TryParse(csv.GetField("BU_Id"), out long buId))
            {
                _perimeters.Add(new Perimeter
                {
                    Id = id,
                    PerimeterName = csv.GetField("PerimeterName") ?? string.Empty,
                    BuId = buId,
                    BuName = csv.GetField("BU_Name") ?? string.Empty
                });
            }
        }

        _logger.LogInformation("Loaded {Count} perimeters", _perimeters.Count);
        return _perimeters;
    }

    public List<UserAcl> GetUserAcls()
    {
        if (_userAcls != null) return _userAcls;

        var path = _configuration["CsvPaths:Acl"] ?? "../data/acl.csv";
        var fullPath = Path.GetFullPath(path);

        _logger.LogInformation("Loading ACLs from: {Path}", fullPath);

        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            Encoding = Encoding.UTF8,
            HasHeaderRecord = true,
        };

        // detectEncodingFromByteOrderMarks = true handles UTF-8 BOM
        using var reader = new StreamReader(fullPath, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
        using var csv = new CsvReader(reader, config);

        _userAcls = new List<UserAcl>();
        csv.Read();
        csv.ReadHeader();

        while (csv.Read())
        {
            if (int.TryParse(csv.GetField("Id"), out int id))
            {
                _userAcls.Add(new UserAcl
                {
                    User = csv.GetField("User") ?? string.Empty,
                    AccessLevel = csv.GetField("AccessLevel") ?? string.Empty,
                    Id = id
                });
            }
        }

        _logger.LogInformation("Loaded {Count} user ACLs", _userAcls.Count);
        return _userAcls;
    }

    public List<string> GetAllUsers()
    {
        var acls = GetUserAcls();
        return acls.Select(a => a.User).Distinct().OrderBy(u => u).ToList();
    }

    public HashSet<long> GetAllowedDepartmentIds(string username)
    {
        var userAcls = GetUserAcls().Where(a => a.User == username).ToList();
        
        if (!userAcls.Any())
        {
            _logger.LogWarning("No ACL found for user: {Username}", username);
            return new HashSet<long>();
        }

        var allowedDeptIds = new HashSet<long>();
        var perimeters = GetPerimeters();

        foreach (var acl in userAcls)
        {
            if (acl.AccessLevel == "Perimeter")
            {
                // Get all department IDs under this perimeter
                var deptIds = perimeters
                    .Where(p => p.Id == acl.Id)
                    .Select(p => p.BuId);
                
                foreach (var deptId in deptIds)
                {
                    allowedDeptIds.Add(deptId);
                }
            }
            else if (acl.AccessLevel == "Business Unit")
            {
                // Direct department access
                allowedDeptIds.Add(acl.Id);
            }
        }

        _logger.LogInformation("User {Username} has access to {Count} departments", username, allowedDeptIds.Count);
        return allowedDeptIds;
    }
}
