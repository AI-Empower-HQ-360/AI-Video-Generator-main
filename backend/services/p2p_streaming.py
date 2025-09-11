"""
Peer-to-Peer Video Sharing and Streaming Service
Enables direct video sharing between users without central server
"""
import asyncio
import json
import time
import uuid
import hashlib
import socket
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path

from config.edge_config import edge_config


@dataclass
class PeerInfo:
    """Information about a peer in the P2P network"""
    peer_id: str
    display_name: str
    ip_address: str
    port: int
    supported_protocols: List[str]
    available_videos: List[str]
    bandwidth_mbps: float
    last_seen: float
    status: str = 'online'  # online, offline, busy, away


@dataclass
class VideoShare:
    """Represents a shared video in the P2P network"""
    share_id: str
    video_id: str
    filename: str
    file_size: int
    file_hash: str
    owner_peer_id: str
    title: str
    description: str
    duration: float
    resolution: str
    bitrate: int
    created_at: float
    permissions: Dict[str, Any]  # access control
    download_count: int = 0
    stream_count: int = 0


@dataclass
class StreamSession:
    """Represents an active streaming session"""
    session_id: str
    video_share_id: str
    streamer_peer_id: str
    viewer_peer_id: str
    protocol: str  # 'webrtc', 'websocket', 'direct'
    quality: str  # 'low', 'medium', 'high', 'adaptive'
    start_time: float
    last_activity: float
    bytes_transferred: int = 0
    status: str = 'active'  # active, paused, ended, error


