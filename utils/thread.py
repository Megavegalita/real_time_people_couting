import cv2
import threading
import queue
from typing import Optional
import numpy as np


class ThreadingClass:
  """Threaded video capture to reduce frame latency.
  
  This class runs video capture in a separate thread and uses a queue
  to store frames. This approach removes OpenCV's internal buffer
  and reduces frame lag by always providing the latest available frame.
  """
  
  def __init__(self, name: str) -> None:
    """Initialize threaded video capture.
    
    Args:
      name: Video source (0 for webcam, path to video file, or RTSP URL)
    """
    self.cap: cv2.VideoCapture = cv2.VideoCapture(name)
    # define an empty queue and thread
    self.q: queue.Queue = queue.Queue()
    self.running: bool = True
    t: threading.Thread = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  def _reader(self) -> None:
    """Read frames in separate thread.
    
    Continuously reads frames from the capture device and puts them
    in the queue. Only keeps the latest frame to reduce latency.
    """
    while self.running:
      ret: bool
      frame: Optional[np.ndarray]
      ret, frame = self.cap.read() # read the frames and ---
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()
        except queue.Empty:
          pass
      if frame is not None:
        self.q.put(frame) # --- store them in a queue (instead of the buffer)

  def read(self) -> Optional[np.ndarray]:
    """Read latest frame from queue.
    
    Returns:
      Latest frame as numpy array, or None if queue is empty
    """
    try:
      return self.q.get(timeout=1) # fetch frames from the queue one by one
    except queue.Empty:
      return None

  def release(self) -> bool:
    """Release video capture resources.
    
    Stops the reader thread and releases the hardware resources.
    
    Returns:
      True if release was successful, False otherwise
    """
    self.running = False
    return self.cap.release() # release the hw resource
