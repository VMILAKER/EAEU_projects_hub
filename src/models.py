import uuid
from enum import Enum

# from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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


class Middle(Base):
    __tablename__ = 'project_participant_wire'

    id = Column(Integer, index=True, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    participant_id = Column(UUID(as_uuid=True), ForeignKey('participants.id'))

    # country_id = Column(UUID(as_uuid=True), ForeignKey('countries.id'))
    country = relationship(
        'Country', lazy='raise_on_sql')


class Project_model(Base):
    __tablename__ = 'projects'

    id = get_id()
    name = Column(String, index=True)

    # qualification_id = Column(
    #     UUID(as_uuid=True), ForeignKey('vkr_qualifications.id'))
    scope = relationship(
        'Scope', lazy='raise_on_sql')

    # stage_id = Column(UUID(as_uuid=True), ForeignKey(
    #         'stages.id'))
    stage = relationship(
        'Stage', lazy='raise_on_sql')

    participants = relationship('Participant', secondary='project_participant_wire',
                                back_populates='project_relation', lazy='raise_on_sql')

    # link_id = Column(UUID(as_uuid=True), ForeignKey(
    #         'links.id'))
    links = relationship(
        'Link', lazy='raise_on_sql')

    description = Column(String)
    comments = Column(String)

    # key_facts_id = Column(UUID(as_uuid=True), ForeignKey(
    #         'key_facts.id'))
    key_facts = relationship(
        'Key_fact', lazy='raise_on_sql')


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


class Country(Base):
    __tablename__ = 'countries'

    id = get_id()
    name = Column(String)


class Link(Base):
    __tablename__ = 'links'

    id = get_id()
    name = Column(String)


class Key_facts(Base):
    __tablename__ = 'key_facts'

    id = get_id()
    name = Column(String)
    # chunks_id = Column(UUID(as_uuid=True), ForeignKey(
    #         'chunks.id'))
    chunk = relationship(
        'Chunk', lazy='raise_on_sql')


class Chunk(Base):
    __tablename__ = 'chunks'

    id = get_id()
    content = Column(String, index=True)
    # embedding = Column(VECTOR(384))

    key_facts_id = Column(UUID(as_uuid=True), ForeignKey('key_facts.id'))
