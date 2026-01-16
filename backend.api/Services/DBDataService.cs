using ServiceDeskDashboard.API.Models;
using Npgsql;

namespace ServiceDeskDashboard.API.Services;

public class DBDataService : IDataProvider
{
    private readonly string _connectionString;
    private readonly ILogger<DBDataService> _logger;
    private List<Department>? _departments;
    private List<Perimeter>? _perimeters;
    private List<UserAcl>? _userAcls;

    public DBDataService(IConfiguration configuration, ILogger<DBDataService> logger)
    {
        _connectionString = configuration["Database:ConnectionString"] 
            ?? throw new InvalidOperationException("Database connection string not configured");
        _logger = logger;
    }

    public List<Department> GetDepartments()
    {
        if (_departments != null && _departments.Count > 0) 
            return _departments;

        _logger.LogInformation("Loading departments from database");

        _departments = new List<Department>();

        try
        {
            using var connection = new NpgsqlConnection(_connectionString);
            connection.Open();

            using var command = connection.CreateCommand();
            command.CommandText = "SELECT id, name FROM departments ORDER BY id";

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                _departments.Add(new Department
                {
                    Id = (long)reader.GetDouble(0),
                    Name = reader.GetString(1)
                });
            }

            _logger.LogInformation("Loaded {Count} departments from database", _departments.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading departments from database");
            throw;
        }

        return _departments;
    }

    public List<Perimeter> GetPerimeters()
    {
        if (_perimeters != null && _perimeters.Count > 0) 
            return _perimeters;

        _logger.LogInformation("Loading perimeters from database");

        _perimeters = new List<Perimeter>();

        try
        {
            using var connection = new NpgsqlConnection(_connectionString);
            connection.Open();

            using var command = connection.CreateCommand();
            command.CommandText = @"
                SELECT 
                  p.id,
                  p.name as perimeter_name,
                  pd.department_id as bu_id,
                  d.name as bu_name
                FROM perimeters p
                LEFT JOIN perimeter_departments pd ON p.id = pd.perimeter_id
                LEFT JOIN departments d ON pd.department_id = d.id
                ORDER BY p.id, pd.department_id";

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                _perimeters.Add(new Perimeter
                {
                    Id = reader.GetInt32(0),
                    PerimeterName = reader.GetString(1),
                    BuId = !reader.IsDBNull(2) ? (long)reader.GetDouble(2) : 0,
                    BuName = !reader.IsDBNull(3) ? reader.GetString(3) : string.Empty
                });
            }

            _logger.LogInformation("Loaded {Count} perimeters from database", _perimeters.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading perimeters from database");
            throw;
        }

        return _perimeters;
    }

    public List<UserAcl> GetUserAcls()
    {
        if (_userAcls != null && _userAcls.Count > 0) 
            return _userAcls;

        _logger.LogInformation("Loading ACLs from database");

        _userAcls = new List<UserAcl>();

        try
        {
            using var connection = new NpgsqlConnection(_connectionString);
            connection.Open();

            using var command = connection.CreateCommand();
            command.CommandText = @"
                SELECT 
                  id,
                  user_id as user,
                  CASE 
                    WHEN perimeter_id IS NOT NULL THEN 'Perimeter'
                    WHEN department_id IS NOT NULL THEN 'Business Unit'
                    ELSE 'Unknown'
                  END as access_level,
                  COALESCE(CAST(perimeter_id AS bigint), CAST(department_id AS bigint)) as access_id
                FROM acls
                ORDER BY user_id, id";

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                _userAcls.Add(new UserAcl
                {
                    Id = (int)reader.GetInt64(3),
                    User = reader.GetString(1),
                    AccessLevel = reader.GetString(2)
                });
            }

            _logger.LogInformation("Loaded {Count} user ACLs from database", _userAcls.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading ACLs from database");
            throw;
        }

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
