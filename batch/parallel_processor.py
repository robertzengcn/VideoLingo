import os
import json
import multiprocessing
from typing import List, Dict, Any
import cli

def process_video(args: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single video with the given arguments."""
    video_path = args['video_path']
    output_dir = args['output_dir']
    mode = args['mode']
    
    try:
        if mode == 'subtitles':
            success = cli.process_subtitles(video_path, output_dir)
        else:  # mode == 'dub'
            success = cli.process_dubbing(video_path, output_dir)
        
        return {
            'video': video_path,
            'success': success,
            'error': None
        }
    except Exception as e:
        return {
            'video': video_path,
            'success': False,
            'error': str(e)
        }

def process_videos_parallel(video_list_path: str, output_base_dir: str, 
                          mode: str = 'subtitles', max_workers: int = None) -> List[Dict[str, Any]]:
    """
    Process multiple videos in parallel.
    
    Args:
        video_list_path: Path to JSON file containing list of video paths
        output_base_dir: Base directory for output files
        mode: Processing mode ('subtitles' or 'dub')
        max_workers: Maximum number of parallel processes (default: number of CPU cores)
    
    Returns:
        List of results for each video
    """
    if not os.path.exists(video_list_path):
        raise FileNotFoundError(f"Video list file '{video_list_path}' does not exist.")
    
    try:
        with open(video_list_path, 'r', encoding='utf-8') as f:
            video_list = json.load(f)
    except json.JSONDecodeError:
        raise ValueError("Video list file must be a valid JSON file containing a list of video paths.")
    
    if not isinstance(video_list, list):
        raise ValueError("Video list file must contain a JSON array of video paths.")
    
    # Prepare arguments for each video
    process_args = []
    for video_path in video_list:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(output_base_dir, video_name)
        
        process_args.append({
            'video_path': video_path,
            'output_dir': output_dir,
            'mode': mode
        })
    
    # Set default max_workers to number of CPU cores
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    
    # Process videos in parallel
    with multiprocessing.Pool(processes=max_workers) as pool:
        results = pool.map(process_video, process_args)
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Parallel video processing for VideoLingo')
    parser.add_argument('video_list', help='JSON file containing list of video paths')
    parser.add_argument('output_dir', help='Base output directory for all processed videos')
    parser.add_argument('--mode', choices=['subtitles', 'dub'], default='subtitles',
                       help='Processing mode (subtitles or dubbing)')
    parser.add_argument('--max-workers', type=int, help='Maximum number of parallel processes')
    
    args = parser.parse_args()
    
    try:
        results = process_videos_parallel(
            args.video_list,
            args.output_dir,
            args.mode,
            args.max_workers
        )
        
        # Print summary
        print("\nProcessing Summary:")
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"{status} {result['video']}")
            if not result['success'] and result['error']:
                print(f"  Error: {result['error']}")
        
        # Print statistics
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total - successful
        print(f"\nTotal videos: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 