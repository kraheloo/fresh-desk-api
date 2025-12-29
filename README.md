# Service Desk Dashboard - Full Stack Application

A modern web application for monitoring and analyzing FreshService incidents and service requests with user-based access control.

## Architecture

- **Backend**: .NET 8.0 Web API
- **Frontend**: React 18 with Vite
- **Data**: CSV-based ACL (Access Control Lists)
- **Charts**: Recharts library

## Project Structure

```
fresh-desk-api/
├── backend.api/                    # .NET Backend
│   ├── Controllers/                # API endpoints
│   │   ├── DataController.cs      # Main data endpoint
│   │   └── UsersController.cs     # User management
│   ├── Models/                     # Data models and DTOs
│   │   ├── Models.cs              # Core models
│   │   └── DTOs/
│   │       └── ResponseDTOs.cs    # API response DTOs
│   ├── Services/                   # Business logic
│   │   ├── DataService.cs         # Main data aggregation service
│   │   ├── FreshServiceClient.cs  # FreshService API client
│   │   └── CsvDataService.cs      # CSV data handling
│   ├── appsettings.json           # Configuration
│   └── Program.cs                 # Application startup
├── client.dashboard/               # React Frontend
│   ├── src/
│   │   ├── components/            # UI components
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── MetricCard.jsx     # Metric display cards
│   │   │   ├── ResolutionChart.jsx # Resolution rate chart
│   │   │   ├── StatusBreakdown.jsx # Status bar chart
│   │   │   └── UserSelector.jsx   # User dropdown
│   │   ├── services/              # API client
│   │   │   └── api.js             # Axios API service
│   │   ├── App.jsx                # Main app component
│   │   └── main.jsx               # App entry point
│   ├── package.json
│   └── vite.config.js
├── data/                          # CSV data files
│   ├── departments.csv            # Department mappings
│   ├── perimeters.csv             # Perimeter to department mappings
│   └── acl.csv                    # User access control list
├── scripts/                       # Python utility scripts
│   ├── get_users.py              # Fetch users from FreshService
│   ├── get_incident_counts.py   # Test incident queries
│   └── requirements.txt          # Python dependencies
└── archive/                       # Legacy Python implementation
```

## Features

### Backend API

- **GET /api/users** - Retrieve all users from ACL
- **GET /api/data/counts** - Get incident and service request metrics with ACL filtering
  - Query parameters:
    - `username` (optional): Filter by user
    - `days` (default: 30): Time range in days
  - Returns: `DataMetricsResponse` with both incident and service request counts

### Frontend Dashboard

- User selection dropdown (populated from ACL)
- Time range selector (7, 14, 30, 60, 90 days)
- **Incident Metrics Section**:
  - Metric cards (Total, Open, Pending, Resolved, Closed, Open+Pending)
  - Resolution rate pie chart
  - Status breakdown bar chart
  - Accessible departments list
- **Service Request Metrics Section**:
  - Metric cards (Total, Open, Pending, Resolved, Closed, Open+Pending)
  - Resolution rate pie chart
  - Status breakdown bar chart

### Access Control

Two levels of access:
- **Perimeter**: Access to all departments under a perimeter
- **Business Unit**: Access to a specific department

## Prerequisites

- .NET 8.0 SDK
- Node.js 18+ and npm
- FreshService API credentials

## Setup

### 1. Configure Backend

Edit `backend.api/appsettings.json`:

```json
{
  "FreshService": {
    "BaseUrl": "https://your-domain.freshservice.com",
    "ApiKey": "YOUR_API_KEY_HERE"
  },
  "CsvFiles": {
    "DepartmentsPath": "../data/departments.csv",
    "PerimetersPath": "../data/perimeters.csv",
    "AclPath": "../data/acl.csv"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "AllowedHosts": "*"
}
```

### 2. Install Backend Dependencies

```bash
cd backend.api
dotnet restore
```

### 3. Install Frontend Dependencies

```bash
cd client.dashboard
npm install
```

## Running the Application

### Start Backend API

```bash
cd backend.api
dotnet run
```

Or use the VS Code task: `build` or `watch`