class P2PDiscoveryService:
    """Handles peer discovery in the P2P network"""
    
    def __init__(self):
        self.local_peer = None
        self.known_peers: Dict[str, PeerInfo] = {}
        self.discovery_socket = None
        self.discovery_running = False
        self.port_range = edge_config.get_p2p_config()['port_range']
    
    async def initialize_peer(self, display_name: str) -> PeerInfo:
        """Initialize local peer"""
        peer_id = str(uuid.uuid4())
        
        # Find available port
        port = await self._find_available_port()
        
        # Get local IP
        ip_address = self._get_local_ip()
        
        self.local_peer = PeerInfo(
            peer_id=peer_id,
            display_name=display_name,
            ip_address=ip_address,
            port=port,
            supported_protocols=['websocket', 'webrtc'],
            available_videos=[],
            bandwidth_mbps=100.0,  # Estimate
            last_seen=time.time(),
            status='online'
        )
        
        return self.local_peer
    
    async def _find_available_port(self) -> int:
        """Find an available port in the configured range"""
        start_port, end_port = self.port_range
        
        for port in range(start_port, end_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        
        raise Exception("No available ports in configured range")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to get local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    async def start_discovery(self):
        """Start peer discovery service"""
        if self.discovery_running:
            return
        
        self.discovery_running = True
        
        # Start UDP broadcast for peer discovery
        asyncio.create_task(self._discovery_broadcast_loop())
        asyncio.create_task(self._discovery_listen_loop())
    
    async def stop_discovery(self):
        """Stop peer discovery service"""
        self.discovery_running = False
        
        if self.discovery_socket:
            self.discovery_socket.close()
    
    async def _discovery_broadcast_loop(self):
        """Broadcast peer presence periodically"""
        while self.discovery_running:
            try:
                await self._broadcast_presence()
                await asyncio.sleep(30)  # Broadcast every 30 seconds
            except Exception as e:
                print(f"Discovery broadcast error: {e}")
                await asyncio.sleep(5)
    
    async def _discovery_listen_loop(self):
        """Listen for peer discovery messages"""
        try:
            # Create UDP socket for listening
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_socket.bind(('', 9999))  # Discovery port
            self.discovery_socket.settimeout(1.0)
            
            while self.discovery_running:
                try:
                    data, addr = self.discovery_socket.recvfrom(1024)
                    await self._handle_discovery_message(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Discovery listen error: {e}")
                    
        except Exception as e:
            print(f"Failed to start discovery listener: {e}")
    
    async def _broadcast_presence(self):
        """Broadcast local peer presence"""
        if not self.local_peer:
            return
        
        message = {
            'type': 'peer_announcement',
            'peer': asdict(self.local_peer),
            'timestamp': time.time()
        }
        
        try:
            # Broadcast to local network
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                data = json.dumps(message).encode()
                s.sendto(data, ('<broadcast>', 9999))
        except Exception as e:
            print(f"Broadcast error: {e}")
    
    async def _handle_discovery_message(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming discovery message"""
        try:
            message = json.loads(data.decode())
            
            if message['type'] == 'peer_announcement':
                peer_data = message['peer']
                
                # Don't add ourselves
                if peer_data['peer_id'] == self.local_peer.peer_id:
                    return
                
                # Update peer info
                peer = PeerInfo(**peer_data)
                peer.last_seen = time.time()
                self.known_peers[peer.peer_id] = peer
                
        except Exception as e:
            print(f"Error handling discovery message: {e}")
    
    def get_known_peers(self) -> List[PeerInfo]:
        """Get list of known peers"""
        current_time = time.time()
        active_peers = []
        
        for peer in self.known_peers.values():
            # Remove peers not seen for 2 minutes
            if current_time - peer.last_seen < 120:
                active_peers.append(peer)
        
        return active_peers
    
    def get_peer(self, peer_id: str) -> Optional[PeerInfo]:
        """Get specific peer by ID"""
        return self.known_peers.get(peer_id)


class P2PVideoSharingService:
    """Manages P2P video sharing"""
    
    def __init__(self):
        self.discovery_service = P2PDiscoveryService()
        self.shared_videos: Dict[str, VideoShare] = {}
        self.active_streams: Dict[str, StreamSession] = {}
        self.download_sessions: Dict[str, Dict] = {}
    
    async def initialize(self, display_name: str):
        """Initialize P2P service"""
        await self.discovery_service.initialize_peer(display_name)
        await self.discovery_service.start_discovery()
    
    async def share_video(self, video_path: str, title: str, description: str = "",
                         permissions: Dict[str, Any] = None) -> VideoShare:
        """Share a video in the P2P network"""
        # Calculate file hash for integrity verification
        file_hash = await self._calculate_file_hash(video_path)
        file_size = Path(video_path).stat().st_size
        
        # Get video metadata (simplified)
        video_metadata = await self._get_video_metadata(video_path)
        
        share_id = str(uuid.uuid4())
        video_id = str(uuid.uuid4())
        
        video_share = VideoShare(
            share_id=share_id,
            video_id=video_id,
            filename=Path(video_path).name,
            file_size=file_size,
            file_hash=file_hash,
            owner_peer_id=self.discovery_service.local_peer.peer_id,
            title=title,
            description=description,
            duration=video_metadata.get('duration', 0),
            resolution=video_metadata.get('resolution', 'unknown'),
            bitrate=video_metadata.get('bitrate', 0),
            created_at=time.time(),
            permissions=permissions or {'public': True}
        )
        
        self.shared_videos[share_id] = video_share
        
        # Update local peer's available videos
        self.discovery_service.local_peer.available_videos.append(share_id)
        
        return video_share
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        import subprocess
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Extract video stream info
                video_stream = next(
                    (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
                    {}
                )
                
                format_info = data.get('format', {})
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'codec': video_stream.get('codec_name', 'unknown')
                }
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting video metadata: {e}")
            return {}
    
    def get_available_videos(self) -> List[VideoShare]:
        """Get list of videos available from all peers"""
        available_videos = []
        
        # Add local shared videos
        available_videos.extend(self.shared_videos.values())
        
        # TODO: Query remote peers for their available videos
        # This would involve sending requests to known peers
        
        return available_videos
    
    async def start_video_stream(self, share_id: str, viewer_peer_id: str,
                                quality: str = 'medium') -> Optional[StreamSession]:
        """Start streaming a video to a peer"""
        video_share = self.shared_videos.get(share_id)
        if not video_share:
            return None
        
        # Check permissions
        if not self._check_stream_permission(video_share, viewer_peer_id):
            return None
        
        session_id = str(uuid.uuid4())
        
        stream_session = StreamSession(
            session_id=session_id,
            video_share_id=share_id,
            streamer_peer_id=self.discovery_service.local_peer.peer_id,
            viewer_peer_id=viewer_peer_id,
            protocol='websocket',  # Default protocol
            quality=quality,
            start_time=time.time(),
            last_activity=time.time()
        )
        
        self.active_streams[session_id] = stream_session
        video_share.stream_count += 1
        
        # Start actual streaming (simplified)
        asyncio.create_task(self._handle_video_streaming(stream_session))
        
        return stream_session
    
    def _check_stream_permission(self, video_share: VideoShare, viewer_peer_id: str) -> bool:
        """Check if peer has permission to stream video"""
        permissions = video_share.permissions
        
        if permissions.get('public', False):
            return True
        
        allowed_peers = permissions.get('allowed_peers', [])
        return viewer_peer_id in allowed_peers
    
    async def _handle_video_streaming(self, session: StreamSession):
        """Handle video streaming session"""
        try:
            # This is a simplified implementation
            # In a real system, this would:
            # 1. Set up WebRTC or WebSocket connection
            # 2. Stream video chunks
            # 3. Handle quality adaptation
            # 4. Manage bandwidth
            
            # Simulate streaming
            video_share = self.shared_videos[session.video_share_id]
            total_size = video_share.file_size
            chunk_size = 64 * 1024  # 64KB chunks
            
            bytes_sent = 0
            while bytes_sent < total_size and session.status == 'active':
                # Simulate sending chunk
                await asyncio.sleep(0.1)  # Simulate network delay
                
                bytes_sent += chunk_size
                session.bytes_transferred = bytes_sent
                session.last_activity = time.time()
            
            session.status = 'ended'
            
        except Exception as e:
            print(f"Streaming error: {e}")
            session.status = 'error'
    
    async def request_video_download(self, share_id: str, peer_id: str) -> Optional[str]:
        """Request to download a video from a peer"""
        # Find peer
        peer = self.discovery_service.get_peer(peer_id)
        if not peer:
            return None
        
        # TODO: Implement actual P2P download protocol
        # This would involve:
        # 1. Connecting to peer
        # 2. Requesting video chunks
        # 3. Verifying integrity
        # 4. Assembling final file
        
        # For now, return a simulated download ID
        download_id = str(uuid.uuid4())
        
        self.download_sessions[download_id] = {
            'share_id': share_id,
            'peer_id': peer_id,
            'status': 'downloading',
            'progress': 0.0,
            'started_at': time.time()
        }
        
        # Start download simulation
        asyncio.create_task(self._simulate_download(download_id))
        
        return download_id
    
    async def _simulate_download(self, download_id: str):
        """Simulate video download progress"""
        session = self.download_sessions[download_id]
        
        try:
            # Simulate download progress
            for progress in range(0, 101, 5):
                await asyncio.sleep(0.5)
                session['progress'] = progress
                
                if session['status'] != 'downloading':
                    break
            
            if session['status'] == 'downloading':
                session['status'] = 'completed'
                session['completed_at'] = time.time()
                
        except Exception as e:
            session['status'] = 'error'
            session['error'] = str(e)
    
    def get_stream_sessions(self) -> List[StreamSession]:
        """Get list of active stream sessions"""
        return list(self.active_streams.values())
    
    def get_download_progress(self, download_id: str) -> Optional[Dict]:
        """Get download progress"""
        return self.download_sessions.get(download_id)
    
    def stop_stream(self, session_id: str) -> bool:
        """Stop a streaming session"""
        if session_id in self.active_streams:
            self.active_streams[session_id].status = 'ended'
            return True
        return False
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get P2P network statistics"""
        known_peers = self.discovery_service.get_known_peers()
        
        total_shared_videos = len(self.shared_videos)
        total_streams = len([s for s in self.active_streams.values() if s.status == 'active'])
        total_downloads = len([d for d in self.download_sessions.values() if d['status'] == 'downloading'])
        
        return {
            'local_peer': asdict(self.discovery_service.local_peer) if self.discovery_service.local_peer else None,
            'known_peers_count': len(known_peers),
            'known_peers': [asdict(peer) for peer in known_peers],
            'shared_videos_count': total_shared_videos,
            'active_streams_count': total_streams,
            'active_downloads_count': total_downloads,
            'total_bytes_shared': sum(s.bytes_transferred for s in self.active_streams.values()),
            'network_status': 'connected' if known_peers else 'isolated'
        }


# Global P2P service instance
p2p_service = P2PVideoSharingService()