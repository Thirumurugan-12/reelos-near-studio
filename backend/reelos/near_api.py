"""NEAR discovery/read endpoints; signing stays in the wallet."""

from fastapi.responses import JSONResponse

from reelos.near import NearReader, NearUnavailable
from reelos.timeline import Identifier


def mount_near(app, settings):
    app.state.near_reader = (
        NearReader(settings.near_contract_id) if settings.near_contract_id else None
    )

    @app.exception_handler(NearUnavailable)
    async def unavailable(request, exc):
        return JSONResponse({"error": {"code": "NEAR_UNAVAILABLE", "message": str(exc)}}, 502)

    @app.get("/api/near/config")
    def config():
        if app.state.near_reader is None:
            return {"enabled": False, "network": "testnet", "contract_id": None}
        return app.state.near_reader.get_config()

    @app.get("/api/near/jobs/{job_id}")
    def job(job_id: Identifier):
        if app.state.near_reader is None:
            return JSONResponse(
                {
                    "error": {
                        "code": "NEAR_NOT_CONFIGURED",
                        "message": "NEAR testnet contract is not configured yet.",
                    }
                },
                503,
            )
        result = app.state.near_reader.get_job(job_id)
        if result["job"] is None:
            raise KeyError("Job not found")
        return result
