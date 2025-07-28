"""
PostgreSQL implementation of the skin tone repository.
"""
import asyncpg
import json
from typing import Optional
from shared.domain.entities.skin_tone import SkinToneAnalysis


class PostgresSkinToneRepository:
    """PostgreSQL-based implementation of skin tone persistence."""
    
    def __init__(self, connection_pool: asyncpg.Pool):
        self._pool = connection_pool
    
    async def save(self, analysis: SkinToneAnalysis) -> None:
        """Save skin tone analysis to PostgreSQL."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO skin_tone_analyses 
                (id, monk_tone, confidence, hex_color, rgb_values, analysis_date, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                    monk_tone = EXCLUDED.monk_tone,
                    confidence = EXCLUDED.confidence,
                    hex_color = EXCLUDED.hex_color,
                    rgb_values = EXCLUDED.rgb_values,
                    analysis_date = EXCLUDED.analysis_date,
                    metadata = EXCLUDED.metadata
                """,
                analysis.id,
                analysis.monk_tone,
                analysis.confidence,
                analysis.hex_color,
                json.dumps(analysis.rgb_values) if analysis.rgb_values else None,
                analysis.analysis_date,
                json.dumps(analysis.metadata) if analysis.metadata else None
            )
    
    async def find_by_id(self, analysis_id: str) -> Optional[SkinToneAnalysis]:
        """Find skin tone analysis by ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, monk_tone, confidence, hex_color, rgb_values, 
                       analysis_date, metadata
                FROM skin_tone_analyses 
                WHERE id = $1
                """,
                analysis_id
            )
            
            if not row:
                return None
            
            return SkinToneAnalysis(
                id=row['id'],
                monk_tone=row['monk_tone'],
                confidence=row['confidence'],
                hex_color=row['hex_color'],
                rgb_values=json.loads(row['rgb_values']) if row['rgb_values'] else None,
                analysis_date=row['analysis_date'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )
    
    async def find_by_user_id(self, user_id: str) -> list[SkinToneAnalysis]:
        """Find all skin tone analyses for a user."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, monk_tone, confidence, hex_color, rgb_values, 
                       analysis_date, metadata
                FROM skin_tone_analyses 
                WHERE metadata->>'user_id' = $1
                ORDER BY analysis_date DESC
                """,
                user_id
            )
            
            analyses = []
            for row in rows:
                analyses.append(SkinToneAnalysis(
                    id=row['id'],
                    monk_tone=row['monk_tone'],
                    confidence=row['confidence'],
                    hex_color=row['hex_color'],
                    rgb_values=json.loads(row['rgb_values']) if row['rgb_values'] else None,
                    analysis_date=row['analysis_date'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                ))
            
            return analyses
