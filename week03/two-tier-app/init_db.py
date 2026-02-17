#!/usr/bin/env python3
"""
Database Initialization Script
Run this to create the students table in your database
"""

import os
import sys

# Load environment variables from .env if present
if os.path.exists('.env'):
    print("Loading .env file...")
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

# Import after setting environment variables
from app import app, db, Student

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✓ Tables created successfully!")
            
            # Verify table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\nExisting tables in database:")
            for table in tables:
                print(f"  - {table}")
            
            if 'students' in tables:
                print("\n✓ 'students' table is ready!")
                
                # Show table structure
                columns = inspector.get_columns('students')
                print("\nTable structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("\n✗ Warning: 'students' table not found!")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        print("\nTroubleshooting:")
        print("  1. Check database connection settings")
        print("  2. Ensure database exists")
        print("  3. Verify credentials are correct")
        print("  4. Run: ./test_connection.sh")
        return False

def test_connection():
    """Test database connection"""
    try:
        with app.app_context():
            # Try to connect
            db.engine.connect()
            print("✓ Database connection successful!")
            
            # Get database info
            result = db.session.execute(db.text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"\nPostgreSQL version:")
            print(f"  {version.split(',')[0]}")
            
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print()
    
    # Show configuration
    print("Configuration:")
    print(f"  Host: {os.environ.get('DB_HOST', 'localhost')}")
    print(f"  Port: {os.environ.get('DB_PORT', '5432')}")
    print(f"  Database: {os.environ.get('DB_NAME', 'students_db')}")
    print(f"  User: {os.environ.get('DB_USER', 'postgres')}")
    print(f"  SSL Mode: {os.environ.get('DB_SSL_MODE', 'prefer')}")
    print()
    
    # Test connection first
    print("Step 1: Testing database connection...")
    print("-" * 60)
    if not test_connection():
        print("\n✗ Cannot connect to database. Fix connection issues first.")
        sys.exit(1)
    
    print()
    
    # Create tables
    print("Step 2: Creating tables...")
    print("-" * 60)
    if create_tables():
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        print("\nYou can now run your Flask application:")
        print("  ./run.sh")
        sys.exit(0)
    else:
        print("\n✗ Database initialization failed.")
        sys.exit(1)