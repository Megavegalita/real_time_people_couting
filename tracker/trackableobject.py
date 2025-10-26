from typing import List, Tuple


class TrackableObject:
	"""
	Represents a trackable object (person) in the video stream.
	
	Stores object ID, centroid history, and counting status.
	"""
	
	def __init__(self, objectID: int, centroid: Tuple[int, int]) -> None:
		"""Initialize a trackable object.
		
		Args:
			objectID: Unique identifier for this object
			centroid: Initial centroid coordinates as (x, y)
		"""
		# store the object ID, then initialize a list of centroids
		# using the current centroid
		self.objectID: int = objectID
		self.centroids: List[Tuple[int, int]] = [centroid]

		# initialize a boolean used to indicate if the object has
		# already been counted or not
		self.counted: bool = False