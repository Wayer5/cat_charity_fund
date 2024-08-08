from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.basemodel import AbstractModel


class Donation(AbstractModel):
    __tablename__ = 'donation'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    comment = Column(Text, nullable=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return (
            f'{super().__repr__()},'
            f'user_id={self.user_id},'
            f'comment={self.comment}'
        )
