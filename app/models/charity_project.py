from sqlalchemy import Column, String, Text

from app.models.basemodel import AbstractModel


class CharityProject(AbstractModel):
    __tablename__ = 'charityproject'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return (
            f'{super().__repr__()},'
            f'name={self.name},'
            f'description={self.description}'
        )
