# Api (v1)
The api module contains FastAPI routes (request handlers), middleware and Pydantic response/request schemas.

## Dependency Injection Container
In order to use a new service, it should be registered in [container.py](../../../src/backend/app/api/v1/container.py). 

### Example usage
You can register a service in a following way:
```python
example_service = providers.Singleton(ExampleService, logger=logger_service, io_service=io_service)
```
The init method of the given service then looks like this:

```python
def __init__(self, logger: LoggerBase, io_service: IOService) -> None:
    self.logger = logger_service
    self.io_service = io_service
```

Usage in a handler:

```python
@app.get("/")
async def handler(service: ExampleService = Depends(Provide[Container.example_service])) -> Response[None]:
    service.some_method()
    ...
```