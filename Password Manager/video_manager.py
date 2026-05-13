import cv2
from pygrabber.dshow_graph import FilterGraph


class VideoManager:

    @staticmethod
    def list_cameras():
        """Returns a list of available camera devices."""
        graph = FilterGraph()
        cameras = graph.get_input_devices()
        return cameras
    
    @staticmethod
    def get_cap(camera_index):
        """Receives a camera index and returns a VideoCapture object for it. Returns None if the camera could not be opened."""
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return None
        else:
            return cap

    @staticmethod
    def get_frame(cap : cv2.VideoCapture):
        """Receives a VideoCapture object and returns a tuple containing a success flag,
        a mirrored RGB frame for display, and a small RGB frame for face recognition processing.\n
        If the frame could not be read, releases the capture and returns (False, )."""
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return (False, )
        
        mirrored_frame = cv2.flip(frame, 1)
        rgb_mirrored_frame = cv2.cvtColor(mirrored_frame, cv2.COLOR_BGR2RGB)

        small_frame = cv2.resize(frame, (0, 0), fx= 0.25, fy= 0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        return (True, rgb_mirrored_frame, rgb_small_frame)