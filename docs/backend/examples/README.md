# Examples
Examples are precomputed and stored in the [examples directory](../../../src/backend/app/examples/). They are copied on startup in [main.py](../../../src/backend/app/main.py) to a directory specified in [.env](../../../src/backend/app/.env) file. These files are then accessed in `/examples/*` API endpoints in [charges.py](../../../src/backend/app/api/v1/routes/charges.py).


## Adding a new example
If you want to add a new example, all you need to do is: 
1. Download the calculation results.
2. Add a new directory to [`examples/`](../../../src/backend/app/examples/). The name of the directory is then used as an identifier.