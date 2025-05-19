# Content

- [api](./api/)
- [database](./db/)
- [examples](./examples/)
- [integrations](./integrations/)
- [services](./services/)

# Environment variables
- `ACC2_DB_URL` - PostgreSQL database connection string.
- `ACC2_DATA_DIR` - Directory for storing uploaded files and calculation results.
- `ACC2_EXAMPLES_DIR` - Directory for storing precalculated examples.
- `ACC2_LOG_DIR` - Directory for storing logs.
- `ACC2_USER_STORAGE_QUOTA_BYTES`- Maximum allowed storage used by a single authenticated user in bytes.
- `ACC2_GUEST_FILE_STORAGE_QUOTA_BYTES` - Maximum allowed file storage space shared by all guest users.
- `ACC2_GUEST_COMPUTE_STORAGE_QUOTA_BYTES` - Maximum allowed calculation storage space shared by all guest users.
- `ACC2_MAX_FILE_SIZE_BYTES` - Maximum allowed size of a single file user can upload.
- `ACC2_MAX_UPLOAD_SIZE_BYTES` - Maximum allowed sum of sizes of files user can upload in a single request.
- `ACC2_MAX_WORKERS` - Maximum threadpool workers.
- `ACC2_MAX_CONCURRENT_CALCULATIONS` - Maximum allowed simultaneous calculations.
- `OIDC_BASE_URL` - URL where the application is deployed.
- `OIDC_REDIRECT_URL` - Redirect URL after successful Life Science auth.
- `OIDC_DISCOVERY_URL` - URL for fetching OIDC Life Science infomation (auth endpoint, ...).
- `OIDC_CLIENT_ID` - Client ID of the registered Life Science Application.
- `OIDC_CLIENT_SECRET` - Client secret of the registered Life Science Application.