The API will be available at:
- HTTP: http://localhost:5000
- HTTPS: https://localhost:5001
- Swagger UI: http://localhost:5000/swagger

### Start Frontend

```bash
cd client.dashboard
npm run dev
```

The frontend will be available at: http://localhost:5173

## Usage

1. Open http://localhost:5173 in your browser
2. Select a user from the dropdown
3. Choose a time range (7-90 days)
4. View incident metrics in the first section
5. View service request metrics in the second section
6. Each section shows:
   - Total counts by status
   - Resolution rate visualization
   - Status breakdown chart
   - Accessible departments (incidents only)

## API Endpoints

### Get Users

```
GET /api/users
```

Response:
```json
[
  {
    "username": "john.doe"
  }
]
```

### Get Data Metrics

```
GET /api/data/counts?username=john.doe&days=30
```

Response:
```json
{
  "incidentCounts": {
    "totalOpen": 5,
    "totalPending": 3,
    "totalResolved": 15,
    "totalClosed": 10,
    "totalOpenAndPending": 8,
    "resolutionRate": 75.8,
    "days": 30,
    "username": "john.doe",
    "departmentFilterApplied": true,
    "generatedAt": "2025-12-29T10:30:00Z",
    "accessibleDepartments": [
      {
        "departmentId": 123,
        "departmentName": "IT Support"
      }
    ]
  },
  "serviceCounts": {
    "totalOpen": 8,
    "totalPending": 5,
    "totalResolved": 20,
    "totalClosed": 15,
    "totalOpenAndPending": 13,
    "resolutionRate": 72.9,
    "days": 30,
    "username": "john.doe",
    "departmentFilterApplied": true,
    "generatedAt": "2025-12-29T10:30:00Z",
    "accessibleDepartments": [
      {
        "departmentId": 123,
        "departmentName": "IT Support"
      }
    ]
  }
}
```

## Development

### Backend Development

```bash
cd backend.api
dotnet watch run
```

Or use VS Code tasks for building/watching.

### Frontend Development

```bash
cd client.dashboard
npm run dev
```

Hot reload is enabled for both backend and frontend.

## Building for Production

### Backend

```bash
cd backend.api
dotnet publish -c Release -o ./publish
```

### Frontend

```bash
cd client.dashboard
npm run build
```

The production build will be in the `dist/` folder.

## Environment Variables

### Frontend

Create `.env` in `client.dashboard/`:

```
VITE_API_URL=http://localhost:5000
```

For production, update this to your API URL.

## Troubleshooting

### CORS Issues

The backend is configured to allow requests from:
- http://localhost:3000
- http://localhost:5173

If using a different port, update the CORS policy in [Program.cs](backend.api/Program.cs).

### CSV File Path Issues

Ensure the CSV file paths in [appsettings.json](backend.api/appsettings.json) are correct relative to the API project directory.

### API Connection Failed

1. Verify the backend is running on port 5000
2. Check the API URL in frontend `.env` file (default: http://localhost:5000)
3. Check browser console for CORS errors
4. Verify FreshService API key in `appsettings.json`

### Data Not Updating After Code Changes

1. Rebuild the backend: `dotnet build` in `backend.api/`
2. Restart both backend and frontend servers
3. Clear browser cache if needed

### Charts Showing Same Values

Ensure the backend is rebuilt after any changes to `DataService.cs` so that the service request calculations are included.

## Technologies

### Backend
- .NET 8.0
- ASP.NET Core Web API
- CsvHelper (for CSV parsing)
- Swashbuckle (Swagger/OpenAPI documentation)

### Frontend
- React 18.2
- Vite 5.0
- Axios 1.6 (HTTP client)
- Recharts 2.10 (charting library)

## Data Models

### Ticket Types
- **Incident**: Issues that need fixing
- **Service Request**: User requests for services

### Ticket Status Codes
- **2**: Open
- **3**: Pending
- **4**: Resolved
- **5**: Closed

### Access Control
- Users in `acl.csv` can have access via:
  - **Perimeter**: Access to all departments under a perimeter
  - **Department**: Access to a specific department

## License

Internal use only.
