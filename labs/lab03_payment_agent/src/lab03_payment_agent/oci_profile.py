"""Local assignment consistency for OCI profiles; OCI validates token signatures."""

import base64
import json
import time
from pathlib import Path


def profile_user(config: dict) -> str:
    """Read a session subject without logging token contents or identifiers.

    OCI CLI session profiles may omit user. This is an assignment guard only;
    the signed OCI API request remains the authentication/authorization boundary.
    """
    if config.get("security_token_file"):
        token = Path(config["security_token_file"]).read_text().strip()
        encoded = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if float(claims.get("exp", 0)) <= time.time():
            raise ValueError("OCI session has expired")
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise ValueError("OCI session subject missing")
        return subject
    if not config.get("user"):
        raise ValueError("OCI profile user missing")
    return config["user"]
