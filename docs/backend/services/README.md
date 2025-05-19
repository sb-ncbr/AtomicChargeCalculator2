# Services
Services module contains logic which should be used in API endpoints (and other services). They are registered in [container.py](../../../src/backend/app/api/v1/container.py).

## calculation_storage
This service provides the functionality to store/retrieve calculation results and statistics about uploaded structures to/from the database.

## chargefw2
Functionality related to ChargeFW2, using [chargefw2 integration](../../../src/backend/app/integrations/chargefw2/base.py).

The number of simultaneous calculations is limited using `asyncio.Semaphore`. This service is injected in [API container](../../../src/backend//app/api/v1/container.py) as a singleton, meaning that the semaphore is the same instance for all users (it restricts the number of simultaneous calculations globally).

## file_storage
Similar to the `calculation_storage` but for files. It currently only provides the functionality to list (filter, sort) files of a user.

## io
Provides additional functionality on top of the [io integration](../../../src/backend/app/integrations/io/base.py).

## mmcif
Used to handle mmCIF file opertations, such as writing charges so that the mmCIF file can be used with Mol* Viewer.

## oidc
This service implements the OpenID Connect logic, which is used with *Life Science Login* integration. It fetches and caches information from the .well_known/openid-configuration URL (`OIDC_DISCOVERY_URL` ENV variable in [.env](../../../src/backend/app/.env)).
