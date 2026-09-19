from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.credit import Credit
    from app.models.season import Season
    from app.models.taxonomy import Country, Genre, Industry, Language
    from app.models.watch_provider import TitleWatchProvider


class Title(Base):
    __tablename__ = "titles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    release_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    release_date_precision: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    poster_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    original_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    tmdb_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tmdb_vote_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tmdb_popularity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_anime: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("type IN ('movie', 'tv')", name="check_title_type"),
        UniqueConstraint("tmdb_id", "type", name="uq_titles_tmdb_id_type"),
        Index("ix_titles_rating_vote_count", "tmdb_rating", "tmdb_vote_count"),
        Index("ix_titles_tmdb_popularity", "tmdb_popularity"),
    )

    # Relationships
    languages: Mapped[list["TitleLanguage"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )
    genres: Mapped[list["TitleGenre"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )
    countries: Mapped[list["TitleCountry"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )
    industries: Mapped[list["TitleIndustry"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )
    credits: Mapped[list["Credit"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )
    seasons: Mapped[list["Season"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )
    alternate_titles: Mapped[list["AlternateTitle"]] = relationship(
        back_populates="title_rel",
        cascade="all, delete-orphan",
    )
    external_ids: Mapped[Optional["ExternalId"]] = relationship(
        back_populates="title",
        uselist=False,
        cascade="all, delete-orphan",
    )
    watch_providers: Mapped[list["TitleWatchProvider"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )


class TitleLanguage(Base):
    __tablename__ = "title_languages"

    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="CASCADE"),
        primary_key=True,
    )

    title: Mapped["Title"] = relationship(back_populates="languages")
    language: Mapped["Language"] = relationship(back_populates="titles")


class TitleGenre(Base):
    __tablename__ = "title_genres"

    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )

    title: Mapped["Title"] = relationship(back_populates="genres")
    genre: Mapped["Genre"] = relationship(back_populates="titles")


class TitleCountry(Base):
    __tablename__ = "title_countries"

    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        primary_key=True,
    )

    title: Mapped["Title"] = relationship(back_populates="countries")
    country: Mapped["Country"] = relationship(back_populates="titles")


class TitleIndustry(Base):
    __tablename__ = "title_industries"

    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    industry_id: Mapped[int] = mapped_column(
        ForeignKey("industries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        server_default="1.0",
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    is_manual_override: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="check_industry_confidence_range",
        ),
    )

    title: Mapped["Title"] = relationship(back_populates="industries")
    industry: Mapped["Industry"] = relationship(back_populates="titles")


class AlternateTitle(Base):
    __tablename__ = "alternate_titles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    title_rel: Mapped["Title"] = relationship(
        "Title",
        back_populates="alternate_titles",
    )


class ExternalId(Base):
    __tablename__ = "external_ids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    imdb_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    wikidata_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    title: Mapped["Title"] = relationship(back_populates="external_ids")
