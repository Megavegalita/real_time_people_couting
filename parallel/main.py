#!/usr/bin/env python3
"""
Main entry point for Parallel People Counter
==============================================

Run parallel people counting from command line.
"""

import argparse
import sys
import os
import logging
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from parallel.parallel_people_counter import ParallelPeopleCounter
from parallel.config_manager import ConfigManager
from parallel.utils.logger import ParallelLogger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Parallel People Counting System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file (JSON)'
    )

    parser.add_argument(
        '-p', '--prototxt',
        type=str,
        default='detector/MobileNetSSD_deploy.prototxt',
        help='Path to Caffe prototxt file'
    )

    parser.add_argument(
        '-m', '--model',
        type=str,
        default='detector/MobileNetSSD_deploy.caffemodel',
        help='Path to Caffe model file'
    )

    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of worker threads'
    )

    parser.add_argument(
        '--camera',
        action='append',
        type=str,
        help='Camera source to add (can be used multiple times)'
    )

    parser.add_argument(
        '--video',
        action='append',
        type=str,
        help='Video file to process (can be used multiple times)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='parallel/results/',
        help='Output directory for results'
    )

    parser.add_argument(
        '--export',
        type=str,
        choices=['json', 'csv'],
        help='Export results to JSON or CSV'
    )

    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Print real-time dashboard'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting Parallel People Counter...")

    try:
        # Initialize counter
        worker_count = args.workers if args.workers else 4

        counter = ParallelPeopleCounter(
            worker_count=worker_count,
            result_output=args.output,
            log_level=args.log_level
        )

        # Load model
        logger.info("Loading model...")
        counter.load_model(
            prototxt=args.prototxt,
            model=args.model
        )

        # Load configuration if provided
        if args.config:
            logger.info(f"Loading configuration from {args.config}")
            config_manager = ConfigManager(args.config)
            worker_count = config_manager.get_worker_count()

            # Update counter with worker count
            counter.worker_count = worker_count

            # Create tasks from config
            tasks = config_manager.create_tasks()
            for task in tasks:
                if task['type'] == 'camera':
                    counter.add_camera(
                        source=task['source'],
                        camera_id=task['camera_id'],
                        alias=task['alias'],
                        threshold=task['threshold']
                    )
                elif task['type'] == 'video':
                    counter.add_video(
                        video_path=task['source'],
                        video_id=task['video_id'],
                        alias=task['alias'],
                        threshold=task['threshold']
                    )

            # Get additional config
            parallel_config = config_manager.get_parallel_config()
            processing_config = {
                'skip_frames': parallel_config.get('skip_frames', 30),
                'confidence': parallel_config.get('confidence', 0.4),
                'Thread': False
            }

        else:
            # Manual configuration
            processing_config = {
                'skip_frames': 30,
                'confidence': 0.4,
                'Thread': False
            }

            # Add cameras if specified
            if args.camera:
                for i, camera_source in enumerate(args.camera):
                    counter.add_camera(
                        source=camera_source,
                        camera_id=f"camera_{i+1}",
                        alias=f"Camera {i+1}"
                    )

            # Add videos if specified
            if args.video:
                for i, video_path in enumerate(args.video):
                    counter.add_video(
                        video_path=video_path,
                        video_id=f"video_{i+1}",
                        alias=f"Video {i+1}"
                    )

            # If no cameras or videos specified, add default
            if not args.camera and not args.video:
                logger.warning("No cameras or videos specified. Adding default webcam.")
                counter.add_camera(source="0", camera_id="default", alias="Webcam")

        # Start processing
        logger.info("Starting parallel processing...")
        counter.start_processing(config=processing_config)

        # Run processing
        try:
            import signal

            def signal_handler(sig, frame):
                logger.info("Received interrupt signal, stopping...")
                counter.stop_processing()
                if args.export:
                    counter.export_results(format=args.export)
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Wait for tasks to complete
            while counter.task_queue.qsize() > 0 or len(counter.workers) > 0:
                if args.dashboard:
                    counter.print_dashboard()
                import time
                time.sleep(2)

            # Print final dashboard
            if args.dashboard:
                counter.print_dashboard()

            # Export results if requested
            if args.export:
                logger.info(f"Exporting results to {args.export}...")
                counter.export_results(format=args.export)

            # Summary
            summary = counter.get_summary()
            logger.info("Processing completed!")
            logger.info(f"Total tasks: {summary['stats']['total_tasks']}")
            logger.info(f"Completed: {summary['stats']['completed_tasks']}")
            logger.info(f"Total In: {summary['overall']['total_in']}")
            logger.info(f"Total Out: {summary['overall']['total_out']}")

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            counter.stop_processing()
            if args.export:
                counter.export_results(format=args.export)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

