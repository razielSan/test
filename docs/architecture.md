

```mermaid
graph TD 
Browser --> FastAPI
FastAPI --> Middleware
FastAPI --> Dependency
FastAPI --> Router
Router --> Application --> UoW --> Sqlite
Dependency --> RateLimitService --> Redis
```

