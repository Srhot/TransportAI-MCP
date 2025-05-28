# TransportAI MCP Server

This is the backend server for the TransportAI project, implementing the Model Context Protocol (MCP) and integrating with the AviationStack API.

## Project Structure

```
TransportAI/
├── server/             # FastAPI backend
│   └── main.py        # Main server file
├── Dockerfile         # Docker configuration
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## Setup Instructions

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your AviationStack API key:
```
AVIATIONSTACK_API_KEY=your_api_key_here
```

4. Start the server:
```bash
cd server
uvicorn main:app --reload
```

### Smithery AI Deployment

1. Ensure you have Docker installed on your system

2. Build the Docker image:
```bash
docker build -t transportai-mcp .
```

3. Test the Docker image locally:
```bash
docker run -p 8000:8000 -e AVIATIONSTACK_API_KEY=your_api_key_here transportai-mcp
```

4. Deploy to Smithery AI:
   - Create a new project in Smithery AI
   - Upload the Dockerfile and related files
   - Set the environment variable `AVIATIONSTACK_API_KEY`
   - Deploy the application

## API Endpoints

### MCP Protocol Endpoints

- `GET /`: Server status and version information
- `GET /mcp/health`: Health check endpoint
- `POST /mcp/query`: Main MCP query endpoint
  - Request body:
    ```json
    {
      "context": {
        "session_id": "optional_session_id"
      },
      "query": "Get information for flight TK123",
      "parameters": {
        "flight_iata": "TK123"
      }
    }
    ```

## Testing the MCP Server

You can test the MCP server using curl:

```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "context": {"session_id": "test_session"},
    "query": "Get information for flight TK123",
    "parameters": {"flight_iata": "TK123"}
  }'
```

## License

MIT 