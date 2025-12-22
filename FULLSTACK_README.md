# Service Desk Dashboard - Full Stack Application

A modern web application for monitoring and analyzing FreshService incidents with user-based access control.

## Architecture

- **Backend**: .NET 8.0 Web API
- **Frontend**: React 18 with Vite
- **Data**: CSV-based ACL (Access Control Lists)
- **Charts**: Recharts library

## Project Structure

```
fresh-desk-api/
├── ServiceDeskDashboard.API/       # .NET Backend
│   ├── Controllers/                # API endpoints
│   ├── Models/                     # Data models and DTOs
│   ├── Services/                   # Business logic
│   └── appsettings.json           # Configuration
├── service-desk-dashboard/         # React Frontend
│   ├── src/
│   │   ├── components/            # UI components
│   │   ├── services/              # API client
│   │   └── App.jsx                # Main app
│   └── package.json
└── data/                          # CSV data files
    ├── departments.csv
    ├── perimeters.csv
    └── acl.csv
```

## Features

### Backend API

- **GET /api/users** - Retrieve all users from ACL
- **GET /api/incidents/counts** - Get incident metrics with ACL filtering
  - Query parameters:
    - `username` (optional): Filter by user
    - `days` (default: 30): Time range in days

### Frontend Dashboard

- User selection dropdown (populated from ACL)
- Time range selector (7, 14, 30, 60, 90 days)
- Metric cards:
  - Total tickets
  - Open incidents
  - Pending incidents
  - Resolved incidents
  - Closed incidents
  - Open + Pending (highlighted if > 0)
- Charts:
  - Resolution rate pie chart
  - Status breakdown bar chart
- Department access list

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

Edit `ServiceDeskDashboard.API/appsettings.json`:

```json
{
  "FreshService": {
    "BaseUrl": "https://axiansnetworkltd.freshservice.com",
    "ApiKey": "YOUR_API_KEY_HERE"
  },
  "CsvFiles": {
    "DepartmentsPath": "../data/departments.csv",
    "PerimetersPath": "../data/perimeters.csv",
    "AclPath": "../data/acl.csv"
  }
}
```

### 2. Install Backend Dependencies

```bash
cd ServiceDeskDashboard.API
dotnet restore
```

### 3. Install Frontend Dependencies

```bash
cd service-desk-dashboard
npm install
```

## Running the Application

### Start Backend API

```bash
cd ServiceDeskDashboard.API
dotnet run
```

The API will be available at:
- HTTP: http://localhost:5000
- HTTPS: https://localhost:5001
- Swagger UI: http://localhost:5000/swagger

### Start Frontend

```bash
cd service-desk-dashboard
npm run dev
```

The frontend will be available at: http://localhost:5173

## Usage

1. Open http://localhost:5173 in your browser
2. Select a user from the dropdown
3. Choose a time range
4. View incident metrics and charts

## API Endpoints

### Get Users

```
GET /api/users
```

Response:
```json
[
  {
    "username": "john.doe",
    "accessLevel": "Perimeter"
  }
]
```

### Get Incident Counts

```
GET /api/incidents/counts?username=john.doe&days=30
```

Response:
```json
{
  "totalOpen": 5,
  "totalPending": 3,
  "totalResolved": 15,
  "totalClosed": 10,
  "totalOpenAndPending": 8,
  "resolutionRate": 75.8,
  "accessibleDepartments": [
    {
      "id": 123,
      "name": "IT Support"
    }
  ]
}
```

## Development

### Backend Development

```bash
cd ServiceDeskDashboard.API
dotnet watch run
```

### Frontend Development

```bash
cd service-desk-dashboard
npm run dev
```

Hot reload is enabled for both backend and frontend.

## Building for Production

### Backend

```bash
cd ServiceDeskDashboard.API
dotnet publish -c Release -o ./publish
```

### Frontend

```bash
cd service-desk-dashboard
npm run build
```

The production build will be in the `dist/` folder.

## Environment Variables

### Frontend

Create `.env` in `service-desk-dashboard/`:

```
VITE_API_URL=http://localhost:5000
```

## Troubleshooting

### CORS Issues

The backend is configured to allow requests from:
- http://localhost:3000
- http://localhost:5173

If using a different port, update the CORS policy in `Program.cs`.

### CSV File Path Issues

Ensure the CSV file paths in `appsettings.json` are correct relative to the API project directory.

### API Connection Failed

1. Verify the backend is running on port 5000
2. Check the API URL in frontend (default: http://localhost:5000)
3. Check browser console for CORS errors

## Technologies

### Backend
- .NET 8.0
- ASP.NET Core Web API
- CsvHelper 30.0.1
- Swashbuckle (Swagger)

### Frontend
- React 18.2
- Vite 5.0
- Axios 1.6
- Recharts 2.10

## License

Internal use only.
