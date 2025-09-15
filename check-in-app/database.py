import psycopg2
from psycopg2 import sql
from pydantic import BaseModel
import json
import ssl
import os
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any

class UserCreate(BaseModel):
    email: str
    group_name: Optional[str] = None
    is_validated: bool = False

class GroupCreate(BaseModel):
    name: str
    max_members: int = 3

class DatabaseOperations:

    def __init__(self):
        # IBM Cloud Code Engine PostgreSQL connection
        pqsqlServiceVars = os.environ.get('DATABASES_FOR_POSTGRESQL_CONNECTION')
        if not pqsqlServiceVars:
            raise ValueError("DATABASES_FOR_POSTGRESQL_CONNECTION environment variable not set")
            
        connectionJson = json.loads(pqsqlServiceVars)
        connectionVars = list(connectionJson.values())[1]
        
        # Handle SSL certificate for IBM Cloud PostgreSQL
        encodedCert = connectionVars['certificate']['certificate_base64']
        certName = connectionVars['certificate']['name']
        certFileName = certName + '.crt'
        ca_cert = base64.b64decode(encodedCert)
        decodedCert = ca_cert.decode('utf-8')
        pqsqlCert = '/usr/local/share/ca-certificates/' + certFileName
        
        # Ensure certificate directory exists
        os.makedirs('/usr/local/share/ca-certificates/', exist_ok=True)
        with open(pqsqlCert, 'w+') as output_file:
            output_file.write(decodedCert)
    
        ssl_context = ssl.create_default_context(cafile=pqsqlCert)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.DATABASE_CONFIG = {
            'database': connectionVars.get('database', 'checkin'),
            'user': connectionVars['username'],
            'password': connectionVars['password'],
            'host': connectionVars['host'],
            'port': connectionVars['port'],
            'sslmode': 'require',
            'sslcert': pqsqlCert
        }

    def connect_to_database(self):
        return psycopg2.connect(**self.DATABASE_CONFIG)

    def ensure_tables(self):
        """Create tables if they don't exist"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                # Create users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        group_name VARCHAR(100),
                        checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_validated BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Create groups table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS groups (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        max_members INTEGER DEFAULT 3,
                        current_members INTEGER DEFAULT 0,
                        is_full BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print("Database tables created successfully")

    def create_user(self, email: str, group_name: Optional[str] = None, is_validated: bool = False) -> int:
        """Create a new user and return the user ID"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                insert_query = sql.SQL(
                    "INSERT INTO users (email, group_name, is_validated) VALUES (%s, %s, %s) RETURNING id"
                )
                cur.execute(insert_query, (email.lower().strip(), group_name, is_validated))
                conn.commit()
                return cur.fetchone()[0]

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, group_name, checked_in_at, is_validated FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'email': row[1],
                        'group_name': row[2],
                        'checked_in_at': row[3].isoformat() if row[3] else None,
                        'is_validated': row[4]
                    }
                return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, group_name, checked_in_at, is_validated FROM users WHERE email = %s", (email.lower().strip(),))
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'email': row[1],
                        'group_name': row[2],
                        'checked_in_at': row[3].isoformat() if row[3] else None,
                        'is_validated': row[4]
                    }
                return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, group_name, checked_in_at, is_validated FROM users ORDER BY checked_in_at DESC")
                rows = cur.fetchall()
                return [{
                    'id': row[0],
                    'email': row[1],
                    'group_name': row[2],
                    'checked_in_at': row[3].isoformat() if row[3] else None,
                    'is_validated': row[4]
                } for row in rows]

    def update_user_group(self, user_id: int, group_name: str) -> bool:
        """Update user's group assignment"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET group_name = %s WHERE id = %s", (group_name, user_id))
                conn.commit()
                return cur.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                return cur.rowcount > 0

    def delete_user_by_email(self, email: str) -> bool:
        """Delete user by email"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE email = %s", (email.lower().strip(),))
                conn.commit()
                return cur.rowcount > 0

    # Group management methods
    def create_group(self, name: str, max_members: int = 3) -> int:
        """Create a new group and return the group ID"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO groups (name, max_members) VALUES (%s, %s) RETURNING id",
                    (name, max_members)
                )
                conn.commit()
                return cur.fetchone()[0]

    def get_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get group by name"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, max_members, current_members, is_full, created_at FROM groups WHERE name = %s", (name,))
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'max_members': row[2],
                        'current_members': row[3],
                        'is_full': row[4],
                        'created_at': row[5].isoformat() if row[5] else None
                    }
                return None

    def get_available_group(self) -> Optional[Dict[str, Any]]:
        """Get first available group (not full)"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, max_members, current_members, is_full, created_at FROM groups WHERE is_full = FALSE LIMIT 1")
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'max_members': row[2],
                        'current_members': row[3],
                        'is_full': row[4],
                        'created_at': row[5].isoformat() if row[5] else None
                    }
                return None

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Get all groups"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, max_members, current_members, is_full, created_at FROM groups ORDER BY created_at")
                rows = cur.fetchall()
                return [{
                    'id': row[0],
                    'name': row[1],
                    'max_members': row[2],
                    'current_members': row[3],
                    'is_full': row[4],
                    'created_at': row[5].isoformat() if row[5] else None
                } for row in rows]

    def update_group_members(self, group_name: str, increment: int = 1) -> bool:
        """Update group member count and full status"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                # Update member count
                cur.execute(
                    "UPDATE groups SET current_members = current_members + %s WHERE name = %s",
                    (increment, group_name)
                )
                
                # Check if group is now full and update status
                cur.execute(
                    "UPDATE groups SET is_full = (current_members >= max_members) WHERE name = %s",
                    (group_name,)
                )
                
                conn.commit()
                return cur.rowcount > 0

    def get_group_count(self) -> int:
        """Get total number of groups"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM groups")
                return cur.fetchone()[0]

    def get_user_count(self) -> int:
        """Get total number of users"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                return cur.fetchone()[0]

    def reset_all_data(self) -> Dict[str, int]:
        """Reset all users and groups - use before demo session"""
        with self.connect_to_database() as conn:
            with conn.cursor() as cur:
                # Count existing data
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM groups")
                group_count = cur.fetchone()[0]
                
                # Delete all data
                cur.execute("DELETE FROM users")
                cur.execute("DELETE FROM groups")
                
                conn.commit()
                return {'users_removed': user_count, 'groups_removed': group_count}
