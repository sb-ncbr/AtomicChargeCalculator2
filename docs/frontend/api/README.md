# Api
This module contains endpoints used to communicate with ACC II API. 

These endpoints are divided in directories based on "domains" and each domain contains the endpoints and types.

*Axios* is instantiated in [base.ts](../../../src/frontend/acc2/src/api/base.ts). API URL is determined by the `VITE_BASE_API_URL` environment variable, located in [.env.development](../../../src/frontend/acc2/.env.development) (build ARG when using [Dockerfile](../../../src/frontend/Dockerfile)).