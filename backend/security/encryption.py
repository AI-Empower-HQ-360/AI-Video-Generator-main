"""
Content Encryption at Rest and in Transit
Enterprise-grade encryption for data protection
"""

import os
import base64
import secrets
import hashlib
from typing import Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
import sqlite3
import json


class KeyManager:
    """Secure key management for encryption operations"""
    
    def __init__(self, key_storage_path: str = "/tmp/keys"):
        self.key_storage_path = key_storage_path
        self.master_key = None
        self._ensure_key_storage()
        self._initialize_master_key()
    
    def _ensure_key_storage(self):
        """Ensure key storage directory exists"""
        os.makedirs(self.key_storage_path, exist_ok=True)
        # Set restrictive permissions
        os.chmod(self.key_storage_path, 0o700)
    
    def _initialize_master_key(self):
        """Initialize or load master key"""
        master_key_path = os.path.join(self.key_storage_path, "master.key")
        
        if os.path.exists(master_key_path):
            with open(master_key_path, 'rb') as f:
                self.master_key = f.read()
        else:
            # Generate new master key
            self.master_key = secrets.token_bytes(32)
            with open(master_key_path, 'wb') as f:
                f.write(self.master_key)
            os.chmod(master_key_path, 0o600)
    
    def generate_data_key(self, key_id: str) -> bytes:
        """Generate a new data encryption key"""
        data_key = secrets.token_bytes(32)
        encrypted_key = self._encrypt_with_master_key(data_key)
        
        # Store encrypted data key
        key_path = os.path.join(self.key_storage_path, f"{key_id}.key")
        with open(key_path, 'wb') as f:
            f.write(encrypted_key)
        os.chmod(key_path, 0o600)
        
        return data_key
    
    def get_data_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve and decrypt a data encryption key"""
        key_path = os.path.join(self.key_storage_path, f"{key_id}.key")
        
        if not os.path.exists(key_path):
            return None
        
        with open(key_path, 'rb') as f:
            encrypted_key = f.read()
        
        return self._decrypt_with_master_key(encrypted_key)
    
    def _encrypt_with_master_key(self, data: bytes) -> bytes:
        """Encrypt data with master key using Fernet"""
        fernet_key = base64.urlsafe_b64encode(self.master_key)
        f = Fernet(fernet_key)
        return f.encrypt(data)
    
    def _decrypt_with_master_key(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with master key using Fernet"""
        fernet_key = base64.urlsafe_b64encode(self.master_key)
        f = Fernet(fernet_key)
        return f.decrypt(encrypted_data)
    
    def rotate_master_key(self) -> bool:
        """Rotate the master key and re-encrypt all data keys"""
        try:
            old_master_key = self.master_key
            new_master_key = secrets.token_bytes(32)
            
            # Re-encrypt all data keys with new master key
            for filename in os.listdir(self.key_storage_path):
                if filename.endswith('.key') and filename != 'master.key':
                    key_path = os.path.join(self.key_storage_path, filename)
                    
                    # Decrypt with old key
                    with open(key_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    old_fernet_key = base64.urlsafe_b64encode(old_master_key)
                    old_f = Fernet(old_fernet_key)
                    data_key = old_f.decrypt(encrypted_data)
                    
                    # Encrypt with new key
                    new_fernet_key = base64.urlsafe_b64encode(new_master_key)
                    new_f = Fernet(new_fernet_key)
                    new_encrypted_data = new_f.encrypt(data_key)
                    
                    # Write back
                    with open(key_path, 'wb') as f:
                        f.write(new_encrypted_data)
            
            # Update master key
            self.master_key = new_master_key
            master_key_path = os.path.join(self.key_storage_path, "master.key")
            with open(master_key_path, 'wb') as f:
                f.write(self.master_key)
            
            return True
        except Exception as e:
            print(f"Key rotation failed: {e}")
            return False


class EncryptionManager:
    """Main encryption manager for content protection"""
    
    def __init__(self, config: Dict):
        self.key_manager = KeyManager(config.get('key_storage_path', '/tmp/keys'))
        self.default_algorithm = config.get('algorithm', 'AES-256-GCM')
        self.encryption_metadata = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize encryption metadata database"""
        self.db_path = "/tmp/encryption_metadata.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_metadata (
                content_id TEXT PRIMARY KEY,
                key_id TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                iv BLOB NOT NULL,
                encrypted_at TIMESTAMP NOT NULL,
                content_type TEXT,
                file_size INTEGER,
                checksum TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def encrypt_content(self, content: Union[str, bytes], content_id: str, content_type: str = "text") -> Dict:
        """Encrypt content and store metadata"""
        try:
            # Convert string to bytes if necessary
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Generate unique key for this content
            key_id = f"content_{content_id}_{int(datetime.utcnow().timestamp())}"
            encryption_key = self.key_manager.generate_data_key(key_id)
            
            # Generate random IV
            iv = secrets.token_bytes(16)
            
            # Encrypt using AES-GCM
            cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(content_bytes) + encryptor.finalize()
            auth_tag = encryptor.tag
            
            # Combine ciphertext and auth tag
            encrypted_data = ciphertext + auth_tag
            
            # Calculate checksum of original content
            checksum = hashlib.sha256(content_bytes).hexdigest()
            
            # Store metadata
            self._store_encryption_metadata({
                'content_id': content_id,
                'key_id': key_id,
                'algorithm': 'AES-256-GCM',
                'iv': iv,
                'encrypted_at': datetime.utcnow(),
                'content_type': content_type,
                'file_size': len(content_bytes),
                'checksum': checksum
            })
            
            return {
                'success': True,
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'content_id': content_id,
                'key_id': key_id,
                'iv': base64.b64encode(iv).decode(),
                'checksum': checksum
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def decrypt_content(self, content_id: str, encrypted_data: str = None) -> Dict:
        """Decrypt content using stored metadata"""
        try:
            # Get encryption metadata
            metadata = self._get_encryption_metadata(content_id)
            if not metadata:
                return {'success': False, 'error': 'Encryption metadata not found'}
            
            # Get decryption key
            decryption_key = self.key_manager.get_data_key(metadata['key_id'])
            if not decryption_key:
                return {'success': False, 'error': 'Decryption key not found'}
            
            # Decode encrypted data if provided as base64
            if encrypted_data:
                encrypted_bytes = base64.b64decode(encrypted_data)
            else:
                return {'success': False, 'error': 'Encrypted data required'}
            
            # Extract ciphertext and auth tag
            ciphertext = encrypted_bytes[:-16]
            auth_tag = encrypted_bytes[-16:]
            
            # Decrypt using AES-GCM
            cipher = Cipher(algorithms.AES(decryption_key), modes.GCM(metadata['iv'], auth_tag))
            decryptor = cipher.decryptor()
            decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Verify checksum
            actual_checksum = hashlib.sha256(decrypted_bytes).hexdigest()
            if actual_checksum != metadata['checksum']:
                return {'success': False, 'error': 'Checksum verification failed'}
            
            # Convert to string if it was originally text
            if metadata['content_type'] == 'text':
                decrypted_content = decrypted_bytes.decode('utf-8')
            else:
                decrypted_content = decrypted_bytes
            
            return {
                'success': True,
                'content': decrypted_content,
                'content_type': metadata['content_type'],
                'decrypted_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def encrypt_file(self, file_path: str, content_id: str) -> Dict:
        """Encrypt a file and return encrypted content"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_extension = os.path.splitext(file_path)[1]
            content_type = f"file{file_extension}"
            
            return self.encrypt_content(file_content, content_id, content_type)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def decrypt_to_file(self, content_id: str, encrypted_data: str, output_path: str) -> Dict:
        """Decrypt content and save to file"""
        try:
            result = self.decrypt_content(content_id, encrypted_data)
            if not result['success']:
                return result
            
            with open(output_path, 'wb') as f:
                if isinstance(result['content'], str):
                    f.write(result['content'].encode('utf-8'))
                else:
                    f.write(result['content'])
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'File decrypted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _store_encryption_metadata(self, metadata: Dict):
        """Store encryption metadata in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO encryption_metadata
            (content_id, key_id, algorithm, iv, encrypted_at, content_type, file_size, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata['content_id'],
            metadata['key_id'],
            metadata['algorithm'],
            metadata['iv'],
            metadata['encrypted_at'],
            metadata['content_type'],
            metadata['file_size'],
            metadata['checksum']
        ))
        
        conn.commit()
        conn.close()
    
    def _get_encryption_metadata(self, content_id: str) -> Optional[Dict]:
        """Retrieve encryption metadata from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT key_id, algorithm, iv, encrypted_at, content_type, file_size, checksum
            FROM encryption_metadata WHERE content_id = ?
        ''', (content_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'key_id': result[0],
                'algorithm': result[1],
                'iv': result[2],
                'encrypted_at': result[3],
                'content_type': result[4],
                'file_size': result[5],
                'checksum': result[6]
            }
        
        return None
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """Generate RSA public/private key pair for asymmetric encryption"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def encrypt_with_public_key(self, data: bytes, public_key_pem: bytes) -> bytes:
        """Encrypt data using RSA public key"""
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        encrypted_data = public_key.encrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_data
    
    def decrypt_with_private_key(self, encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """Decrypt data using RSA private key"""
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        
        decrypted_data = private_key.decrypt(
            encrypted_data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted_data
    
    def secure_delete_content(self, content_id: str) -> Dict:
        """Securely delete encrypted content and its metadata"""
        try:
            # Get metadata
            metadata = self._get_encryption_metadata(content_id)
            if not metadata:
                return {'success': False, 'error': 'Content not found'}
            
            # Delete encryption key
            key_path = os.path.join(self.key_manager.key_storage_path, f"{metadata['key_id']}.key")
            if os.path.exists(key_path):
                # Overwrite file with random data before deletion
                with open(key_path, 'rb+') as f:
                    file_size = os.path.getsize(key_path)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                os.remove(key_path)
            
            # Delete metadata
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM encryption_metadata WHERE content_id = ?', (content_id,))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Content {content_id} securely deleted'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_encryption_status(self) -> Dict:
        """Get overall encryption system status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM encryption_metadata')
            total_encrypted_items = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(file_size) FROM encryption_metadata')
            total_encrypted_size = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT algorithm, COUNT(*) 
                FROM encryption_metadata 
                GROUP BY algorithm
            ''')
            algorithm_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_encrypted_items': total_encrypted_items,
                'total_encrypted_size_bytes': total_encrypted_size,
                'algorithm_distribution': algorithm_stats,
                'key_storage_path': self.key_manager.key_storage_path,
                'master_key_status': 'active' if self.key_manager.master_key else 'missing'
            }
            
        except Exception as e:
            return {'error': str(e)}