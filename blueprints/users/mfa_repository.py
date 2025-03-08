from typing import Optional
from sqlalchemy.orm import Session

from blueprints.users.models import MFA, Credentials, User

class MFARepository():
    def __init__(self,write_db_session:Session, read_db_session:Session) -> None:
        self.write_db_session = write_db_session
        self.read_db_session = read_db_session

    
    def get_mfa_details_by_user_id(self, user_id:int) -> Optional[MFA]:
        return self.read_db_session.query(MFA).join(User,User.mfa_id == MFA.id).filter(User.id == user_id).first()
    
    def get_user_details_by_mfa_id(self,email:str):
        return self.read_db_session(User).join(Credentials,User.credentials_id == Credentials.id).join(MFA, User.mfa_id == MFA.id).filter(Credentials.email == email).first()
    
    def get_mfa_details(self, mfa_id:int) -> Optional[MFA]:
        return self.read_db_session.query(MFA).filter(MFA.id == mfa_id).first()
    
    def create(self,totp_secret:str) -> int:
        mfa = MFA(totp_secret = totp_secret)
        self.write_db_session.add(mfa)
        self.write_db_session.commit()
        self.write_db_session.flush()
        return mfa.id
    
    def delete(self,mfa_id:int)->None:
        mfa = self.get_mfa_details(mfa_id)
        if mfa:
            self.write_db_session.delete(mfa)
            self.write_db_session.commit()
    
    def update_mfa_secret(self, user_id: int, totp_secret: str) -> Optional[MFA]:
        """Updates the TOTP secret for the user's MFA entry."""
        mfa = self.get_mfa_details_by_user_id(user_id)
        if not mfa:
            return None

        mfa.totp_secret = totp_secret
        self.write_db_session.commit()
        self.write_db_session.refresh(mfa)
        
        return mfa
