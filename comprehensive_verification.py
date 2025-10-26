#!/usr/bin/env python3
"""
Comprehensive Verification Script
=================================

Verifies both single-threaded (people_counter.py) and parallel processing
to ensure optimization didn't break anything.
"""

import subprocess
import json
import sys
import os
import time
import psutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime


class ComprehensiveVerifier:
    """Verify both single and parallel processing."""
    
    def __init__(self):
        """Initialize verifier."""
        self.results_dir = Path("verification_results")
        self.results_dir.mkdir(exist_ok=True)
        self.test_video = "utils/data/tests/test_1.mp4"
        
    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def run_single_processing(self) -> Dict[str, Any]:
        """Run single-threaded people counter."""
        self.print_header("🔵 SINGLE PROCESSING TEST")
        
        print("\n📊 Running people_counter.py (original)...")
        
        prototxt = "detector/MobileNetSSD_deploy.prototxt"
        model = "detector/MobileNetSSD_deploy.caffemodel"
        
        command = [
            "python", "people_counter.py",
            "--prototxt", prototxt,
            "--model", model,
            "--input", self.test_video,
            "--confidence", "0.4",
            "--skip-frames", "30"
        ]
        
        result = self._run_command(command, "single_processing")
        return result
    
    def run_parallel_processing(self) -> Dict[str, Any]:
        """Run parallel people counter."""
        self.print_header("🟢 PARALLEL PROCESSING TEST")
        
        print("\n📊 Running parallel/main.py...")
        
        prototxt = "detector/MobileNetSSD_deploy.prototxt"
        model = "detector/MobileNetSSD_deploy.caffemodel"
        
        command = [
            "python", "parallel/main.py",
            "--prototxt", prototxt,
            "--model", model,
            "--video", self.test_video,
            "--workers", "2",
            "--log-level", "INFO"
        ]
        
        result = self._run_command(command, "parallel_processing")
        return result
    
    def _run_command(
        self, 
        command: List[str], 
        label: str
    ) -> Dict[str, Any]:
        """Run command and collect metrics."""
        print(f"   Command: {' '.join(command)}")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor
            cpu_samples = []
            memory_samples = []
            max_duration = 120
            
            elapsed = 0
            while process.poll() is None and elapsed < max_duration:
                time.sleep(0.1)
                elapsed = time.time() - start_time
                
                try:
                    cpu_pct = process.cpu_percent()
                    memory_mb = self._get_process_memory(process.pid)
                    if memory_mb > 0:
                        cpu_samples.append(cpu_pct)
                        memory_samples.append(memory_mb)
                except:
                    pass
            
            stdout, stderr = process.communicate(timeout=30)
            end_time = time.time()
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            end_time = start_time + max_duration
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {}
        
        duration = end_time - start_time
        
        # Parse output
        total_in, total_out, fps = self._parse_output(stdout)
        
        # Calculate averages
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else 0
        peak_memory = max(memory_samples) if memory_samples else 0
        
        result = {
            'label': label,
            'success': process.returncode == 0,
            'duration': duration,
            'total_in': total_in,
            'total_out': total_out,
            'current_count': total_in - total_out,
            'fps': fps,
            'cpu_avg': avg_cpu,
            'memory_avg_mb': avg_memory,
            'memory_peak_mb': peak_memory,
            'returncode': process.returncode,
            'stdout': stdout,
            'stderr': stderr
        }
        
        # Save to file
        with open(self.results_dir / f"{label}_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
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
    
    def _parse_output(self, output: str) -> Tuple[int, int, float]:
        """Parse output to extract counting results."""
        total_in = 0
        total_out = 0
        fps = 0.0
        
        # Try to extract from output
        import re
        
        # Look for counting patterns
        in_match = re.search(r'Enter:\s*(\d+)', output)
        if in_match:
            total_in = int(in_match.group(1))
        
        out_match = re.search(r'Exit:\s*(\d+)', output)
        if out_match:
            total_out = int(out_match.group(1))
        
        # Look for FPS
        fps_match = re.search(r'FPS[:\s]+([\d.]+)', output)
        if fps_match:
            fps = float(fps_match.group(1))
        
        return total_in, total_out, fps
    
    def compare_results(
        self,
        single_result: Dict[str, Any],
        parallel_result: Dict[str, Any]
    ):
        """Compare single vs parallel results."""
        self.print_header("📊 COMPARISON RESULTS")
        
        print("\n🔵 Single Processing:")
        print(f"   Status: {'✅ Success' if single_result.get('success') else '❌ Failed'}")
        print(f"   Duration: {single_result.get('duration', 0):.2f}s")
        print(f"   Total In: {single_result.get('total_in', 0)}")
        print(f"   Total Out: {single_result.get('total_out', 0)}")
        print(f"   Current Count: {single_result.get('current_count', 0)}")
        print(f"   FPS: {single_result.get('fps', 0):.2f}")
        print(f"   Memory Avg: {single_result.get('memory_avg_mb', 0):.1f} MB")
        print(f"   Memory Peak: {single_result.get('memory_peak_mb', 0):.1f} MB")
        
        print("\n🟢 Parallel Processing:")
        print(f"   Status: {'✅ Success' if parallel_result.get('success') else '❌ Failed'}")
        print(f"   Duration: {parallel_result.get('duration', 0):.2f}s")
        print(f"   Total In: {parallel_result.get('total_in', 0)}")
        print(f"   Total Out: {parallel_result.get('total_out', 0)}")
        print(f"   Current Count: {parallel_result.get('current_count', 0)}")
        print(f"   FPS: {parallel_result.get('fps', 0):.2f}")
        print(f"   Memory Avg: {parallel_result.get('memory_avg_mb', 0):.1f} MB")
        print(f"   Memory Peak: {parallel_result.get('memory_peak_mb', 0):.1f} MB")
        
        # Calculate differences
        print("\n📈 Performance Comparison:")
        duration_diff = parallel_result.get('duration', 0) - single_result.get('duration', 0)
        speedup = single_result.get('duration', 1) / parallel_result.get('duration', 1)
        
        print(f"   Duration Difference: {duration_diff:.2f}s")
        print(f"   Speedup: {speedup:.2f}x")
        
        memory_diff_pct = (parallel_result.get('memory_avg_mb', 0) / single_result.get('memory_avg_mb', 1) - 1) * 100
        print(f"   Memory Difference: {memory_diff_pct:+.1f}%")
        
        # Accuracy check
        print("\n✅ Accuracy Check:")
        in_match = abs(single_result.get('total_in', 0) - parallel_result.get('total_in', 0))
        out_match = abs(single_result.get('total_out', 0) - parallel_result.get('total_out', 0))
        
        if in_match == 0 and out_match == 0:
            print(f"   ✅ Perfect match: In={in_match}, Out={out_match}")
        else:
            print(f"   ⚠️  Differences: In={in_match}, Out={out_match}")
        
    def verify(self):
        """Run comprehensive verification."""
        print("\n" + "="*70)
        print("  COMPREHENSIVE VERIFICATION")
        print("  Testing Single vs Parallel Processing")
        print("="*70)
        
        # Check if test video exists
        if not os.path.exists(self.test_video):
            print(f"\n❌ Test video not found: {self.test_video}")
            print("   Please ensure test video exists.")
            return False
        
        # Run tests
        single_result = self.run_single_processing()
        parallel_result = self.run_parallel_processing()
        
        # Compare
        self.compare_results(single_result, parallel_result)
        
        # Summary
        self.print_header("📋 VERIFICATION SUMMARY")
        
        print("\n✅ Tests Completed")
        print(f"   Single Processing: {'✅ Pass' if single_result.get('success') else '❌ Fail'}")
        print(f"   Parallel Processing: {'✅ Pass' if parallel_result.get('success') else '❌ Fail'}")
        
        # Save summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'single_result': single_result,
            'parallel_result': parallel_result,
            'accuracy_match': (
                single_result.get('total_in') == parallel_result.get('total_in') and
                single_result.get('total_out') == parallel_result.get('total_out')
            )
        }
        
        with open(self.results_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n   Results saved to: {self.results_dir}/")
        
        return True


def main():
    """Main entry point."""
    verifier = ComprehensiveVerifier()
    success = verifier.verify()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

