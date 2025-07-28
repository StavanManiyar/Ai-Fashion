"""
Database optimization utilities for improved performance.
"""
import asyncpg
from typing import List
from shared.domain.entities.product import Product


class DatabaseOptimizer:
    """Provides database optimization utilities."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.pool = db_pool
    
    async def batch_insert_products(self, products: List[Product]) -> None:
        """Use batch inserts for better performance when adding multiple products."""
        async with self.pool.acquire() as conn:
            # Prepare the data for batch insert
            product_data = [
                (
                    p.id, p.name, p.brand, p.category, p.sub_category,
                    p.price, p.currency, p.image_url, p.description,
                    p.availability, p.rating, p.review_count
                )
                for p in products
            ]
            
            await conn.executemany(
                """
                INSERT INTO products 
                (id, name, brand, category, sub_category, price, currency, 
                 image_url, description, availability, rating, review_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    brand = EXCLUDED.brand,
                    category = EXCLUDED.category,
                    sub_category = EXCLUDED.sub_category,
                    price = EXCLUDED.price,
                    currency = EXCLUDED.currency,
                    image_url = EXCLUDED.image_url,
                    description = EXCLUDED.description,
                    availability = EXCLUDED.availability,
                    rating = EXCLUDED.rating,
                    review_count = EXCLUDED.review_count
                """,
                product_data
            )
    
    async def create_indexes(self) -> None:
        """Create database indexes for frequently queried fields."""
        async with self.pool.acquire() as conn:
            # Product indexes
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products (category)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_brand ON products (brand)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_price ON products (price)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_products_rating ON products (rating)"
            )
            
            # Skin tone analysis indexes
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_skin_tone_monk_tone ON skin_tone_analyses (monk_tone)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_skin_tone_date ON skin_tone_analyses (analysis_date)"
            )
            
            # Color recommendations indexes
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_color_recs_season ON color_recommendations (season)"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_color_recs_compatibility ON color_recommendations (skin_tone_compatibility)"
            )
    
    async def get_database_stats(self) -> dict:
        """Get database performance statistics."""
        async with self.pool.acquire() as conn:
            # Table sizes
            table_sizes = await conn.fetch("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            # Index usage
            index_usage = await conn.fetch("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY n_distinct DESC
            """)
            
            return {
                'table_sizes': [dict(row) for row in table_sizes],
                'index_usage': [dict(row) for row in index_usage]
            }
    
    async def vacuum_analyze(self) -> None:
        """Run VACUUM ANALYZE for database maintenance."""
        async with self.pool.acquire() as conn:
            await conn.execute("VACUUM ANALYZE")
    
    async def get_slow_queries(self) -> List[dict]:
        """Get slow query statistics if pg_stat_statements is enabled."""
        async with self.pool.acquire() as conn:
            try:
                slow_queries = await conn.fetch("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements 
                    ORDER BY mean_time DESC 
                    LIMIT 10
                """)
                return [dict(row) for row in slow_queries]
            except:
                # pg_stat_statements extension not available
                return []
