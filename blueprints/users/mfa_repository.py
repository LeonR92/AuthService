from sqlalchemy.orm import Session

from blueprints.users.models import MFA, User

class MFARepository():
    def __init__(self,write_db_session:Session, read_db_session:Session) -> None:
        self.write_db_session = write_db_session
        self.read_db_session = read_db_session

    
    def get_mfa_details_by_user_id(self, user_id:int) -> MFA|None:
        return self.read_db_session.query(MFA).join(User,User.mfa_id == MFA.id).filter(User.id == user_id).first()
    
    def get_mfa_details(self, mfa_id:int) -> MFA|None:
        return self.read_db_session.query(MFA).filter(MFA.id == mfa_id).first()
    
    def create(self,otp_secret:str) -> int:
        mfa = MFA(otp_secret = otp_secret)
        self.write_db_session.add(mfa)
        self.write_db_session.commit()
        self.write_db_session.flush()
        return mfa.id
    
    def delete(self,mfa_id:int)->None:
        mfa = self.get_mfa_details(mfa_id)
        if mfa:
            self.write_db_session.delete(mfa)
            self.write_db_session.commit()
    
    def update(self,mfa_id:int,**kwargs)->None|int:
        mfa = self.get_mfa_details(mfa_id)
        if not mfa:
            return None
        for key,value in kwargs.items():
            setattr(mfa,key,value)
        self.write_db_session.commit()
        self.write_db_session.refresh(mfa)
        return mfa
