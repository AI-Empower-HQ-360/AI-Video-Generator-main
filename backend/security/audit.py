"""
Security Audit Trails and Intrusion Detection
Enterprise security monitoring and incident response
"""

import sqlite3
import json
import hashlib
import ipaddress
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re
import time
from collections import defaultdict, deque


class SecurityEventType(Enum):
    """Types of security events to monitor"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    ADMIN_ACTION = "admin_action"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    SYSTEM_ERROR = "system_error"


class RiskLevel(Enum):
    """Risk levels for security events"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SecurityEvent:
    """Individual security event record"""
    event_id: str
    event_type: SecurityEventType
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    resource: str
    action: str
    outcome: str  # success, failure, blocked
    risk_level: RiskLevel
    details: Dict
    session_id: Optional[str] = None
    geolocation: Optional[str] = None


@dataclass
class SecurityAlert:
    """Security alert for suspicious activity"""
    alert_id: str
    alert_type: str
    severity: RiskLevel
    timestamp: datetime
    description: str
    affected_user: Optional[str]
    source_ip: str
    triggered_by: List[str]  # event IDs that triggered this alert
    status: str  # open, investigating, resolved, false_positive
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class IntrusionDetectionEngine:
    """Real-time intrusion detection and threat analysis"""
    
    def __init__(self):
        self.failed_login_window = 300  # 5 minutes
        self.max_failed_logins = 5
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_minute = 100
        self.suspicious_ips = set()
        self.blocked_ips = set()
        
        # Track recent events for pattern detection
        self.recent_events = deque(maxlen=1000)
        self.ip_request_counts = defaultdict(lambda: deque(maxlen=100))
        self.failed_logins = defaultdict(lambda: deque(maxlen=10))
        
        # Known malicious patterns
        self.malicious_patterns = [
            r'(?i)(\<script\>|javascript:|vbscript:)',  # XSS attempts
            r'(?i)(union\s+select|or\s+1=1|drop\s+table)',  # SQL injection
            r'(?i)(\.\.\/|\.\.\\)',  # Path traversal
            r'(?i)(exec\s*\(|eval\s*\(|system\s*\()',  # Code injection
        ]
    
    def analyze_event(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Analyze security event and generate alerts if necessary"""
        alerts = []
        self.recent_events.append(event)
        
        # Check for various threat patterns
        alerts.extend(self._check_brute_force_attack(event))
        alerts.extend(self._check_rate_limiting(event))
        alerts.extend(self._check_suspicious_patterns(event))
        alerts.extend(self._check_privilege_escalation(event))
        alerts.extend(self._check_unusual_access_patterns(event))
        alerts.extend(self._check_geolocation_anomalies(event))
        
        return alerts
    
    def _check_brute_force_attack(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Detect brute force login attempts"""
        alerts = []
        
        if event.event_type == SecurityEventType.LOGIN_FAILURE:
            ip_failures = self.failed_logins[event.ip_address]
            ip_failures.append(event.timestamp)
            
            # Remove old failures outside the window
            cutoff_time = event.timestamp - timedelta(seconds=self.failed_login_window)
            while ip_failures and ip_failures[0] < cutoff_time:
                ip_failures.popleft()
            
            # Check if threshold exceeded
            if len(ip_failures) >= self.max_failed_logins:
                alert = SecurityAlert(
                    alert_id=f"bf_{event.ip_address}_{int(time.time())}",
                    alert_type="brute_force_attack",
                    severity=RiskLevel.HIGH,
                    timestamp=event.timestamp,
                    description=f"Brute force attack detected from {event.ip_address}",
                    affected_user=event.user_id,
                    source_ip=event.ip_address,
                    triggered_by=[event.event_id],
                    status="open"
                )
                alerts.append(alert)
                self.suspicious_ips.add(event.ip_address)
        
        return alerts
    
    def _check_rate_limiting(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Detect rate limit violations"""
        alerts = []
        
        ip_requests = self.ip_request_counts[event.ip_address]
        ip_requests.append(event.timestamp)
        
        # Remove old requests outside the window
        cutoff_time = event.timestamp - timedelta(seconds=self.rate_limit_window)
        while ip_requests and ip_requests[0] < cutoff_time:
            ip_requests.popleft()
        
        # Check if rate limit exceeded
        if len(ip_requests) > self.max_requests_per_minute:
            alert = SecurityAlert(
                alert_id=f"rl_{event.ip_address}_{int(time.time())}",
                alert_type="rate_limit_exceeded",
                severity=RiskLevel.MEDIUM,
                timestamp=event.timestamp,
                description=f"Rate limit exceeded from {event.ip_address}",
                affected_user=event.user_id,
                source_ip=event.ip_address,
                triggered_by=[event.event_id],
                status="open"
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_suspicious_patterns(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Check for malicious patterns in request data"""
        alerts = []
        
        # Check event details for malicious patterns
        details_str = json.dumps(event.details)
        
        for pattern in self.malicious_patterns:
            if re.search(pattern, details_str):
                alert = SecurityAlert(
                    alert_id=f"mp_{hashlib.md5(pattern.encode()).hexdigest()[:8]}_{int(time.time())}",
                    alert_type="malicious_pattern_detected",
                    severity=RiskLevel.HIGH,
                    timestamp=event.timestamp,
                    description=f"Malicious pattern detected in request from {event.ip_address}",
                    affected_user=event.user_id,
                    source_ip=event.ip_address,
                    triggered_by=[event.event_id],
                    status="open"
                )
                alerts.append(alert)
                break
        
        return alerts
    
    def _check_privilege_escalation(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Detect potential privilege escalation attempts"""
        alerts = []
        
        if event.event_type == SecurityEventType.PERMISSION_DENIED:
            # Check if user is attempting to access high-privilege resources
            if any(term in event.resource.lower() for term in ['admin', 'system', 'config', 'user']):
                alert = SecurityAlert(
                    alert_id=f"pe_{event.user_id}_{int(time.time())}",
                    alert_type="privilege_escalation_attempt",
                    severity=RiskLevel.HIGH,
                    timestamp=event.timestamp,
                    description=f"Potential privilege escalation attempt by {event.user_id}",
                    affected_user=event.user_id,
                    source_ip=event.ip_address,
                    triggered_by=[event.event_id],
                    status="open"
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_unusual_access_patterns(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Detect unusual access patterns"""
        alerts = []
        
        if event.user_id:
            # Check for access outside normal hours (example: outside 9-17)
            if event.timestamp.hour < 9 or event.timestamp.hour > 17:
                # Check if this is unusual for this user
                recent_user_events = [e for e in self.recent_events 
                                    if e.user_id == event.user_id and 
                                       e.timestamp > event.timestamp - timedelta(days=7)]
                
                normal_hour_events = [e for e in recent_user_events 
                                    if 9 <= e.timestamp.hour <= 17]
                
                # If user typically accesses during business hours
                if len(normal_hour_events) > len(recent_user_events) * 0.8:
                    alert = SecurityAlert(
                        alert_id=f"ua_{event.user_id}_{int(time.time())}",
                        alert_type="unusual_access_time",
                        severity=RiskLevel.MEDIUM,
                        timestamp=event.timestamp,
                        description=f"Unusual access time for user {event.user_id}",
                        affected_user=event.user_id,
                        source_ip=event.ip_address,
                        triggered_by=[event.event_id],
                        status="open"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _check_geolocation_anomalies(self, event: SecurityEvent) -> List[SecurityAlert]:
        """Check for geolocation-based anomalies"""
        alerts = []
        
        # This would integrate with a geolocation service
        # For now, just check for private/suspicious IP ranges
        try:
            ip = ipaddress.ip_address(event.ip_address)
            
            # Check for Tor exit nodes (simplified example)
            tor_ranges = [
                ipaddress.ip_network('198.98.0.0/16'),  # Example Tor range
            ]
            
            for tor_range in tor_ranges:
                if ip in tor_range:
                    alert = SecurityAlert(
                        alert_id=f"tor_{event.ip_address}_{int(time.time())}",
                        alert_type="tor_access_detected",
                        severity=RiskLevel.HIGH,
                        timestamp=event.timestamp,
                        description=f"Access from potential Tor exit node {event.ip_address}",
                        affected_user=event.user_id,
                        source_ip=event.ip_address,
                        triggered_by=[event.event_id],
                        status="open"
                    )
                    alerts.append(alert)
                    break
        
        except ValueError:
            # Invalid IP address
            pass
        
        return alerts


class AuditTrailManager:
    """Main audit trail manager for security monitoring"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_path = config.get('audit_db_path', '/tmp/audit_trail.db')
        self.retention_days = config.get('audit_retention_days', 2555)  # 7 years default
        self.intrusion_detection = IntrusionDetectionEngine()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize audit trail database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Security events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                timestamp TIMESTAMP NOT NULL,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                outcome TEXT NOT NULL,
                risk_level INTEGER NOT NULL,
                details TEXT NOT NULL,
                session_id TEXT,
                geolocation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT NOT NULL,
                severity INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                description TEXT NOT NULL,
                affected_user TEXT,
                source_ip TEXT NOT NULL,
                triggered_by TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_to TEXT,
                resolution_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_id ON security_events(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_ip ON security_events(ip_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON security_alerts(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON security_alerts(severity)')
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type: str, user_id: Optional[str], ip_address: str,
                  user_agent: str, resource: str, action: str, outcome: str,
                  details: Dict, session_id: Optional[str] = None,
                  risk_level: str = "LOW") -> Dict:
        """Log a security event and trigger intrusion detection analysis"""
        try:
            event_id = hashlib.sha256(f"{event_type}_{user_id}_{ip_address}_{time.time()}".encode()).hexdigest()
            
            event = SecurityEvent(
                event_id=event_id,
                event_type=SecurityEventType(event_type),
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                resource=resource,
                action=action,
                outcome=outcome,
                risk_level=RiskLevel[risk_level.upper()],
                details=details,
                session_id=session_id
            )
            
            # Store event in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events
                (event_id, event_type, user_id, ip_address, user_agent, timestamp,
                 resource, action, outcome, risk_level, details, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.event_type.value,
                event.user_id,
                event.ip_address,
                event.user_agent,
                event.timestamp,
                event.resource,
                event.action,
                event.outcome,
                event.risk_level.value,
                json.dumps(event.details),
                event.session_id
            ))
            
            conn.commit()
            conn.close()
            
            # Run intrusion detection analysis
            alerts = self.intrusion_detection.analyze_event(event)
            
            # Store any generated alerts
            for alert in alerts:
                self._store_alert(alert)
            
            return {
                'success': True,
                'event_id': event_id,
                'alerts_generated': len(alerts),
                'alert_ids': [alert.alert_id for alert in alerts]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _store_alert(self, alert: SecurityAlert):
        """Store security alert in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_alerts
            (alert_id, alert_type, severity, timestamp, description, affected_user,
             source_ip, triggered_by, status, assigned_to, resolution_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_id,
            alert.alert_type,
            alert.severity.value,
            alert.timestamp,
            alert.description,
            alert.affected_user,
            alert.source_ip,
            json.dumps(alert.triggered_by),
            alert.status,
            alert.assigned_to,
            alert.resolution_notes
        ))
        
        conn.commit()
        conn.close()
    
    def get_security_events(self, filters: Dict) -> Dict:
        """Retrieve security events with filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query with filters
            where_conditions = []
            params = []
            
            if filters.get('user_id'):
                where_conditions.append('user_id = ?')
                params.append(filters['user_id'])
            
            if filters.get('ip_address'):
                where_conditions.append('ip_address = ?')
                params.append(filters['ip_address'])
            
            if filters.get('event_type'):
                where_conditions.append('event_type = ?')
                params.append(filters['event_type'])
            
            if filters.get('start_date'):
                where_conditions.append('timestamp >= ?')
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                where_conditions.append('timestamp <= ?')
                params.append(filters['end_date'])
            
            if filters.get('risk_level'):
                where_conditions.append('risk_level >= ?')
                params.append(RiskLevel[filters['risk_level'].upper()].value)
            
            where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
            
            query = f'''
                SELECT * FROM security_events
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            
            limit = filters.get('limit', 100)
            params.append(limit)
            
            cursor.execute(query, params)
            events = cursor.fetchall()
            
            conn.close()
            
            # Convert to dictionaries
            event_dicts = []
            for event in events:
                event_dict = {
                    'event_id': event[0],
                    'event_type': event[1],
                    'user_id': event[2],
                    'ip_address': event[3],
                    'user_agent': event[4],
                    'timestamp': event[5],
                    'resource': event[6],
                    'action': event[7],
                    'outcome': event[8],
                    'risk_level': event[9],
                    'details': json.loads(event[10]),
                    'session_id': event[11]
                }
                event_dicts.append(event_dict)
            
            return {
                'success': True,
                'events': event_dicts,
                'total_events': len(event_dicts)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_security_alerts(self, status: str = None, severity: str = None) -> Dict:
        """Retrieve security alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if status:
                where_conditions.append('status = ?')
                params.append(status)
            
            if severity:
                where_conditions.append('severity >= ?')
                params.append(RiskLevel[severity.upper()].value)
            
            where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
            
            query = f'''
                SELECT * FROM security_alerts
                WHERE {where_clause}
                ORDER BY timestamp DESC
            '''
            
            cursor.execute(query, params)
            alerts = cursor.fetchall()
            
            conn.close()
            
            # Convert to dictionaries
            alert_dicts = []
            for alert in alerts:
                alert_dict = {
                    'alert_id': alert[0],
                    'alert_type': alert[1],
                    'severity': alert[2],
                    'timestamp': alert[3],
                    'description': alert[4],
                    'affected_user': alert[5],
                    'source_ip': alert[6],
                    'triggered_by': json.loads(alert[7]),
                    'status': alert[8],
                    'assigned_to': alert[9],
                    'resolution_notes': alert[10]
                }
                alert_dicts.append(alert_dict)
            
            return {
                'success': True,
                'alerts': alert_dicts,
                'total_alerts': len(alert_dicts)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_alert_status(self, alert_id: str, status: str, assigned_to: str = None,
                           resolution_notes: str = None) -> Dict:
        """Update security alert status and assignment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            update_fields = ['status = ?', 'updated_at = ?']
            params = [status, datetime.utcnow()]
            
            if assigned_to:
                update_fields.append('assigned_to = ?')
                params.append(assigned_to)
            
            if resolution_notes:
                update_fields.append('resolution_notes = ?')
                params.append(resolution_notes)
            
            params.append(alert_id)
            
            query = f'''
                UPDATE security_alerts
                SET {', '.join(update_fields)}
                WHERE alert_id = ?
            '''
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': 'Alert not found'}
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Alert {alert_id} updated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_security_report(self, start_date: str, end_date: str) -> Dict:
        """Generate comprehensive security report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Event statistics
            cursor.execute('''
                SELECT event_type, outcome, COUNT(*)
                FROM security_events
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY event_type, outcome
            ''', (start_date, end_date))
            event_stats = cursor.fetchall()
            
            # Alert statistics
            cursor.execute('''
                SELECT alert_type, severity, status, COUNT(*)
                FROM security_alerts
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY alert_type, severity, status
            ''', (start_date, end_date))
            alert_stats = cursor.fetchall()
            
            # Top source IPs
            cursor.execute('''
                SELECT ip_address, COUNT(*) as event_count
                FROM security_events
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY ip_address
                ORDER BY event_count DESC
                LIMIT 10
            ''', (start_date, end_date))
            top_ips = cursor.fetchall()
            
            # Failed login attempts
            cursor.execute('''
                SELECT ip_address, user_id, COUNT(*) as attempts
                FROM security_events
                WHERE timestamp BETWEEN ? AND ?
                AND event_type = 'login_failure'
                GROUP BY ip_address, user_id
                ORDER BY attempts DESC
                LIMIT 10
            ''', (start_date, end_date))
            failed_logins = cursor.fetchall()
            
            conn.close()
            
            return {
                'report_period': {'start': start_date, 'end': end_date},
                'event_statistics': {
                    f"{row[0]}_{row[1]}": row[2]
                    for row in event_stats
                },
                'alert_statistics': {
                    f"{row[0]}_sev{row[1]}_{row[2]}": row[3]
                    for row in alert_stats
                },
                'top_source_ips': [
                    {'ip': row[0], 'events': row[1]}
                    for row in top_ips
                ],
                'failed_login_attempts': [
                    {'ip': row[0], 'user': row[1], 'attempts': row[2]}
                    for row in failed_logins
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}