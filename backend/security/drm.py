"""
Digital Rights Management (DRM) and Video Protection
Watermarking and content protection for video assets
"""

import hashlib
import secrets
import base64
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import os
import io
from PIL import Image, ImageDraw, ImageFont
import time


class ProtectionLevel(Enum):
    """Levels of content protection"""
    BASIC = 1
    STANDARD = 2
    PREMIUM = 3
    ENTERPRISE = 4


class WatermarkType(Enum):
    """Types of watermarks"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    DYNAMIC = "dynamic"
    FORENSIC = "forensic"


class AccessRight(Enum):
    """Content access rights"""
    VIEW = "view"
    DOWNLOAD = "download"
    SHARE = "share"
    EDIT = "edit"
    PRINT = "print"
    COPY = "copy"


@dataclass
class ContentLicense:
    """Digital content license"""
    license_id: str
    content_id: str
    user_id: str
    rights: List[AccessRight]
    expiry_date: Optional[datetime]
    max_views: Optional[int]
    max_downloads: Optional[int]
    geographic_restrictions: List[str]
    device_restrictions: List[str]
    created_at: datetime
    protection_level: ProtectionLevel


@dataclass
class WatermarkConfig:
    """Watermark configuration"""
    watermark_id: str
    watermark_type: WatermarkType
    content: str  # Text or image path
    position: str  # top-left, top-right, center, etc.
    opacity: float
    size: Tuple[int, int]
    font_size: int
    color: str
    rotation: int


@dataclass
class AccessLog:
    """Content access tracking"""
    access_id: str
    content_id: str
    user_id: str
    access_type: AccessRight
    timestamp: datetime
    ip_address: str
    device_info: str
    session_id: str
    success: bool
    metadata: Dict


class DigitalRightsManager:
    """Main DRM system for content protection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_path = config.get('drm_db_path', '/tmp/drm.db')
        self.content_storage_path = config.get('content_storage_path', '/tmp/protected_content')
        self.watermark_storage_path = config.get('watermark_storage_path', '/tmp/watermarks')
        self._initialize_database()
        self._ensure_storage_directories()
    
    def _initialize_database(self):
        """Initialize DRM database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Content licenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_licenses (
                license_id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                rights TEXT NOT NULL,
                expiry_date TIMESTAMP,
                max_views INTEGER,
                max_downloads INTEGER,
                geographic_restrictions TEXT,
                device_restrictions TEXT,
                created_at TIMESTAMP NOT NULL,
                protection_level INTEGER NOT NULL,
                current_views INTEGER DEFAULT 0,
                current_downloads INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Watermark configurations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watermark_configs (
                watermark_id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                watermark_type TEXT NOT NULL,
                content TEXT NOT NULL,
                position TEXT NOT NULL,
                opacity REAL NOT NULL,
                size_width INTEGER NOT NULL,
                size_height INTEGER NOT NULL,
                font_size INTEGER,
                color TEXT,
                rotation INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Access logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                access_id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                access_type TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                ip_address TEXT,
                device_info TEXT,
                session_id TEXT,
                success BOOLEAN NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Protected content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS protected_content (
                content_id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                protected_filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                protection_level INTEGER NOT NULL,
                encryption_key_id TEXT,
                watermark_applied BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT NOT NULL
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_licenses_content ON content_licenses(content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_licenses_user ON content_licenses(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_content ON access_logs(content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_user ON access_logs(user_id)')
        
        conn.commit()
        conn.close()
    
    def _ensure_storage_directories(self):
        """Ensure storage directories exist"""
        os.makedirs(self.content_storage_path, exist_ok=True)
        os.makedirs(self.watermark_storage_path, exist_ok=True)
        
        # Set restrictive permissions
        os.chmod(self.content_storage_path, 0o700)
        os.chmod(self.watermark_storage_path, 0o700)
    
    def protect_content(self, content_path: str, content_id: str, 
                       protection_level: str = "STANDARD") -> Dict:
        """Apply DRM protection to content"""
        try:
            if not os.path.exists(content_path):
                return {'success': False, 'error': 'Content file not found'}
            
            protection_enum = ProtectionLevel[protection_level.upper()]
            
            # Generate protected filename
            file_extension = os.path.splitext(content_path)[1]
            protected_filename = f"{content_id}_protected{file_extension}"
            protected_path = os.path.join(self.content_storage_path, protected_filename)
            
            # Calculate checksum
            with open(content_path, 'rb') as f:
                content_data = f.read()
                checksum = hashlib.sha256(content_data).hexdigest()
            
            # Apply protection based on level
            if protection_enum in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                # Encrypt content for higher protection levels
                from .encryption import EncryptionManager
                encryption_manager = EncryptionManager(self.config)
                
                encryption_result = encryption_manager.encrypt_content(
                    content_data, content_id, "video"
                )
                
                if not encryption_result['success']:
                    return {'success': False, 'error': 'Content encryption failed'}
                
                # Store encrypted content
                with open(protected_path, 'wb') as f:
                    f.write(base64.b64decode(encryption_result['encrypted_data']))
                
                encryption_key_id = encryption_result['key_id']
            else:
                # Basic protection - just copy with access control
                with open(protected_path, 'wb') as f:
                    f.write(content_data)
                encryption_key_id = None
            
            # Store protection metadata
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO protected_content
                (content_id, original_filename, protected_filename, content_type,
                 file_size, protection_level, encryption_key_id, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content_id,
                os.path.basename(content_path),
                protected_filename,
                self._get_content_type(file_extension),
                len(content_data),
                protection_enum.value,
                encryption_key_id,
                checksum
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'content_id': content_id,
                'protected_path': protected_path,
                'protection_level': protection_level,
                'encryption_applied': encryption_key_id is not None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_license(self, content_id: str, user_id: str, rights: List[str],
                      expiry_date: Optional[str] = None, max_views: Optional[int] = None,
                      max_downloads: Optional[int] = None, 
                      geographic_restrictions: List[str] = None,
                      device_restrictions: List[str] = None,
                      protection_level: str = "STANDARD") -> Dict:
        """Create a content license for a user"""
        try:
            license_id = hashlib.sha256(f"{content_id}_{user_id}_{time.time()}".encode()).hexdigest()
            
            # Validate rights
            valid_rights = []
            for right in rights:
                try:
                    valid_rights.append(AccessRight(right))
                except ValueError:
                    return {'success': False, 'error': f'Invalid access right: {right}'}
            
            # Parse expiry date if provided
            expiry_datetime = None
            if expiry_date:
                expiry_datetime = datetime.fromisoformat(expiry_date)
            
            license_obj = ContentLicense(
                license_id=license_id,
                content_id=content_id,
                user_id=user_id,
                rights=valid_rights,
                expiry_date=expiry_datetime,
                max_views=max_views,
                max_downloads=max_downloads,
                geographic_restrictions=geographic_restrictions or [],
                device_restrictions=device_restrictions or [],
                created_at=datetime.utcnow(),
                protection_level=ProtectionLevel[protection_level.upper()]
            )
            
            # Store license
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO content_licenses
                (license_id, content_id, user_id, rights, expiry_date, max_views,
                 max_downloads, geographic_restrictions, device_restrictions,
                 created_at, protection_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                license_obj.license_id,
                license_obj.content_id,
                license_obj.user_id,
                json.dumps([right.value for right in license_obj.rights]),
                license_obj.expiry_date,
                license_obj.max_views,
                license_obj.max_downloads,
                json.dumps(license_obj.geographic_restrictions),
                json.dumps(license_obj.device_restrictions),
                license_obj.created_at,
                license_obj.protection_level.value
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'license_id': license_id,
                'message': 'License created successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def apply_watermark(self, content_id: str, watermark_config: Dict) -> Dict:
        """Apply watermark to protected content"""
        try:
            # Get content info
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT protected_filename, content_type, protection_level
                FROM protected_content WHERE content_id = ?
            ''', (content_id,))
            
            content_info = cursor.fetchone()
            if not content_info:
                return {'success': False, 'error': 'Content not found'}
            
            protected_filename, content_type, protection_level = content_info
            
            # Generate watermark ID
            watermark_id = hashlib.md5(f"{content_id}_{time.time()}".encode()).hexdigest()
            
            # Create watermark configuration
            watermark = WatermarkConfig(
                watermark_id=watermark_id,
                watermark_type=WatermarkType(watermark_config.get('type', 'visible')),
                content=watermark_config.get('content', 'PROTECTED'),
                position=watermark_config.get('position', 'bottom-right'),
                opacity=watermark_config.get('opacity', 0.5),
                size=(watermark_config.get('width', 200), watermark_config.get('height', 50)),
                font_size=watermark_config.get('font_size', 24),
                color=watermark_config.get('color', '#FFFFFF'),
                rotation=watermark_config.get('rotation', 0)
            )
            
            # Apply watermark based on content type
            if content_type.startswith('image/'):
                result = self._apply_image_watermark(content_id, protected_filename, watermark)
            elif content_type.startswith('video/'):
                result = self._apply_video_watermark(content_id, protected_filename, watermark)
            else:
                return {'success': False, 'error': 'Unsupported content type for watermarking'}
            
            if result['success']:
                # Store watermark config
                cursor.execute('''
                    INSERT INTO watermark_configs
                    (watermark_id, content_id, watermark_type, content, position,
                     opacity, size_width, size_height, font_size, color, rotation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    watermark.watermark_id,
                    content_id,
                    watermark.watermark_type.value,
                    watermark.content,
                    watermark.position,
                    watermark.opacity,
                    watermark.size[0],
                    watermark.size[1],
                    watermark.font_size,
                    watermark.color,
                    watermark.rotation
                ))
                
                # Update content as watermarked
                cursor.execute('''
                    UPDATE protected_content
                    SET watermark_applied = TRUE
                    WHERE content_id = ?
                ''', (content_id,))
                
                conn.commit()
            
            conn.close()
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_image_watermark(self, content_id: str, protected_filename: str, 
                              watermark: WatermarkConfig) -> Dict:
        """Apply watermark to image content"""
        try:
            image_path = os.path.join(self.content_storage_path, protected_filename)
            
            # Open image
            with Image.open(image_path) as img:
                # Create watermark overlay
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)
                
                # Calculate position
                text = watermark.content
                position = self._calculate_watermark_position(watermark.position, img.size, watermark.size)
                
                # Apply watermark based on type
                if watermark.watermark_type == WatermarkType.VISIBLE:
                    # Draw text watermark
                    try:
                        font = ImageFont.truetype("arial.ttf", watermark.font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Convert color
                    color = tuple(int(watermark.color[i:i+2], 16) for i in (1, 3, 5))
                    color_with_alpha = color + (int(255 * watermark.opacity),)
                    
                    draw.text(position, text, font=font, fill=color_with_alpha)
                
                elif watermark.watermark_type == WatermarkType.INVISIBLE:
                    # LSB steganography for invisible watermark
                    self._apply_lsb_watermark(img, text)
                
                # Composite images
                if watermark.watermark_type == WatermarkType.VISIBLE:
                    watermarked = Image.alpha_composite(img.convert('RGBA'), overlay)
                    watermarked = watermarked.convert('RGB')
                else:
                    watermarked = img
                
                # Save watermarked image
                watermarked_path = os.path.join(self.watermark_storage_path, f"{content_id}_watermarked.jpg")
                watermarked.save(watermarked_path, 'JPEG', quality=95)
                
                # Replace original protected file
                os.replace(watermarked_path, image_path)
            
            return {
                'success': True,
                'watermark_id': watermark.watermark_id,
                'message': 'Image watermark applied successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_video_watermark(self, content_id: str, protected_filename: str,
                              watermark: WatermarkConfig) -> Dict:
        """Apply watermark to video content (placeholder)"""
        # In a real implementation, this would use FFmpeg or similar
        # For now, just return success
        return {
            'success': True,
            'watermark_id': watermark.watermark_id,
            'message': 'Video watermarking not implemented in this demo'
        }
    
    def _apply_lsb_watermark(self, image: Image, text: str):
        """Apply LSB steganography watermark"""
        # Convert text to binary
        binary_text = ''.join(format(ord(char), '08b') for char in text)
        binary_text += '1111111111111110'  # Delimiter
        
        pixels = list(image.getdata())
        
        # Modify LSB of red channel
        for i, bit in enumerate(binary_text):
            if i < len(pixels):
                r, g, b = pixels[i][:3]  # Get RGB values
                r = (r & 0xFE) | int(bit)  # Modify LSB
                pixels[i] = (r, g, b) + pixels[i][3:]  # Keep alpha if present
        
        # Update image data
        image.putdata(pixels)
    
    def _calculate_watermark_position(self, position: str, image_size: Tuple[int, int],
                                    watermark_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate watermark position coordinates"""
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        positions = {
            'top-left': (10, 10),
            'top-right': (img_width - wm_width - 10, 10),
            'bottom-left': (10, img_height - wm_height - 10),
            'bottom-right': (img_width - wm_width - 10, img_height - wm_height - 10),
            'center': ((img_width - wm_width) // 2, (img_height - wm_height) // 2)
        }
        
        return positions.get(position, positions['bottom-right'])
    
    def check_access_rights(self, content_id: str, user_id: str, access_type: str,
                           ip_address: str = None, device_info: str = None) -> Dict:
        """Check if user has rights to access content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get active license
            cursor.execute('''
                SELECT license_id, rights, expiry_date, max_views, max_downloads,
                       current_views, current_downloads, geographic_restrictions,
                       device_restrictions, status
                FROM content_licenses
                WHERE content_id = ? AND user_id = ? AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            ''', (content_id, user_id))
            
            license_data = cursor.fetchone()
            if not license_data:
                return {'success': False, 'error': 'No valid license found'}
            
            (license_id, rights_json, expiry_date, max_views, max_downloads,
             current_views, current_downloads, geo_restrictions, device_restrictions,
             status) = license_data
            
            # Parse rights
            rights = json.loads(rights_json)
            
            # Check if access type is allowed
            if access_type not in rights:
                return {'success': False, 'error': f'Access type {access_type} not permitted'}
            
            # Check expiry
            if expiry_date:
                expiry_dt = datetime.fromisoformat(expiry_date)
                if datetime.utcnow() > expiry_dt:
                    return {'success': False, 'error': 'License has expired'}
            
            # Check usage limits
            if access_type == 'view' and max_views and current_views >= max_views:
                return {'success': False, 'error': 'View limit exceeded'}
            
            if access_type == 'download' and max_downloads and current_downloads >= max_downloads:
                return {'success': False, 'error': 'Download limit exceeded'}
            
            # Check geographic restrictions
            if geo_restrictions:
                geo_list = json.loads(geo_restrictions)
                # This would integrate with geolocation service
                # For now, just allow all
            
            # Check device restrictions
            if device_restrictions:
                device_list = json.loads(device_restrictions)
                # This would check device fingerprinting
                # For now, just allow all
            
            conn.close()
            
            return {
                'success': True,
                'license_id': license_id,
                'access_granted': True,
                'remaining_views': max_views - current_views if max_views else None,
                'remaining_downloads': max_downloads - current_downloads if max_downloads else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def log_access(self, content_id: str, user_id: str, access_type: str,
                   success: bool, ip_address: str = None, device_info: str = None,
                   session_id: str = None, metadata: Dict = None) -> Dict:
        """Log content access attempt"""
        try:
            access_id = hashlib.sha256(f"{content_id}_{user_id}_{time.time()}".encode()).hexdigest()
            
            access_log = AccessLog(
                access_id=access_id,
                content_id=content_id,
                user_id=user_id,
                access_type=AccessRight(access_type),
                timestamp=datetime.utcnow(),
                ip_address=ip_address or '',
                device_info=device_info or '',
                session_id=session_id or '',
                success=success,
                metadata=metadata or {}
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs
                (access_id, content_id, user_id, access_type, timestamp,
                 ip_address, device_info, session_id, success, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                access_log.access_id,
                access_log.content_id,
                access_log.user_id,
                access_log.access_type.value,
                access_log.timestamp,
                access_log.ip_address,
                access_log.device_info,
                access_log.session_id,
                access_log.success,
                json.dumps(access_log.metadata)
            ))
            
            # Update usage counters if successful
            if success:
                if access_type == 'view':
                    cursor.execute('''
                        UPDATE content_licenses
                        SET current_views = current_views + 1
                        WHERE content_id = ? AND user_id = ?
                    ''', (content_id, user_id))
                elif access_type == 'download':
                    cursor.execute('''
                        UPDATE content_licenses
                        SET current_downloads = current_downloads + 1
                        WHERE content_id = ? AND user_id = ?
                    ''', (content_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'access_id': access_id,
                'logged_at': access_log.timestamp.isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_content_type(self, file_extension: str) -> str:
        """Determine content type from file extension"""
        content_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    def get_drm_status(self) -> Dict:
        """Get overall DRM system status and statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Protected content count
            cursor.execute('SELECT COUNT(*) FROM protected_content')
            total_protected_content = cursor.fetchone()[0]
            
            # Active licenses count
            cursor.execute('SELECT COUNT(*) FROM content_licenses WHERE status = "active"')
            active_licenses = cursor.fetchone()[0]
            
            # Watermarked content count
            cursor.execute('SELECT COUNT(*) FROM protected_content WHERE watermark_applied = TRUE')
            watermarked_content = cursor.fetchone()[0]
            
            # Access attempts today
            cursor.execute('''
                SELECT COUNT(*) FROM access_logs
                WHERE DATE(timestamp) = DATE('now')
            ''')
            todays_access_attempts = cursor.fetchone()[0]
            
            # Protection level distribution
            cursor.execute('''
                SELECT protection_level, COUNT(*)
                FROM protected_content
                GROUP BY protection_level
            ''')
            protection_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_protected_content': total_protected_content,
                'active_licenses': active_licenses,
                'watermarked_content': watermarked_content,
                'todays_access_attempts': todays_access_attempts,
                'protection_level_distribution': protection_distribution,
                'system_status': 'operational',
                'storage_paths': {
                    'content': self.content_storage_path,
                    'watermarks': self.watermark_storage_path
                }
            }
            
        except Exception as e:
            return {'error': str(e)}