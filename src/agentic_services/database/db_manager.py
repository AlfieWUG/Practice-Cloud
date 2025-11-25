"""Database Manager - SQLite persistence for Agentic Services"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for the platform"""
    
    def __init__(self, db_path: str = "data/agentic_services.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_database()
    
    def get_connection(self):
        """Get or create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
        return self.conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                requirements TEXT,
                timeline TEXT,
                priority TEXT,
                budget TEXT,
                complexity TEXT,
                status TEXT DEFAULT 'Planning',
                phase TEXT DEFAULT 'Discovery',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                demo_mode BOOLEAN DEFAULT 1,
                source_infrastructure TEXT,
                source_code TEXT,
                target_config TEXT,
                aws_credentials TEXT
            )
        """)
        
        # Agent Executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                agent_name TEXT NOT NULL,
                phase TEXT NOT NULL,
                status TEXT DEFAULT 'queued',
                progress INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                error_message TEXT,
                result_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                agent_name TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT,
                file_size INTEGER,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                type TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                title TEXT NOT NULL,
                message TEXT,
                is_read BOOLEAN DEFAULT 0,
                action_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Checklist Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                item TEXT NOT NULL,
                description TEXT,
                is_completed BOOLEAN DEFAULT 0,
                is_required BOOLEAN DEFAULT 1,
                completed_at TIMESTAMP,
                completed_by TEXT,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Cost Tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                date DATE NOT NULL,
                service_name TEXT NOT NULL,
                cost_amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                resource_count INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Activity Log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_name TEXT,
                action_type TEXT NOT NULL,
                action_description TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_project ON agent_executions(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_status ON agent_executions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_project ON artifacts(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_project ON notifications(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checklist_project ON checklist_items(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_project ON cost_tracking(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_project ON activity_log(project_id)")
        
        conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    # ==================== PROJECT OPERATIONS ====================
    
    def create_project(self, project_data: Dict[str, Any]) -> int:
        """Create a new project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects 
            (name, description, requirements, timeline, priority, budget, complexity, 
             status, phase, progress, demo_mode, source_infrastructure, source_code, 
             target_config, aws_credentials)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_data.get('name'),
            project_data.get('description'),
            project_data.get('requirements'),
            project_data.get('timeline'),
            project_data.get('priority'),
            project_data.get('budget'),
            project_data.get('complexity'),
            project_data.get('status', 'Planning'),
            project_data.get('phase', 'Discovery'),
            project_data.get('progress', 0),
            project_data.get('demo_mode', True),
            json.dumps(project_data.get('source_infrastructure', {})),
            json.dumps(project_data.get('source_code', {})),
            json.dumps(project_data.get('target_config', {})),
            json.dumps(project_data.get('aws_credentials', {}))
        ))
        
        project_id = cursor.lastrowid
        conn.commit()
        
        # Log activity
        self.log_activity(project_id, None, 'project_created', f"Project '{project_data.get('name')}' created")
        
        return project_id
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get a project by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_project_dict(row)
        return None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        return [self._row_to_project_dict(row) for row in rows]
    
    def update_project(self, project_id: int, updates: Dict[str, Any]) -> bool:
        """Update a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        update_fields = []
        values = []
        
        for key, value in updates.items():
            if key in ['source_infrastructure', 'source_code', 'target_config', 'aws_credentials']:
                value = json.dumps(value)
            update_fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(project_id)
        
        cursor.execute(f"""
            UPDATE projects 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all related data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        
        return cursor.rowcount > 0
    
    # ==================== AGENT EXECUTION OPERATIONS ====================
    
    def create_execution(self, execution_data: Dict[str, Any]) -> int:
        """Create a new agent execution record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO agent_executions 
            (project_id, agent_name, phase, status, progress, started_at, result_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_data['project_id'],
            execution_data['agent_name'],
            execution_data['phase'],
            execution_data.get('status', 'queued'),
            execution_data.get('progress', 0),
            execution_data.get('started_at'),
            json.dumps(execution_data.get('result_data', {}))
        ))
        
        execution_id = cursor.lastrowid
        conn.commit()
        
        return execution_id
    
    def update_execution(self, execution_id: int, updates: Dict[str, Any]) -> bool:
        """Update an agent execution"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        
        for key, value in updates.items():
            if key == 'result_data':
                value = json.dumps(value)
            update_fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(execution_id)
        
        cursor.execute(f"""
            UPDATE agent_executions 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, values)
        
        conn.commit()
        return cursor.rowcount > 0
    
    def get_project_executions(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all executions for a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM agent_executions 
            WHERE project_id = ? 
            ORDER BY created_at DESC
        """, (project_id,))
        
        rows = cursor.fetchall()
        return [self._row_to_execution_dict(row) for row in rows]
    
    def get_execution_stats(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Get execution statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        where_clause = f"WHERE project_id = {project_id}" if project_id else ""
        
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN duration_seconds IS NOT NULL THEN duration_seconds ELSE 0 END) as avg_duration
            FROM agent_executions
            {where_clause}
        """)
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    # ==================== ARTIFACT OPERATIONS ====================
    
    def create_artifact(self, artifact_data: Dict[str, Any]) -> int:
        """Create a new artifact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO artifacts 
            (project_id, agent_name, artifact_type, title, description, 
             file_path, file_size, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact_data['project_id'],
            artifact_data['agent_name'],
            artifact_data['artifact_type'],
            artifact_data['title'],
            artifact_data.get('description'),
            artifact_data.get('file_path'),
            artifact_data.get('file_size'),
            artifact_data.get('content'),
            json.dumps(artifact_data.get('metadata', {}))
        ))
        
        artifact_id = cursor.lastrowid
        conn.commit()
        
        return artifact_id
    
    def get_project_artifacts(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all artifacts for a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM artifacts 
            WHERE project_id = ? 
            ORDER BY created_at DESC
        """, (project_id,))
        
        rows = cursor.fetchall()
        return [self._row_to_artifact_dict(row) for row in rows]
    
    # ==================== NOTIFICATION OPERATIONS ====================
    
    def create_notification(self, notification_data: Dict[str, Any]) -> int:
        """Create a new notification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications 
            (project_id, type, severity, title, message, action_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            notification_data.get('project_id'),
            notification_data['type'],
            notification_data.get('severity', 'info'),
            notification_data['title'],
            notification_data.get('message'),
            notification_data.get('action_url')
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        
        return notification_id
    
    def get_unread_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get unread notifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE is_read = 0 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        
        return cursor.rowcount > 0
    
    # ==================== ACTIVITY LOG ====================
    
    def log_activity(self, project_id: Optional[int], user_name: Optional[str], 
                     action_type: str, description: str, entity_type: Optional[str] = None,
                     entity_id: Optional[int] = None, metadata: Optional[Dict] = None):
        """Log an activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO activity_log 
            (project_id, user_name, action_type, action_description, entity_type, entity_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            user_name,
            action_type,
            description,
            entity_type,
            entity_id,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
    
    def get_recent_activity(self, project_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent activity log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if project_id:
            cursor.execute("""
                SELECT * FROM activity_log 
                WHERE project_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (project_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM activity_log 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ==================== HELPER METHODS ====================
    
    def _row_to_project_dict(self, row) -> Dict[str, Any]:
        """Convert database row to project dictionary"""
        project = dict(row)
        
        # Parse JSON fields
        for field in ['source_infrastructure', 'source_code', 'target_config', 'aws_credentials']:
            if project.get(field):
                try:
                    project[field] = json.loads(project[field])
                except:
                    project[field] = {}
        
        return project
    
    def _row_to_execution_dict(self, row) -> Dict[str, Any]:
        """Convert database row to execution dictionary"""
        execution = dict(row)
        
        if execution.get('result_data'):
            try:
                execution['result_data'] = json.loads(execution['result_data'])
            except:
                execution['result_data'] = {}
        
        return execution
    
    def _row_to_artifact_dict(self, row) -> Dict[str, Any]:
        """Convert database row to artifact dictionary"""
        artifact = dict(row)
        
        if artifact.get('metadata'):
            try:
                artifact['metadata'] = json.loads(artifact['metadata'])
            except:
                artifact['metadata'] = {}
        
        return artifact
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Singleton instance
_db_instance = None

def get_db() -> DatabaseManager:
    """Get database manager singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
