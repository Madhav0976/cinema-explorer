"""phase_6d_performance_indexes

Revision ID: e1a2b3c4d5e6
Revises: d98bb1cdd79c
Create Date: 2026-09-19 11:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd98bb1cdd79c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create query-justified secondary indexes to accelerate catalog discovery and search."""
    # 1. Lowercase title index for Title A-Z sort, tie-breaking, and exact/prefix search
    op.execute("CREATE INDEX IF NOT EXISTS ix_titles_lower_title ON titles (lower(title));")

    # 2. Descending vote count index for Most Voted catalog sorting
    op.execute("CREATE INDEX IF NOT EXISTS ix_titles_tmdb_vote_count ON titles (tmdb_vote_count DESC NULLS LAST);")

    # 3. Secondary foreign key index on title_genres(genre_id) to eliminate full table scans
    op.create_index(op.f('ix_title_genres_genre_id'), 'title_genres', ['genre_id'], unique=False)

    # 4. Secondary foreign key index on title_industries(industry_id) to accelerate industry and curated regional hub queries
    op.create_index(op.f('ix_title_industries_industry_id'), 'title_industries', ['industry_id'], unique=False)

    # 5. Secondary foreign key index on title_languages(language_id) to accelerate language filters
    op.create_index(op.f('ix_title_languages_language_id'), 'title_languages', ['language_id'], unique=False)

    # 6. Secondary foreign key index on title_countries(country_id) to accelerate country filters
    op.create_index(op.f('ix_title_countries_country_id'), 'title_countries', ['country_id'], unique=False)


def downgrade() -> None:
    """Drop secondary performance indexes."""
    op.drop_index(op.f('ix_title_countries_country_id'), table_name='title_countries')
    op.drop_index(op.f('ix_title_languages_language_id'), table_name='title_languages')
    op.drop_index(op.f('ix_title_industries_industry_id'), table_name='title_industries')
    op.drop_index(op.f('ix_title_genres_genre_id'), table_name='title_genres')
    op.execute("DROP INDEX IF EXISTS ix_titles_tmdb_vote_count;")
    op.execute("DROP INDEX IF EXISTS ix_titles_lower_title;")

