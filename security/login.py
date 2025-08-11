from fastapi import HTTPException, Depends, Cookie
from typing import Optional
from sqlmodel import Session, select
from datetime import datetime
from database.models import User, UserSession
from database.db_connection import get_session


class CurrentUserSession:
    def __init__(self):
        pass

    def current_session(self, session_token: Optional[str] = Cookie(None),
                        session: Session = Depends(get_session)):
        """
        Dependency to get the current user session based on the session token.
        If the session token is not provided or invalid, 
        it raises an HTTPException.
        """
        cu = self.__get_current_user_session(session_token, session)
        if not cu:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return cu

    # Dependency to validate session
    def __get_current_user_session(self, session_token, session: Session):
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        user_session = session.exec(select(UserSession).where(
            UserSession.token == session_token)).first()

        if not user_session:
            raise HTTPException(status_code=401, detail="Invalid session")

        if datetime.utcnow() > user_session.expires_at:
            # Delete expired session
            session.delete(user_session)
            session.commit()
            raise HTTPException(status_code=401, detail="Session expired")

        user = session.get(User, user_session.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
