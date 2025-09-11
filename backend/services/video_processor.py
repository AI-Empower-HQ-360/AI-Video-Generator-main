"""
Video Processing Service
Handles video processing with GPU acceleration and distributed computing
"""
import asyncio
import json
import os
import subprocess
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from config.edge_config import edge_config


@dataclass
class VideoProcessingTask:
    """Represents a video processing task"""
    task_id: str
    operation: str  # 'transcode', 'enhance', 'edit', 'render', 'analyze'
    input_file: str
    output_file: str
    parameters: Dict[str, Any]
    node_id: Optional[str] = None
    status: str = 'pending'  # pending, processing, completed, failed, cancelled
    progress: float = 0.0
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    gpu_accelerated: bool = False
    chunk_info: Optional[Dict] = None


class GPUAccelerator:
    """Handles GPU acceleration for video processing"""
    
    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
        self.gpu_devices = self._detect_gpu_devices()
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            # Check for NVIDIA GPU
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        try:
            # Check for AMD GPU (placeholder for future implementation)
            # Could add ROCm/OpenCL detection here
            pass
        except:
            pass
        
        return False
    
    def _detect_gpu_devices(self) -> List[Dict]:
        """Detect available GPU devices"""
        devices = []
        
        if not self.gpu_available:
            return devices
        
        try:
            # Get NVIDIA GPU info
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=index,name,memory.total,memory.used',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(', ')
                        if len(parts) >= 4:
                            devices.append({
                                'index': int(parts[0]),
                                'name': parts[1],
                                'memory_total': int(parts[2]),
                                'memory_used': int(parts[3]),
                                'memory_available': int(parts[2]) - int(parts[3]),
                                'type': 'nvidia'
                            })
        except Exception as e:
            print(f"Error detecting GPU devices: {e}")
        
        return devices
    
    def get_optimal_device(self, memory_required: int = 1024) -> Optional[Dict]:
        """Get the optimal GPU device for processing"""
        if not self.gpu_available or not self.gpu_devices:
            return None
        
        # Find device with enough memory
        suitable_devices = [
            device for device in self.gpu_devices
            if device['memory_available'] >= memory_required
        ]
        
        if not suitable_devices:
            return None
        
        # Return device with most available memory
        return max(suitable_devices, key=lambda d: d['memory_available'])
    
    def get_ffmpeg_gpu_args(self, device: Dict = None) -> List[str]:
        """Get FFmpeg arguments for GPU acceleration"""
        if not device:
            device = self.get_optimal_device()
        
        if not device:
            return []
        
        if device['type'] == 'nvidia':
            return [
                '-hwaccel', 'cuda',
                '-hwaccel_output_format', 'cuda',
                '-gpu', str(device['index'])
            ]
        
        return []


