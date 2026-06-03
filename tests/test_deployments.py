"""
Unit tests for the deployments API.
Each test gets an isolated SQLite database via the `client` fixture in conftest.py.

Success responses follow the envelope shape:
  list  → {"status": "success", "data": [...], "count": N}
  single → {"status": "success", "data": {...}}
Error responses always carry {"status": "error", "code": ..., "message": ..., ...}.
"""

from httpx import AsyncClient

VALID = {"service": "payment-service", "region": "us-east-1", "version": "2.0.0"}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


class TestListDeployments:
    async def test_empty_list(self, client: AsyncClient):
        r = await client.get("/api/v1/deployments/")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        assert body["data"] == []
        assert body["count"] == 0

    async def test_returns_created_deployment(self, client: AsyncClient):
        await client.post("/api/v1/deployments/", json=VALID)
        r = await client.get("/api/v1/deployments/")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        assert body["count"] == 1
        assert len(body["data"]) == 1

    async def test_filter_by_region(self, client: AsyncClient):
        await client.post("/api/v1/deployments/", json={**VALID, "region": "us-east-1"})
        await client.post("/api/v1/deployments/", json={**VALID, "region": "eu-west-1"})
        r = await client.get("/api/v1/deployments/?region=us-east-1")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] == 1
        assert all(d["region"] == "us-east-1" for d in body["data"])

    async def test_filter_by_service(self, client: AsyncClient):
        await client.post("/api/v1/deployments/", json={**VALID, "service": "api"})
        await client.post("/api/v1/deployments/", json={**VALID, "service": "worker"})
        r = await client.get("/api/v1/deployments/?service=api")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] == 1
        assert all(d["service"] == "api" for d in body["data"])

    async def test_filter_by_status(self, client: AsyncClient):
        await client.post("/api/v1/deployments/", json={**VALID, "status": "success"})
        await client.post("/api/v1/deployments/", json={**VALID, "status": "failed"})
        r = await client.get("/api/v1/deployments/?status=success")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] == 1
        assert all(d["status"] == "success" for d in body["data"])


# ---------------------------------------------------------------------------
# Create — happy paths
# ---------------------------------------------------------------------------


class TestCreateDeploymentValid:
    async def test_minimal_fields(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json=VALID)
        assert r.status_code == 201
        body = r.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["service"] == VALID["service"]
        assert data["region"] == VALID["region"]
        assert data["version"] == VALID["version"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "deployed_at" in data

    async def test_region_normalised_to_lowercase(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "region": "US-EAST-1"})
        assert r.status_code == 201
        assert r.json()["data"]["region"] == "us-east-1"

    async def test_explicit_status(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "status": "success"})
        assert r.status_code == 201
        assert r.json()["data"]["status"] == "success"

    async def test_with_metadata(self, client: AsyncClient):
        meta = {"commit": "abc123", "triggered_by": "ci"}
        r = await client.post("/api/v1/deployments/", json={**VALID, "metadata": meta})
        assert r.status_code == 201
        assert r.json()["data"]["metadata"] == meta


# ---------------------------------------------------------------------------
# Create — Pydantic validation errors (422 VALIDATION_ERROR)
# ---------------------------------------------------------------------------


class TestCreateDeploymentPydanticValidation:
    async def test_missing_service(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={"region": "us-east-1", "version": "1.0.0"})
        assert r.status_code == 422
        body = r.json()
        assert body["status"] == "error"
        assert body["code"] == "VALIDATION_ERROR"
        assert body["details"] is not None

    async def test_missing_region(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={"service": "api", "version": "1.0.0"})
        assert r.status_code == 422
        assert r.json()["code"] == "VALIDATION_ERROR"

    async def test_missing_version(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={"service": "api", "region": "us-east-1"})
        assert r.status_code == 422
        assert r.json()["code"] == "VALIDATION_ERROR"

    async def test_empty_body(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={})
        assert r.status_code == 422
        body = r.json()
        assert body["code"] == "VALIDATION_ERROR"
        missing = [e["loc"][-1] for e in body["details"]]
        assert "service" in missing
        assert "region" in missing
        assert "version" in missing

    async def test_invalid_status_enum(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "status": "deploying"})
        assert r.status_code == 422
        assert r.json()["code"] == "VALIDATION_ERROR"

    async def test_empty_string_service(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "service": ""})
        assert r.status_code == 422
        assert r.json()["code"] == "VALIDATION_ERROR"

    async def test_empty_string_version(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "version": ""})
        assert r.status_code == 422
        assert r.json()["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# Create — business-level validation (422 INVALID_DEPLOYMENT_DATA)
# ---------------------------------------------------------------------------


class TestCreateDeploymentInvalidData:
    async def test_service_name_with_spaces(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "service": "My Service"})
        assert r.status_code == 422
        body = r.json()
        assert body["status"] == "error"
        assert body["code"] == "INVALID_DEPLOYMENT_DATA"
        assert "service name" in body["message"]

    async def test_service_name_with_special_chars(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "service": "api@v2!"})
        assert r.status_code == 422
        assert r.json()["code"] == "INVALID_DEPLOYMENT_DATA"

    async def test_service_name_uppercase(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "service": "MyService"})
        assert r.status_code == 422
        assert r.json()["code"] == "INVALID_DEPLOYMENT_DATA"

    async def test_service_name_starting_with_hyphen(self, client: AsyncClient):
        r = await client.post("/api/v1/deployments/", json={**VALID, "service": "-bad-name"})
        assert r.status_code == 422
        assert r.json()["code"] == "INVALID_DEPLOYMENT_DATA"


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


class TestGetDeployment:
    async def test_get_existing(self, client: AsyncClient):
        created = (await client.post("/api/v1/deployments/", json=VALID)).json()["data"]
        r = await client.get(f"/api/v1/deployments/{created['id']}")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        assert body["data"]["id"] == created["id"]

    async def test_get_not_found_returns_custom_exception(self, client: AsyncClient):
        r = await client.get("/api/v1/deployments/99999")
        assert r.status_code == 404
        body = r.json()
        assert body["status"] == "error"
        assert body["code"] == "DEPLOYMENT_NOT_FOUND"
        assert body["message"] == "The requested deployment does not exist."
        assert "timestamp" in body
        assert body["details"] is None

    async def test_get_invalid_id_type(self, client: AsyncClient):
        r = await client.get("/api/v1/deployments/not-an-id")
        assert r.status_code == 422
        assert r.json()["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestDeleteDeployment:
    async def test_delete_existing(self, client: AsyncClient):
        created = (await client.post("/api/v1/deployments/", json=VALID)).json()["data"]
        r = await client.delete(f"/api/v1/deployments/{created['id']}")
        assert r.status_code == 204

    async def test_deleted_record_no_longer_found(self, client: AsyncClient):
        created = (await client.post("/api/v1/deployments/", json=VALID)).json()["data"]
        await client.delete(f"/api/v1/deployments/{created['id']}")
        r = await client.get(f"/api/v1/deployments/{created['id']}")
        assert r.status_code == 404
        assert r.json()["code"] == "DEPLOYMENT_NOT_FOUND"

    async def test_delete_not_found(self, client: AsyncClient):
        r = await client.delete("/api/v1/deployments/99999")
        assert r.status_code == 404
        assert r.json()["code"] == "DEPLOYMENT_NOT_FOUND"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class TestHealth:
    async def test_health_returns_ok(self, client: AsyncClient):
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
