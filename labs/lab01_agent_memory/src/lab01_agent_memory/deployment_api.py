"""Local rehearsal gateway for team-scoped Lab 1 memory bundle deployment.

The module has no OCI credentials and does not call Autonomous Database.  It
models the boundary that the future OCI deployment must preserve: authenticate
the caller, derive its team scope on the server, validate its bundle, then
retrieve only within that scope.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from .gateway_auth import TeamIdentity, TokenValidationError, verify_local_team_token
from .models import Guideline, MemoryScope
from .store import ScopedMemoryStore

AGENT_ID = "khipu-workshop-agent"
THREAD_ID = "lab01-secure-deployment"


class ProcedurePayload(BaseModel):
    """One synthetic procedure submitted by a workshop team."""

    id: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=1000)
    tags: list[str] = Field(min_length=1, max_length=12)


class DeployBundleRequest(BaseModel):
    """The deployable memory bundle, including the claimed team identifier."""

    team_id: str = Field(min_length=1, max_length=32)
    display_name: str = Field(min_length=1, max_length=100)
    procedures: list[ProcedurePayload] = Field(min_length=1, max_length=12)


class QueryRequest(BaseModel):
    """A query for the caller's derived scope; it intentionally has no team_id."""

    query: str = Field(min_length=1, max_length=500)


@dataclass
class LocalMemoryRepository:
    """Small in-memory repository for the secure deployment rehearsal."""

    bundles: dict[str, tuple[Guideline, ...]] = field(default_factory=dict)

    def deploy(self, identity: TeamIdentity, request: DeployBundleRequest) -> int:
        """Replace only the authenticated team's synthetic procedure bundle."""

        if request.team_id != identity.team_id:
            raise PermissionError("The bundle team_id does not match the authenticated team")
        procedures = tuple(
            Guideline(
                identifier=procedure.id.strip(),
                content=procedure.content.strip(),
                tags=tuple(tag.strip() for tag in procedure.tags),
            )
            for procedure in request.procedures
        )
        if any(not procedure.identifier or not procedure.content for procedure in procedures):
            raise ValueError("Procedure identifiers and content must not be blank")
        if any(not tag for procedure in procedures for tag in procedure.tags):
            raise ValueError("Procedure tags must not be blank")
        self.bundles[identity.team_id] = procedures
        return len(procedures)

    def search(self, identity: TeamIdentity, query: str) -> list[Guideline]:
        """Search only the scope derived from the authenticated identity."""

        store = ScopedMemoryStore()
        scope = MemoryScope(
            team_id=identity.team_id,
            agent_id=AGENT_ID,
            thread_id=THREAD_ID,
        )
        for procedure in self.bundles.get(identity.team_id, ()):
            store.add_guideline(scope, procedure)
        return store.search(scope, query)


def create_app(token_secret: str, repository: LocalMemoryRepository | None = None) -> FastAPI:
    """Create an API whose scope is always derived from a verified token."""

    memory_repository = repository or LocalMemoryRepository()
    app = FastAPI(
        title="Lab 1 Secure Deployment Gateway",
        version="0.1.0",
        description="Local rehearsal only. It has no OCI credential or database connection.",
    )

    def require_identity(
        x_workshop_token: str | None = Header(default=None),
    ) -> TeamIdentity:
        if not x_workshop_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="A workshop token is required",
            )
        try:
            return verify_local_team_token(x_workshop_token, token_secret)
        except TokenValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The workshop token is invalid",
            ) from error

    @app.get("/health")
    def health() -> dict[str, object]:
        """Return the intentionally limited posture of this local adapter."""

        return {"status": "ok", "mode": "local-rehearsal", "oci_connection": False}

    @app.post("/v1/bundles/deploy")
    def deploy_bundle(
        request: DeployBundleRequest,
        identity: TeamIdentity = Depends(require_identity),
    ) -> dict[str, object]:
        """Validate a bundle and deploy it to the authenticated team's local scope."""

        try:
            procedure_count = memory_repository.deploy(identity, request)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The bundle is not authorized for this team",
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error
        return {
            "deployment_status": "accepted",
            "authenticated_team_id": identity.team_id,
            "procedure_count": procedure_count,
            "oci_persisted": False,
        }

    @app.post("/v1/memory/query")
    def query_memory(
        request: QueryRequest,
        identity: TeamIdentity = Depends(require_identity),
    ) -> dict[str, object]:
        """Retrieve procedures from only the server-derived team scope."""

        procedures = memory_repository.search(identity, request.query)
        return {
            "authenticated_team_id": identity.team_id,
            "procedure_ids": [procedure.identifier for procedure in procedures],
            "result_count": len(procedures),
            "oci_retrieval": False,
        }

    return app


def main() -> None:
    """Run the local rehearsal gateway on loopback only."""

    token_secret = os.environ.get("LAB01_WORKSHOP_TOKEN_SECRET")
    if not token_secret:
        raise RuntimeError("LAB01_WORKSHOP_TOKEN_SECRET must be set before starting the gateway")
    import uvicorn

    uvicorn.run(create_app(token_secret), host="127.0.0.1", port=8081)


if __name__ == "__main__":
    main()
