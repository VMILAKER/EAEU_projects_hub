import uuid
from enum import Enum

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


@staticmethod
def get_id():
    return Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)


class CountryTemplates(str, Enum):
    BELARUS = 'Беларусь'
    RUSSIA = 'Россия'
    KAZAKHSTAN = 'Казахстан'
    ARMENIA = 'Армения'
    KYRGYZSTAN = 'Кыргызстан'


class Middle_project_participant(Base):
    __tablename__ = 'project_participant_wire'

    id = Column(Integer, index=True, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    participant_id = Column(UUID(as_uuid=True), ForeignKey('participants.id'))

class Middle_project_link(Base):
    __tablename__ = 'project_link_wire'

    id = Column(Integer, index=True, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    link_id = Column(UUID(as_uuid=True), ForeignKey('links.id'))


class Scope(Base):
    __tablename__ = 'scopes'

    id = get_id()
    name = Column(String)


class Stage(Base):
    __tablename__ = 'stages'

    id = get_id()
    name = Column(String)


class Participant(Base):
    __tablename__ = 'participants'

    id = get_id()
    name = Column(String)
    country_id = Column(
            UUID(as_uuid=True), ForeignKey('countries.id'))
    country_relation = relationship(
        'Country', lazy='raise_on_sql')

    project_participant_relation = relationship('Project', secondary='project_participant_wire',
                                    back_populates='participant_relation', lazy='raise_on_sql')

class Country(Base):
    __tablename__ = 'countries'

    id = get_id()
    name = Column(String)


class Link(Base):
    __tablename__ = 'links'

    id = get_id()
    name = Column(String)

    project_link_relation = relationship(
            'Project', secondary='project_link_wire', back_populates='link_relation' , lazy='raise_on_sql')


class Key_fact(Base):
    __tablename__ = 'key_facts'

    id = get_id()
    text = Column(String)

    embedding = Column(VECTOR(384))
    
    project_id = Column(UUID(as_uuid=True), ForeignKey(
            'projects.id'))


class Project(Base):
    __tablename__ = 'projects'

    id = get_id()
    name = Column(String, index=True)

    scope_id = Column(
        UUID(as_uuid=True), ForeignKey('scopes.id'))
    scope_relation = relationship(
        'Scope', lazy='raise_on_sql')

    stage_id = Column(UUID(as_uuid=True), ForeignKey(
            'stages.id'))
    stage_relation = relationship(
        'Stage', lazy='raise_on_sql')

    participant_relation = relationship('Participant', secondary='project_participant_wire',
                                back_populates='project_participant_relation', lazy='raise_on_sql')

    link_relation = relationship(
        'Link', secondary='project_link_wire', back_populates='project_link_relation' , lazy='raise_on_sql')

    description = Column(String)

    key_facts_relation = relationship(
        'Key_fact', lazy='raise_on_sql')

