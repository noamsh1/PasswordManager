import face_recognition
import dlib
import numpy as np

class FaceRecognizer:

    @staticmethod
    def get_face_encodings(rgb_frame):
        """Receives an RGB frame, detects faces and returns the face encoding of the first face found as binary data.
        Returns None if no face was detected."""
        face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample= 2, model= "hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not face_encodings:
            return None
        else:
            encoding_array = face_encodings[0]
            bin_face_encoding = encoding_array.astype(np.float64).tobytes()
            return bin_face_encoding

    
    @staticmethod
    def compare_faces(stored_bin_face_encoding, bin_face_encoding):
        """Receives a stored face encoding and a login face encoding as binary data,
        compares the two face encodings and returns True if they match, False otherwise."""
        if not bin_face_encoding or not stored_bin_face_encoding:
            return False
        
        stored_face_encoding = np.frombuffer(stored_bin_face_encoding, dtype= np.float64)
        face_encoding = np.frombuffer(bin_face_encoding, dtype= np.float64)

        matches = face_recognition.compare_faces([stored_face_encoding], face_encoding)
        
        if True in matches:
            return True
        else:
            return False