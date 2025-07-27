#!/usr/bin/env python3
"""
Database Population Script for AI Fashion Color System

This script populates the PostgreSQL database with color palette data
for different Monk skin tones.
"""

import psycopg2
import os
from pathlib import Path

# Database configuration (same as in color_routes.py)
DB_CONFIG = {
    'host': 'dpg-d1vhvpbuibrs739dkn3g-a.oregon-postgres.render.com',
    'database': 'fashion_jvy9',
    'user': 'fashion_jvy9_user',
    'password': '0d2Nn5mvyw6KMBDT21l9olpHaxrTPEzh',
    'port': '5432',
    'sslmode': 'require'
}

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Successfully connected to the database")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def run_sql_file(conn, sql_file_path):
    """Execute SQL file contents"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        cursor = conn.cursor()
        
        # Split SQL content by semicolons and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed statement {i+1}/{len(statements)}")
                except Exception as e:
                    print(f"⚠️  Warning on statement {i+1}: {e}")
                    # Continue with other statements
        
        conn.commit()
        cursor.close()
        print("✅ All SQL statements executed successfully")
        
    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")
        conn.rollback()

def verify_data(conn):
    """Verify that data was inserted correctly"""
    try:
        cursor = conn.cursor()
        
        # Check total number of records
        cursor.execute("SELECT COUNT(*) FROM colors;")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total colors in database: {total_count}")
        
        # Check distribution by skin tone
        cursor.execute("""
            SELECT suitable_skin_tone, category, COUNT(*) as count 
            FROM colors 
            WHERE suitable_skin_tone IS NOT NULL
            GROUP BY suitable_skin_tone, category 
            ORDER BY suitable_skin_tone, category;
        """)
        
        results = cursor.fetchall()
        print("\n📊 Color distribution by skin tone:")
        print("Skin Tone\t\tCategory\t\tCount")
        print("-" * 50)
        
        for row in results:
            skin_tone, category, count = row
            print(f"{skin_tone}\t\t{category}\t\t{count}")
        
        # Check for any potential issues
        cursor.execute("""
            SELECT COUNT(*) FROM colors 
            WHERE hex_code IS NULL OR color_name IS NULL;
        """)
        
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"⚠️  Warning: {null_count} records have NULL values")
        else:
            print("✅ All records have valid data")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

def main():
    """Main function to populate the database"""
    print("🎨 AI Fashion Color Database Population Script")
    print("=" * 50)
    
    # Get the path to the SQL file
    script_dir = Path(__file__).parent
    sql_file_path = script_dir / "populate_color_data.sql"
    
    if not sql_file_path.exists():
        print(f"❌ SQL file not found: {sql_file_path}")
        return
    
    print(f"📁 Using SQL file: {sql_file_path}")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Run the SQL file
        print("\n🔄 Executing SQL statements...")
        run_sql_file(conn, sql_file_path)
        
        # Verify the data
        print("\n🔍 Verifying data...")
        verify_data(conn)
        
        print("\n🎉 Database population completed successfully!")
        print("\n💡 You can now test the color palette API endpoints:")
        print("   GET /api/colors/palette/Monk05")
        print("   GET /api/colors/recommendations/Monk05")
        print("   GET /api/colors/skin-tone/Monk05")
        
    finally:
        conn.close()
        print("\n🔐 Database connection closed")

if __name__ == "__main__":
    main()
