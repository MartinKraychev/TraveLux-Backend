from sqlalchemy.orm import Session

import models


def create_token(db: Session, user_id, access_token, status):
    """
    Creates access token
    """
    token_db = models.Token(user_id=user_id, access_token=access_token, status=status)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)


def delete_expired_tokens(db: Session, tokens):
    """
    Delete expired tokens
    """
    db.query(models.Token).where(models.Token.user_id.in_(tokens)).delete()
    db.commit()


def set_inactive_token(db: Session, token):
    """
    Sets token to be inactive
    """
    existing_token = db.query(models.Token).filter(models.Token.access_token == token).first()

    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)