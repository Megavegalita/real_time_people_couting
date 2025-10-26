"""
Result Handler for Parallel People Counting
============================================

Manages results from multiple workers.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class ResultHandler:
    """
    Handles results from parallel workers.
    """

    def __init__(self, output_dir: str = "parallel/results/"):
        """
        Initialize ResultHandler.

        Args:
            output_dir: Directory to save results
        """
        self.output_dir = output_dir
        self.results: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = Lock()
        self.statistics: Dict[str, Any] = {
            'total_workers': 0,
            'active_workers': 0,
            'total_cameras': 0,
            'total_videos': 0,
            'total_in': 0,
            'total_out': 0,
            'start_time': None,
            'end_time': None
        }

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def add_result(self, task_id: str, result: Dict[str, Any]):
        """
        Add result from a worker.

        Args:
            task_id: Unique task identifier
            result: Result dictionary
        """
        with self.lock:
            if task_id not in self.results:
                self.results[task_id] = []

            result['timestamp'] = datetime.now().isoformat()
            self.results[task_id].append(result)

            # Update statistics - ONLY use latest result for each task
            # Don't accumulate, as results are sent periodically
            # We'll calculate overall stats from latest results of all tasks

    def get_task_results(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific task."""
        return self.results.get(task_id, [])

    def get_latest_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest result for a task."""
        if task_id in self.results and self.results[task_id]:
            return self.results[task_id][-1]
        return None

    def get_all_results(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all results."""
        with self.lock:
            return self.results.copy()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all tasks.

        Returns:
            Summary dictionary
        """
        summary = {
            'total_tasks': len(self.results),
            'tasks': {}
        }

        # Calculate proper totals from latest results only
        total_in_all = 0
        total_out_all = 0

        for task_id, results in self.results.items():
            if not results:
                continue

            latest = results[-1]
            task_in = latest.get('total_in', 0)
            task_out = latest.get('total_out', 0)
            
            task_summary = {
                'latest_fps': latest.get('fps', 0),
                'total_in': task_in,
                'total_out': task_out,
                'current_count': latest.get('current_count', 0),
                'status': latest.get('status', 'unknown'),
                'last_update': latest.get('timestamp', ''),
                'total_updates': len(results)
            }
            summary['tasks'][task_id] = task_summary
            
            # Accumulate totals from latest results
            total_in_all += task_in
            total_out_all += task_out

        summary['overall'] = {
            'total_in': total_in_all,
            'total_out': total_out_all,
            'net_count': total_in_all - total_out_all
        }

        return summary

    def export_to_json(self, filename: str = None):
        """
        Export results to JSON file.

        Args:
            filename: Output filename (default: timestamp-based)
        """
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.output_dir, filename)

        export_data = {
            'export_time': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'detailed_results': self.get_all_results()
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Results exported to {filepath}")

    def export_to_csv(self, task_id: str, filename: str = None):
        """
        Export task results to CSV.

        Args:
            task_id: Task ID to export
            filename: Output filename
        """
        if task_id not in self.results:
            logger.warning(f"No results found for task {task_id}")
            return

        if filename is None:
            filename = f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.output_dir, filename)

        import csv

        with open(filepath, 'w', newline='') as f:
            if not self.results[task_id]:
                return

            fieldnames = list(self.results[task_id][0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results[task_id])

        logger.info(f"CSV exported to {filepath}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.statistics.copy()

    def reset(self):
        """Reset all results and statistics."""
        with self.lock:
            self.results.clear()
            self.statistics = {
                'total_workers': 0,
                'active_workers': 0,
                'total_cameras': 0,
                'total_videos': 0,
                'total_in': 0,
                'total_out': 0,
                'start_time': None,
                'end_time': None
            }

    def update_statistics(self, **kwargs):
        """Update statistics with new values."""
        with self.lock:
            self.statistics.update(kwargs)

