import cv2
import pickle
import math
from imutils.video import WebcamVideoStream
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
from sklearn import neighbors
from PIL import Image, ImageDraw
import os
import os.path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class VideoCamera(object):
    def __init__(self):
        #self.stream = stream
        self.stream = WebcamVideoStream(src=0).start()
        with open("facesmodel.clf", 'rb') as f:
            self.knn_clf = pickle.load(f)

    def __del__(self):
        self.stream.stop()

    def predict(self, frame, knn_clf, distance_threshold=0.4):
        face_locations = face_recognition.face_locations(frame)
        
        if len(face_locations) == 0:
            return []

        faces_encodings = face_recognition.face_encodings(frame, known_face_locations=face_locations)

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
        #       If the javascript face encoding algorithm works this code is broken from here.        #
        #             Imported encoding from javascript replaces python face encodings                #
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ << Comments by Mutai Tony >> #

        closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
        are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(face_locations))]
        
        return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in
                zip(knn_clf.predict(faces_encodings), face_locations, are_matches)]

    def get_frame(self):
        # +++++++++++++++++++++++++++++++++ THIS PART HAS TO GO +++++++++++++++++++++++++++++++++++++ #

        image = self.stream.read()

        # Replaced by the encodings from javascript                   
        # ++++++++++++++++++++++++++++++++++++++++++ END +++++++++++++++ << Comments by Mutai Tony >> #
        li = []
        
        f = open("trainStatus.txt")
        for i in f:
            isTrained = int(i)
        if isTrained:  
            with open("facesmodel.clf", 'rb') as f:
                self.knn_clf = pickle.load(f)
            file = open("trainStatus.txt", "w")
            file.write("0")
            file.close()
        predictions = self.predict(image, self.knn_clf)
        name = ''
        for name, (top, right, bottom, left) in predictions:
            startX = int(left)
            startY = int(top)
            endX = int(right)
            endY = int(bottom)
        # +++++++++++++++++++++++++++++++++ THIS PART HAS TO GO +++++++++++++++++++++++++++++++++++++ #

            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(image, name, (endX - 70, endY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        # ++++++++++++++++++++++++++++++++++++++++++ END +++++++++++++++ << Comments by Mutai Tony >> #

        # +++++++++++++++++++++++++++++++++ THIS PART HAS TO GO +++++++++++++++++++++++++++++++++++++ #

        ret, jpeg = cv2.imencode('.jpg', image)
        data = []
        data.append(jpeg.tobytes())
        data.append(name)
        #print(name)

        # Replace return data with return name                           
        # ++++++++++++++++++++++++++++++++++++++++++ END +++++++++++++++ << Comments by Mutai Tony >> #

        return data

    def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
        X = []
        y = []

        for class_dir in os.listdir(train_dir):
            if not os.path.isdir(os.path.join(train_dir, class_dir)):
                continue

            for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
                image = face_recognition.load_image_file(img_path)
                face_bounding_boxes = face_recognition.face_locations(image)

                if len(face_bounding_boxes) != 1:
                    if verbose:
                        print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
                else:
                    X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                    y.append(class_dir)

        if n_neighbors is None:
            n_neighbors = int(round(math.sqrt(len(X))))
            if verbose:
                print("Chose n_neighbors automatically:", n_neighbors)

        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit(X, y)

        if model_save_path is not None:
            with open(model_save_path, 'wb') as f:
                pickle.dump(knn_clf, f)

        return knn_clf