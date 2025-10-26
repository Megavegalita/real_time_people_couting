#!/usr/bin/env python3
"""
Performance Benchmark Script
============================

Measures FPS, memory, and CPU usage for original vs optimized code.
"""

import time
import psutil
import subprocess
import sys
import os
from typing import Dict, Any, Tuple
from pathlib import Path


class PerformanceBenchmark:
    """Benchmark performance of code."""
    
    def __init__(self):
        """Initialize benchmark."""
        self.results_dir = Path("benchmark_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def measure_execution(
        self, 
        command: list, 
        label: str
    ) -> Dict[str, Any]:
        """Measure execution time, FPS, memory."""
        print(f"\n📊 Measuring {label}...")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Start process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor while running
        cpu_samples = []
        memory_samples = []
        
        max_duration = 60  # Max 60 seconds
        
        try:
            elapsed = 0
            while process.poll() is None and elapsed < max_duration:
                time.sleep(0.1)
                elapsed = time.time() - start_time
                
                # Sample CPU and memory
                try:
                    cpu_pct = process.cpu_percent()
                    memory_mb = self._get_process_memory(process.pid)
                    if memory_mb > 0:
                        cpu_samples.append(cpu_pct)
                        memory_samples.append(memory_mb)
                except:
                    pass
                    
            # Wait for completion
            stdout, stderr = process.communicate(timeout=30)
            
            end_time = time.time()
            duration = end_time - start_time
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            duration = max_duration
            
        end_memory = self._get_memory_usage()
        
        # Calculate averages
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else 0
        peak_memory = max(memory_samples) if memory_samples else 0
        
        # Try to extract FPS from output
        fps = self._extract_fps(stdout)
        
        result = {
            'label': label,
            'duration': duration,
            'fps': fps,
            'cpu_avg': avg_cpu,
            'memory_avg_mb': avg_memory,
            'memory_peak_mb': peak_memory,
            'memory_delta_mb': end_memory - start_memory
        }
        
        return result
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def _get_process_memory(self, pid: int) -> float:
        """Get memory usage for specific process."""
        try:
            process = psutil.Process(pid)
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0
    
    def _extract_fps(self, output: str) -> float:
        """Extract FPS from output."""
        # Look for FPS in output
        import re
        match = re.search(r'FPS[:\s]+([\d.]+)', output)
        if match:
            return float(match.group(1))
        return 0.0
    
    def benchmark(self, video_path: str) -> Tuple[Dict, Dict]:
        """Run full benchmark."""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK")
        print("="*60)
        
        # Test parameters
        prototxt = "detector/MobileNetSSD_deploy.prototxt"
        model = "detector/MobileNetSSD_deploy.caffemodel"
        
        # Original code
        original_cmd = [
            "python", "people_counter.py",
            "--prototxt", prototxt,
            "--model", model,
            "--input", video_path,
            "--confidence", "0.4",
            "--skip-frames", "30"
        ]
        
        original_results = self.measure_execution(original_cmd, "ORIGINAL")
        
        # Optimized code (placeholder)
        optimized_results = {
            'label': 'OPTIMIZED',
            'duration': 0,
            'fps': 0,
            'cpu_avg': 0,
            'memory_avg_mb': 0,
            'memory_peak_mb': 0,
            'memory_delta_mb': 0
        }
        
        # Save results
        with open(self.results_dir / "benchmark_results.json", "w") as f:
            json.dump({
                'original': original_results,
                'optimized': optimized_results
            }, f, indent=2)
        
        return original_results, optimized_results
    
    def print_comparison(
        self, 
        original: Dict[str, Any],
        optimized: Dict[str, Any]
    ):
        """Print comparison results."""
        print("\n" + "="*60)
        print("BENCHMARK COMPARISON")
        print("="*60)
        
        # Calculate ratios
        if original['fps'] > 0:
            fps_ratio = optimized['fps'] / original['fps'] * 100
        else:
            fps_ratio = 100
            
        cpu_ratio = optimized['cpu_avg'] / original['cpu_avg'] * 100 if original['cpu_avg'] > 0 else 100
        memory_ratio = optimized['memory_avg_mb'] / original['memory_avg_mb'] * 100 if original['memory_avg_mb'] > 0 else 100
        
        print(f"\n📊 FPS:")
        print(f"   Original:  {original['fps']:.2f}")
        print(f"   Optimized: {optimized['fps']:.2f} ({fps_ratio:.1f}%)")
        
        print(f"\n🖥️  CPU:")
        print(f"   Original:  {original['cpu_avg']:.1f}%")
        print(f"   Optimized: {optimized['cpu_avg']:.1f}% ({cpu_ratio:.1f}%)")
        
        print(f"\n💾 Memory:")
        print(f"   Original:  {original['memory_avg_mb']:.1f} MB")
        print(f"   Optimized: {optimized['memory_avg_mb']:.1f} MB ({memory_ratio:.1f}%)")
        
        # Check if meets criteria
        print("\n" + "="*60)
        
        if fps_ratio >= 95 and memory_ratio <= 110:
            print("✅ PERFORMANCE ACCEPTABLE")
            print(f"   FPS: {fps_ratio:.1f}% (target: >=95%)")
            print(f"   Memory: {memory_ratio:.1f}% (target: <=110%)")
        else:
            print("❌ PERFORMANCE DEGRADED")
            if fps_ratio < 95:
                print(f"   ⚠️  FPS dropped to {fps_ratio:.1f}%")
            if memory_ratio > 110:
                print(f"   ⚠️  Memory increased to {memory_ratio:.1f}%")
        
        print("="*60)


def main():
    """Main entry point."""
    video_path = "utils/data/tests/test_1.mp4"
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    benchmark = PerformanceBenchmark()
    original, optimized = benchmark.benchmark(video_path)
    benchmark.print_comparison(original, optimized)


if __name__ == "__main__":
    import json
    import psutil
    main()