class VideoProcessor:
    """Main video processing engine"""
    
    def __init__(self):
        self.gpu_accelerator = GPUAccelerator()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.active_tasks: Dict[str, VideoProcessingTask] = {}
        self.task_callbacks: Dict[str, List[Callable]] = {}
    
    def add_task_callback(self, task_id: str, callback: Callable):
        """Add a callback for task progress updates"""
        if task_id not in self.task_callbacks:
            self.task_callbacks[task_id] = []
        self.task_callbacks[task_id].append(callback)
    
    def _notify_progress(self, task_id: str, progress: float, status: str = None):
        """Notify callbacks about task progress"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].progress = progress
            if status:
                self.active_tasks[task_id].status = status
        
        if task_id in self.task_callbacks:
            for callback in self.task_callbacks[task_id]:
                try:
                    callback(task_id, progress, status)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    async def create_task(self, operation: str, input_file: str, output_file: str, 
                         parameters: Dict[str, Any]) -> VideoProcessingTask:
        """Create a new video processing task"""
        task_id = str(uuid.uuid4())
        
        task = VideoProcessingTask(
            task_id=task_id,
            operation=operation,
            input_file=input_file,
            output_file=output_file,
            parameters=parameters,
            status='pending',
            created_at=time.time(),
            gpu_accelerated=edge_config.enable_gpu_acceleration and self.gpu_accelerator.gpu_available
        )
        
        self.active_tasks[task_id] = task
        return task
    
    async def process_video(self, task: VideoProcessingTask) -> bool:
        """Process video based on task parameters"""
        try:
            task.status = 'processing'
            task.started_at = time.time()
            self._notify_progress(task.task_id, 0.0, 'processing')
            
            if task.operation == 'transcode':
                success = await self._transcode_video(task)
            elif task.operation == 'enhance':
                success = await self._enhance_video(task)
            elif task.operation == 'edit':
                success = await self._edit_video(task)
            elif task.operation == 'render':
                success = await self._render_video(task)
            elif task.operation == 'analyze':
                success = await self._analyze_video(task)
            else:
                raise ValueError(f"Unknown operation: {task.operation}")
            
            if success:
                task.status = 'completed'
                task.completed_at = time.time()
                self._notify_progress(task.task_id, 100.0, 'completed')
            else:
                task.status = 'failed'
                task.error_message = "Processing failed"
                self._notify_progress(task.task_id, task.progress, 'failed')
            
            return success
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            self._notify_progress(task.task_id, task.progress, 'failed')
            return False
    
    async def _transcode_video(self, task: VideoProcessingTask) -> bool:
        """Transcode video to different format/quality"""
        params = task.parameters
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-i', task.input_file]
        
        # Add GPU acceleration if available
        if task.gpu_accelerated:
            gpu_device = self.gpu_accelerator.get_optimal_device()
            if gpu_device:
                cmd.extend(self.gpu_accelerator.get_ffmpeg_gpu_args(gpu_device))
        
        # Video codec and quality settings
        if params.get('codec') == 'h264':
            if task.gpu_accelerated:
                cmd.extend(['-c:v', 'h264_nvenc'])
            else:
                cmd.extend(['-c:v', 'libx264'])
        elif params.get('codec') == 'h265':
            if task.gpu_accelerated:
                cmd.extend(['-c:v', 'hevc_nvenc'])
            else:
                cmd.extend(['-c:v', 'libx265'])
        
        # Quality settings
        quality = params.get('quality', 'medium')
        if quality == 'low':
            cmd.extend(['-crf', '28', '-preset', 'fast'])
        elif quality == 'medium':
            cmd.extend(['-crf', '23', '-preset', 'medium'])
        elif quality == 'high':
            cmd.extend(['-crf', '18', '-preset', 'slow'])
        elif quality == 'ultra':
            cmd.extend(['-crf', '15', '-preset', 'veryslow'])
        
        # Resolution
        if 'resolution' in params:
            cmd.extend(['-vf', f"scale={params['resolution']}"])
        
        # Frame rate
        if 'fps' in params:
            cmd.extend(['-r', str(params['fps'])])
        
        # Audio codec
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        
        # Output file
        cmd.extend(['-y', task.output_file])
        
        # Execute FFmpeg with progress monitoring
        return await self._execute_ffmpeg(cmd, task)
    
    async def _enhance_video(self, task: VideoProcessingTask) -> bool:
        """Enhance video quality using AI/ML techniques"""
        params = task.parameters
        
        # For now, implement basic enhancement with FFmpeg filters
        cmd = ['ffmpeg', '-i', task.input_file]
        
        if task.gpu_accelerated:
            gpu_device = self.gpu_accelerator.get_optimal_device()
            if gpu_device:
                cmd.extend(self.gpu_accelerator.get_ffmpeg_gpu_args(gpu_device))
        
        # Enhancement filters
        filters = []
        
        if params.get('denoise', False):
            filters.append('hqdn3d')
        
        if params.get('sharpen', False):
            filters.append('unsharp=5:5:1.0:5:5:0.0')
        
        if params.get('brightness'):
            filters.append(f"eq=brightness={params['brightness']}")
        
        if params.get('contrast'):
            filters.append(f"eq=contrast={params['contrast']}")
        
        if params.get('saturation'):
            filters.append(f"eq=saturation={params['saturation']}")
        
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        cmd.extend(['-c:a', 'copy', '-y', task.output_file])
        
        return await self._execute_ffmpeg(cmd, task)
    
    async def _edit_video(self, task: VideoProcessingTask) -> bool:
        """Apply video editing operations"""
        params = task.parameters
        
        # Handle different edit operations
        if 'trim' in params:
            return await self._trim_video(task)
        elif 'concat' in params:
            return await self._concatenate_videos(task)
        elif 'overlay' in params:
            return await self._overlay_videos(task)
        
        return False
    
    async def _render_video(self, task: VideoProcessingTask) -> bool:
        """Render video from editing timeline"""
        # This would interface with a video editing engine
        # For now, implement basic rendering
        return await self._transcode_video(task)
    
    async def _analyze_video(self, task: VideoProcessingTask) -> bool:
        """Analyze video properties and content"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', task.input_file
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                analysis = json.loads(stdout.decode())
                
                # Save analysis to output file
                with open(task.output_file, 'w') as f:
                    json.dump(analysis, f, indent=2)
                
                return True
            else:
                task.error_message = stderr.decode()
                return False
                
        except Exception as e:
            task.error_message = str(e)
            return False
    
    async def _execute_ffmpeg(self, cmd: List[str], task: VideoProcessingTask) -> bool:
        """Execute FFmpeg command with progress monitoring"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress (simplified)
            while True:
                if process.returncode is not None:
                    break
                
                # Update progress (rough estimate)
                task.progress = min(task.progress + 5, 95)
                self._notify_progress(task.task_id, task.progress)
                
                await asyncio.sleep(1)
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True
            else:
                task.error_message = stderr.decode()
                return False
                
        except Exception as e:
            task.error_message = str(e)
            return False
    
    async def _trim_video(self, task: VideoProcessingTask) -> bool:
        """Trim video to specified duration"""
        params = task.parameters['trim']
        start_time = params.get('start', 0)
        duration = params.get('duration')
        
        cmd = ['ffmpeg', '-i', task.input_file]
        
        if start_time > 0:
            cmd.extend(['-ss', str(start_time)])
        
        if duration:
            cmd.extend(['-t', str(duration)])
        
        cmd.extend(['-c', 'copy', '-y', task.output_file])
        
        return await self._execute_ffmpeg(cmd, task)
    
    async def _concatenate_videos(self, task: VideoProcessingTask) -> bool:
        """Concatenate multiple videos"""
        input_files = task.parameters['concat']['files']
        
        # Create temporary file list
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for file_path in input_files:
                f.write(f"file '{file_path}'\n")
            filelist_path = f.name
        
        try:
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', filelist_path, '-c', 'copy', '-y', task.output_file
            ]
            
            return await self._execute_ffmpeg(cmd, task)
        finally:
            os.unlink(filelist_path)
    
    async def _overlay_videos(self, task: VideoProcessingTask) -> bool:
        """Overlay one video on top of another"""
        overlay_params = task.parameters['overlay']
        overlay_file = overlay_params['file']
        position = overlay_params.get('position', '10:10')
        
        cmd = [
            'ffmpeg', '-i', task.input_file, '-i', overlay_file,
            '-filter_complex', f'[0:v][1:v] overlay={position}',
            '-c:a', 'copy', '-y', task.output_file
        ]
        
        return await self._execute_ffmpeg(cmd, task)
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a processing task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return asdict(task)
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a processing task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status == 'processing':
                task.status = 'cancelled'
                self._notify_progress(task_id, task.progress, 'cancelled')
                return True
        return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for task_id, task in self.active_tasks.items():
            if task.status in ['completed', 'failed', 'cancelled']:
                if task.completed_at and (current_time - task.completed_at) > max_age_seconds:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.active_tasks[task_id]
            if task_id in self.task_callbacks:
                del self.task_callbacks[task_id]


# Global video processor instance
video_processor = VideoProcessor()