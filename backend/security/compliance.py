"""
GDPR/CCPA Compliance with Data Retention Policies
Enterprise compliance management system
"""

import sqlite3
import json
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import os


class DataCategory(Enum):
    """Categories of personal data"""
    IDENTITY = "identity"  # Name, email, username
    CONTACT = "contact"    # Address, phone, email
    BIOMETRIC = "biometric"  # Voice recordings, video
    TECHNICAL = "technical"  # IP address, device info
    BEHAVIORAL = "behavioral"  # Usage patterns, preferences
    CONTENT = "content"    # User-generated content


class LegalBasis(Enum):
    """Legal basis for data processing under GDPR"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataPurpose(Enum):
    """Purposes for data processing"""
    AUTHENTICATION = "authentication"
    SERVICE_PROVISION = "service_provision"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    LEGAL_COMPLIANCE = "legal_compliance"
    SECURITY = "security"


@dataclass
class DataSubject:
    """Data subject (user) information"""
    user_id: str
    email: str
    registration_date: datetime
    consent_status: Dict[str, bool]
    data_categories: Set[DataCategory]
    legal_basis: LegalBasis
    retention_period: int  # days
    last_activity: datetime
    location: str  # for jurisdiction determination


@dataclass
class DataProcessingRecord:
    """Record of data processing activity"""
    record_id: str
    data_subject_id: str
    data_category: DataCategory
    purpose: DataPurpose
    legal_basis: LegalBasis
    processing_date: datetime
    retention_until: datetime
    data_location: str
    third_parties: List[str]
    security_measures: List[str]


@dataclass
class ConsentRecord:
    """User consent tracking"""
    consent_id: str
    user_id: str
    purpose: DataPurpose
    granted: bool
    timestamp: datetime
    consent_text: str
    withdrawal_date: Optional[datetime] = None
    ip_address: str = ""
    user_agent: str = ""


class ComplianceManager:
    """Main compliance manager for GDPR/CCPA requirements"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_path = config.get('compliance_db_path', '/tmp/compliance.db')
        self.default_retention_days = config.get('default_retention_days', 365)
        self.jurisdiction = config.get('jurisdiction', 'EU')  # EU, CA, US
        self._initialize_database()
        self._initialize_retention_policies()
    
    def _initialize_database(self):
        """Initialize compliance database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Data subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_subjects (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                registration_date TIMESTAMP NOT NULL,
                consent_status TEXT NOT NULL,
                data_categories TEXT NOT NULL,
                legal_basis TEXT NOT NULL,
                retention_period INTEGER NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Processing records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_records (
                record_id TEXT PRIMARY KEY,
                data_subject_id TEXT NOT NULL,
                data_category TEXT NOT NULL,
                purpose TEXT NOT NULL,
                legal_basis TEXT NOT NULL,
                processing_date TIMESTAMP NOT NULL,
                retention_until TIMESTAMP NOT NULL,
                data_location TEXT,
                third_parties TEXT,
                security_measures TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (data_subject_id) REFERENCES data_subjects (user_id)
            )
        ''')
        
        # Consent records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                purpose TEXT NOT NULL,
                granted BOOLEAN NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                consent_text TEXT NOT NULL,
                withdrawal_date TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES data_subjects (user_id)
            )
        ''')
        
        # Data requests table (for subject access requests)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_requests (
                request_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                request_type TEXT NOT NULL,
                status TEXT NOT NULL,
                requested_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                data_export TEXT,
                verification_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Retention schedule table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retention_schedule (
                schedule_id TEXT PRIMARY KEY,
                data_category TEXT NOT NULL,
                purpose TEXT NOT NULL,
                retention_days INTEGER NOT NULL,
                legal_basis TEXT NOT NULL,
                auto_delete BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_retention_policies(self):
        """Initialize default data retention policies"""
        default_policies = [
            ('identity', 'authentication', 2555, 'contract', True),  # 7 years
            ('contact', 'service_provision', 1095, 'contract', True),  # 3 years
            ('behavioral', 'analytics', 730, 'legitimate_interests', True),  # 2 years
            ('content', 'service_provision', 1825, 'contract', False),  # 5 years, manual review
            ('technical', 'security', 365, 'legitimate_interests', True),  # 1 year
            ('biometric', 'service_provision', 1095, 'consent', False),  # 3 years, manual review
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for policy in default_policies:
            schedule_id = hashlib.md5(f"{policy[0]}_{policy[1]}".encode()).hexdigest()
            cursor.execute('''
                INSERT OR IGNORE INTO retention_schedule
                (schedule_id, data_category, purpose, retention_days, legal_basis, auto_delete)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (schedule_id, *policy))
        
        conn.commit()
        conn.close()
    
    def register_data_subject(self, user_data: Dict) -> Dict:
        """Register a new data subject with compliance tracking"""
        try:
            user_id = user_data['user_id']
            email = user_data['email']
            location = user_data.get('location', 'unknown')
            
            # Default consent status
            default_consent = {
                'essential': True,
                'analytics': False,
                'marketing': False,
                'third_party': False
            }
            
            data_subject = DataSubject(
                user_id=user_id,
                email=email,
                registration_date=datetime.utcnow(),
                consent_status=user_data.get('consent', default_consent),
                data_categories={DataCategory.IDENTITY, DataCategory.CONTACT},
                legal_basis=LegalBasis.CONSENT,
                retention_period=self.default_retention_days,
                last_activity=datetime.utcnow(),
                location=location
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_subjects
                (user_id, email, registration_date, consent_status, data_categories, 
                 legal_basis, retention_period, last_activity, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_subject.user_id,
                data_subject.email,
                data_subject.registration_date,
                json.dumps(data_subject.consent_status),
                json.dumps([cat.value for cat in data_subject.data_categories]),
                data_subject.legal_basis.value,
                data_subject.retention_period,
                data_subject.last_activity,
                data_subject.location
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'Data subject registered successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_consent(self, user_id: str, purpose: str, granted: bool, 
                      consent_text: str, ip_address: str = "", user_agent: str = "") -> Dict:
        """Record user consent for specific purpose"""
        try:
            consent_id = hashlib.md5(f"{user_id}_{purpose}_{datetime.utcnow().timestamp()}".encode()).hexdigest()
            
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                purpose=DataPurpose(purpose),
                granted=granted,
                timestamp=datetime.utcnow(),
                consent_text=consent_text,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO consent_records
                (consent_id, user_id, purpose, granted, timestamp, consent_text, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                consent_record.consent_id,
                consent_record.user_id,
                consent_record.purpose.value,
                consent_record.granted,
                consent_record.timestamp,
                consent_record.consent_text,
                consent_record.ip_address,
                consent_record.user_agent
            ))
            
            # Update data subject consent status
            cursor.execute('''
                SELECT consent_status FROM data_subjects WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if result:
                consent_status = json.loads(result[0])
                consent_status[purpose] = granted
                
                cursor.execute('''
                    UPDATE data_subjects SET consent_status = ? WHERE user_id = ?
                ''', (json.dumps(consent_status), user_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'consent_id': consent_id,
                'message': f'Consent {"granted" if granted else "withdrawn"} for {purpose}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def withdraw_consent(self, user_id: str, purpose: str) -> Dict:
        """Withdraw user consent for specific purpose"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update latest consent record
            cursor.execute('''
                UPDATE consent_records 
                SET withdrawal_date = ?
                WHERE user_id = ? AND purpose = ? AND granted = TRUE AND withdrawal_date IS NULL
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (datetime.utcnow(), user_id, purpose))
            
            # Record new withdrawal consent
            withdrawal_result = self.record_consent(
                user_id, purpose, False, 
                f"Consent withdrawn for {purpose} on {datetime.utcnow().isoformat()}"
            )
            
            conn.commit()
            conn.close()
            
            if withdrawal_result['success']:
                # Trigger data deletion if required
                self._handle_consent_withdrawal(user_id, purpose)
            
            return {
                'success': True,
                'message': f'Consent withdrawn for {purpose}',
                'next_steps': 'Data scheduled for deletion according to retention policy'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_consent_withdrawal(self, user_id: str, purpose: str):
        """Handle actions required when consent is withdrawn"""
        # In a real implementation, this would:
        # 1. Stop processing for that purpose
        # 2. Schedule data deletion
        # 3. Notify relevant systems
        # 4. Update retention schedules
        pass
    
    def create_data_request(self, user_id: str, request_type: str) -> Dict:
        """Create a data subject access request (GDPR Article 15, CCPA)"""
        try:
            valid_types = ['access', 'portability', 'rectification', 'erasure', 'restriction']
            if request_type not in valid_types:
                return {'success': False, 'error': 'Invalid request type'}
            
            request_id = hashlib.md5(f"{user_id}_{request_type}_{datetime.utcnow().timestamp()}".encode()).hexdigest()
            verification_token = hashlib.sha256(f"{request_id}_{user_id}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_requests
                (request_id, user_id, request_type, status, requested_at, verification_token)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request_id, user_id, request_type, 'pending', datetime.utcnow(), verification_token))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'request_id': request_id,
                'verification_token': verification_token,
                'message': f'{request_type.title()} request created successfully',
                'estimated_completion': '30 days'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_data_access_request(self, request_id: str, verification_token: str) -> Dict:
        """Process a data access request and generate data export"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify request
            cursor.execute('''
                SELECT user_id, request_type, status FROM data_requests
                WHERE request_id = ? AND verification_token = ?
            ''', (request_id, verification_token))
            
            request_data = cursor.fetchone()
            if not request_data:
                return {'success': False, 'error': 'Invalid request or verification token'}
            
            user_id, request_type, status = request_data
            
            if status != 'pending':
                return {'success': False, 'error': f'Request already {status}'}
            
            # Generate data export
            user_data_export = self._generate_user_data_export(user_id)
            
            # Update request status
            cursor.execute('''
                UPDATE data_requests
                SET status = ?, completed_at = ?, data_export = ?
                WHERE request_id = ?
            ''', ('completed', datetime.utcnow(), json.dumps(user_data_export), request_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'request_id': request_id,
                'data_export': user_data_export,
                'completed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_user_data_export(self, user_id: str) -> Dict:
        """Generate comprehensive data export for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get data subject info
        cursor.execute('SELECT * FROM data_subjects WHERE user_id = ?', (user_id,))
        subject_data = cursor.fetchone()
        
        # Get processing records
        cursor.execute('SELECT * FROM processing_records WHERE data_subject_id = ?', (user_id,))
        processing_records = cursor.fetchall()
        
        # Get consent history
        cursor.execute('SELECT * FROM consent_records WHERE user_id = ?', (user_id,))
        consent_history = cursor.fetchall()
        
        # Get data requests
        cursor.execute('SELECT * FROM data_requests WHERE user_id = ?', (user_id,))
        data_requests = cursor.fetchall()
        
        conn.close()
        
        return {
            'user_profile': {
                'user_id': user_id,
                'email': subject_data[1] if subject_data else None,
                'registration_date': subject_data[2] if subject_data else None,
                'last_activity': subject_data[7] if subject_data else None,
            },
            'consent_history': [
                {
                    'purpose': record[2],
                    'granted': bool(record[3]),
                    'timestamp': record[4],
                    'withdrawal_date': record[6]
                }
                for record in consent_history
            ],
            'data_processing': [
                {
                    'category': record[2],
                    'purpose': record[3],
                    'legal_basis': record[4],
                    'processing_date': record[5],
                    'retention_until': record[6]
                }
                for record in processing_records
            ],
            'data_requests': [
                {
                    'request_type': record[2],
                    'status': record[3],
                    'requested_at': record[4],
                    'completed_at': record[5]
                }
                for record in data_requests
            ],
            'export_generated_at': datetime.utcnow().isoformat()
        }
    
    def schedule_data_deletion(self) -> Dict:
        """Schedule data deletion based on retention policies"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find data past retention period
            cursor.execute('''
                SELECT ds.user_id, ds.email, ds.retention_period, ds.last_activity
                FROM data_subjects ds
                WHERE datetime(ds.last_activity, '+' || ds.retention_period || ' days') < datetime('now')
            ''')
            
            expired_subjects = cursor.fetchall()
            deletion_scheduled = []
            
            for subject in expired_subjects:
                user_id, email, retention_period, last_activity = subject
                
                # Check if consent allows deletion
                cursor.execute('''
                    SELECT consent_status FROM data_subjects WHERE user_id = ?
                ''', (user_id,))
                
                consent_data = cursor.fetchone()
                if consent_data:
                    consent_status = json.loads(consent_data[0])
                    
                    # Only delete if no active consents requiring retention
                    if not any(consent_status.values()):
                        deletion_scheduled.append({
                            'user_id': user_id,
                            'email': email,
                            'scheduled_deletion_date': datetime.utcnow() + timedelta(days=30),
                            'reason': 'retention_period_expired'
                        })
            
            conn.close()
            
            return {
                'success': True,
                'scheduled_deletions': len(deletion_scheduled),
                'deletion_list': deletion_scheduled
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total data subjects
            cursor.execute('SELECT COUNT(*) FROM data_subjects')
            total_subjects = cursor.fetchone()[0]
            
            # Consent statistics
            cursor.execute('''
                SELECT purpose, 
                       SUM(CASE WHEN granted = 1 THEN 1 ELSE 0 END) as granted,
                       SUM(CASE WHEN granted = 0 THEN 1 ELSE 0 END) as withdrawn
                FROM consent_records 
                GROUP BY purpose
            ''')
            consent_stats = cursor.fetchall()
            
            # Data requests statistics
            cursor.execute('''
                SELECT request_type, status, COUNT(*) 
                FROM data_requests 
                GROUP BY request_type, status
            ''')
            request_stats = cursor.fetchall()
            
            # Retention compliance
            cursor.execute('''
                SELECT COUNT(*) 
                FROM data_subjects 
                WHERE datetime(last_activity, '+' || retention_period || ' days') < datetime('now')
            ''')
            expired_data_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_data_subjects': total_subjects,
                'consent_statistics': {
                    row[0]: {'granted': row[1], 'withdrawn': row[2]}
                    for row in consent_stats
                },
                'data_request_statistics': {
                    f"{row[0]}_{row[1]}": row[2]
                    for row in request_stats
                },
                'retention_compliance': {
                    'subjects_past_retention': expired_data_count,
                    'compliance_rate': ((total_subjects - expired_data_count) / total_subjects * 100) if total_subjects > 0 else 100
                },
                'jurisdiction': self.jurisdiction,
                'report_generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}