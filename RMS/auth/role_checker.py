from fastapi import HTTPException, status


def check_role(current_user: dict, allowed_roles: list):
    user_role = current_user.get("role")
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied! Sirf {allowed_roles} wale ye kar sakte hain"
        )
    return True