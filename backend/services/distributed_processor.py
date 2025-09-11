"""
Distributed Video Processing Service
Coordinates video processing across multiple edge nodes
"""
import asyncio
import json
import time
import uuid
import aiohttp
import math
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

from config.edge_config import edge_config, EdgeNodeConfig
from services.video_processor import VideoProcessingTask, video_processor


@dataclass
class DistributedTask:
    """Represents a distributed processing task"""
    task_id: str
    original_file: str
    output_file: str
    operation: str
    parameters: Dict[str, Any]
    chunks: List[Dict] = None
    assigned_nodes: Dict[str, str] = None  # chunk_id -> node_id
    chunk_results: Dict[str, str] = None  # chunk_id -> result_file
    status: str = 'pending'  # pending, distributing, processing, merging, completed, failed
    progress: float = 0.0
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None


class VideoChunker:
    """Handles video segmentation for distributed processing"""
    
    @staticmethod
    async def analyze_video_duration(file_path: str) -> float:
        """Get video duration in seconds"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', file_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                duration = float(stdout.decode().strip())
                return duration
            else:
                raise Exception(f"Failed to analyze video: {stderr.decode()}")
                
        except Exception as e:
            raise Exception(f"Error analyzing video duration: {str(e)}")
    
    @staticmethod
    async def create_chunks(file_path: str, chunk_duration: int = None) -> List[Dict]:
        """Split video into chunks for distributed processing"""
        if chunk_duration is None:
            chunk_duration = edge_config.video_chunk_size
        
        # Get total duration
        total_duration = await VideoChunker.analyze_video_duration(file_path)
        
        # Calculate number of chunks
        num_chunks = math.ceil(total_duration / chunk_duration)
        
        chunks = []
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, total_duration)
            actual_duration = end_time - start_time
            
            chunk = {
                'chunk_id': f"chunk_{i:03d}",
                'start_time': start_time,
                'duration': actual_duration,
                'end_time': end_time,
                'sequence': i,
                'file_path': None  # Will be set when chunk is created
            }
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    async def extract_chunk(input_file: str, chunk: Dict, output_dir: str) -> str:
        """Extract a specific chunk from video"""
        chunk_filename = f"{chunk['chunk_id']}.mp4"
        chunk_path = f"{output_dir}/{chunk_filename}"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(chunk['start_time']),
            '-t', str(chunk['duration']),
            '-c', 'copy',  # Use stream copy for faster extraction
            '-avoid_negative_ts', 'make_zero',
            '-y', chunk_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                chunk['file_path'] = chunk_path
                return chunk_path
            else:
                raise Exception(f"Failed to extract chunk: {stderr.decode()}")
                
        except Exception as e:
            raise Exception(f"Error extracting chunk {chunk['chunk_id']}: {str(e)}")
    
    @staticmethod
    async def merge_chunks(chunk_files: List[str], output_file: str) -> bool:
        """Merge processed chunks back into single video"""
        import tempfile
        import os
        
        # Create temporary file list for concatenation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for chunk_file in chunk_files:
                f.write(f"file '{chunk_file}'\n")
            filelist_path = f.name
        
        try:
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', filelist_path,
                '-c', 'copy',
                '-y', output_file
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True
            else:
                raise Exception(f"Failed to merge chunks: {stderr.decode()}")
                
        except Exception as e:
            raise Exception(f"Error merging chunks: {str(e)}")
        finally:
            os.unlink(filelist_path)


class DistributedProcessor:
    """Manages distributed video processing across edge nodes"""
    
    def __init__(self, edge_manager):
        self.edge_manager = edge_manager
        self.active_tasks: Dict[str, DistributedTask] = {}
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=8)
    
    async def initialize(self):
        """Initialize HTTP session for node communication"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def create_distributed_task(self, operation: str, input_file: str, 
                                    output_file: str, parameters: Dict[str, Any]) -> DistributedTask:
        """Create a new distributed processing task"""
        task_id = str(uuid.uuid4())
        
        task = DistributedTask(
            task_id=task_id,
            original_file=input_file,
            output_file=output_file,
            operation=operation,
            parameters=parameters,
            chunks=[],
            assigned_nodes={},
            chunk_results={},
            status='pending',
            created_at=time.time()
        )
        
        self.active_tasks[task_id] = task
        return task
    
    async def process_distributed_task(self, task: DistributedTask) -> bool:
        """Process a task using distributed computing"""
        try:
            task.status = 'distributing'
            task.started_at = time.time()
            
            # Step 1: Analyze if task should be distributed
            should_distribute = await self._should_distribute_task(task)
            
            if not should_distribute:
                # Process on single node (local)
                return await self._process_on_single_node(task)
            
            # Step 2: Create video chunks
            await self._create_video_chunks(task)
            
            # Step 3: Assign chunks to edge nodes
            await self._assign_chunks_to_nodes(task)
            
            # Step 4: Process chunks on assigned nodes
            task.status = 'processing'
            await self._process_chunks_on_nodes(task)
            
            # Step 5: Merge results
            task.status = 'merging'
            success = await self._merge_chunk_results(task)
            
            if success:
                task.status = 'completed'
                task.completed_at = time.time()
                task.progress = 100.0
            else:
                task.status = 'failed'
                task.error_message = "Failed to merge chunk results"
            
            return success
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            return False
    
    async def _should_distribute_task(self, task: DistributedTask) -> bool:
        """Determine if task should be distributed across nodes"""
        # Get available nodes
        available_nodes = self.edge_manager.get_available_nodes()
        
        # Don't distribute if we don't have multiple nodes
        if len(available_nodes) < 2:
            return False
        
        # Don't distribute very short videos
        try:
            duration = await VideoChunker.analyze_video_duration(task.original_file)
            if duration < edge_config.video_chunk_size * 2:
                return False
        except:
            return False
        
        # Don't distribute operations that can't be parallelized
        non_distributable_ops = ['analyze', 'concat']
        if task.operation in non_distributable_ops:
            return False
        
        return True
    
    async def _process_on_single_node(self, task: DistributedTask) -> bool:
        """Process task on a single node (usually local)"""
        # Create a regular VideoProcessingTask
        video_task = await video_processor.create_task(
            task.operation,
            task.original_file,
            task.output_file,
            task.parameters
        )
        
        # Process the task
        success = await video_processor.process_video(video_task)
        
        # Update distributed task status
        if success:
            task.progress = 100.0
        else:
            task.error_message = video_task.error_message
        
        return success
    
    async def _create_video_chunks(self, task: DistributedTask):
        """Create video chunks for distributed processing"""
        import tempfile
        import os
        
        # Create temporary directory for chunks
        temp_dir = tempfile.mkdtemp(prefix=f"chunks_{task.task_id}_")
        
        # Create chunks metadata
        chunks = await VideoChunker.create_chunks(task.original_file)
        
        # Extract actual chunk files
        extracted_chunks = []
        for chunk in chunks:
            try:
                chunk_path = await VideoChunker.extract_chunk(
                    task.original_file, chunk, temp_dir
                )
                extracted_chunks.append(chunk)
            except Exception as e:
                raise Exception(f"Failed to create chunk {chunk['chunk_id']}: {str(e)}")
        
        task.chunks = extracted_chunks
        task.parameters['temp_dir'] = temp_dir
    
    async def _assign_chunks_to_nodes(self, task: DistributedTask):
        """Assign chunks to available edge nodes"""
        available_nodes = self.edge_manager.get_available_nodes()
        
        if not available_nodes:
            raise Exception("No available nodes for processing")
        
        # Assign chunks to nodes in round-robin fashion
        for i, chunk in enumerate(task.chunks):
            node = available_nodes[i % len(available_nodes)]
            task.assigned_nodes[chunk['chunk_id']] = node.node_id
            
            # Mark node as busy
            self.edge_manager.update_node_status(node.node_id, 'busy')
    
    async def _process_chunks_on_nodes(self, task: DistributedTask):
        """Process chunks on assigned edge nodes"""
        if not self.session:
            await self.initialize()
        
        # Create processing tasks for each chunk
        chunk_tasks = []
        for chunk in task.chunks:
            chunk_id = chunk['chunk_id']
            node_id = task.assigned_nodes[chunk_id]
            
            chunk_task = asyncio.create_task(
                self._process_chunk_on_node(task, chunk, node_id)
            )
            chunk_tasks.append(chunk_task)
        
        # Wait for all chunks to complete
        results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
        
        # Check results
        failed_chunks = []
        for i, result in enumerate(results):
            chunk = task.chunks[i]
            if isinstance(result, Exception):
                failed_chunks.append(chunk['chunk_id'])
            elif not result:
                failed_chunks.append(chunk['chunk_id'])
        
        if failed_chunks:
            raise Exception(f"Failed to process chunks: {failed_chunks}")
        
        # Update progress
        task.progress = 90.0  # 90% when all chunks are processed
    
    async def _process_chunk_on_node(self, task: DistributedTask, chunk: Dict, node_id: str) -> bool:
        """Process a single chunk on a specific node"""
        try:
            node = self.edge_manager.nodes.get(node_id)
            if not node:
                raise Exception(f"Node {node_id} not found")
            
            if node_id == "local":
                # Process locally
                return await self._process_chunk_locally(task, chunk)
            else:
                # Process on remote node
                return await self._process_chunk_remotely(task, chunk, node)
                
        except Exception as e:
            print(f"Error processing chunk {chunk['chunk_id']} on node {node_id}: {e}")
            return False
        finally:
            # Mark node as available again
            self.edge_manager.update_node_status(node_id, 'online')
    
    async def _process_chunk_locally(self, task: DistributedTask, chunk: Dict) -> bool:
        """Process chunk on local node"""
        chunk_id = chunk['chunk_id']
        input_file = chunk['file_path']
        output_file = f"{task.parameters['temp_dir']}/processed_{chunk_id}.mp4"
        
        # Create processing task
        video_task = await video_processor.create_task(
            task.operation,
            input_file,
            output_file,
            task.parameters
        )
        
        # Process the chunk
        success = await video_processor.process_video(video_task)
        
        if success:
            task.chunk_results[chunk_id] = output_file
        
        return success
    
    async def _process_chunk_remotely(self, task: DistributedTask, chunk: Dict, node: EdgeNodeConfig) -> bool:
        """Process chunk on remote edge node"""
        # This would implement the protocol for sending chunks to remote nodes
        # For now, we'll simulate remote processing
        
        chunk_id = chunk['chunk_id']
        
        try:
            # Simulate processing time
            await asyncio.sleep(2)
            
            # In a real implementation, this would:
            # 1. Upload chunk to remote node
            # 2. Send processing request
            # 3. Monitor progress
            # 4. Download result
            
            output_file = f"{task.parameters['temp_dir']}/processed_{chunk_id}.mp4"
            
            # For simulation, just copy the input file
            import shutil
            shutil.copy2(chunk['file_path'], output_file)
            
            task.chunk_results[chunk_id] = output_file
            return True
            
        except Exception as e:
            print(f"Remote processing failed for chunk {chunk_id}: {e}")
            return False
    
    async def _merge_chunk_results(self, task: DistributedTask) -> bool:
        """Merge processed chunks into final result"""
        try:
            # Collect all processed chunk files in order
            chunk_files = []
            for chunk in sorted(task.chunks, key=lambda c: c['sequence']):
                chunk_id = chunk['chunk_id']
                if chunk_id in task.chunk_results:
                    chunk_files.append(task.chunk_results[chunk_id])
                else:
                    raise Exception(f"Missing result for chunk {chunk_id}")
            
            # Merge chunks
            success = await VideoChunker.merge_chunks(chunk_files, task.output_file)
            
            if success:
                # Clean up temporary files
                await self._cleanup_temp_files(task)
            
            return success
            
        except Exception as e:
            task.error_message = f"Failed to merge chunks: {str(e)}"
            return False
    
    async def _cleanup_temp_files(self, task: DistributedTask):
        """Clean up temporary files created during processing"""
        import shutil
        
        try:
            temp_dir = task.parameters.get('temp_dir')
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Failed to clean up temp files: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a distributed task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return asdict(task)
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a distributed task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status in ['pending', 'distributing', 'processing']:
                task.status = 'cancelled'
                # In a real implementation, would also cancel chunk processing on nodes
                return True
        return False


# This will be initialized by the edge computing API
distributed_processor = None