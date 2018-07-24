#!/usr/bin/python

# The program finds faces in a camera image or video stream and displays a red box around them.
import os
import time
import sys
import cv2.cv as cv
from datetime import datetime
import subprocess

APPLICATION_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
PICTURE_PATH = os.path.join(APPLICATION_PATH, "www", "media", "snapshots")


class CameraControl():
    def __init__(self):
        # Shows the detection video when set to True. Must run in graphics mode to work.
        self.showVideo = False

        self.min_size = (20, 20)
        self.image_scale = 2
        self.haar_scale = 1.2
        self.min_neighbors = 2
        self.haar_flags = 0

        self.cascade = None
        self.capture = None
        self.frame_copy = None

        self.is_finding_faces = False

    # return True if a face is found in an image
    def detect_no_draw(self, img):
        # allocate temporary images
        gray = cv.CreateImage((img.width, img.height), 8, 1)
        small_img = cv.CreateImage((cv.Round(img.width / self.image_scale),
                                    cv.Round(img.height / self.image_scale)), 8, 1)

        # convert color input image to grayscale
        cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

        # scale input image for faster processing
        cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
        cv.EqualizeHist(small_img, small_img)

        if self.cascade:
            t = cv.GetTickCount()
            faces = cv.HaarDetectObjects(small_img, self.cascade, cv.CreateMemStorage(0),
                                         self.haar_scale, self.min_neighbors, self.haar_flags, self.min_size)
            t = cv.GetTickCount() - t
        if faces:
            return True
        else:
            return False

    # draws a rectangle on a discovered face
    def detect_and_draw(self, img):

        # allocate temporary images
        gray = cv.CreateImage((img.width, img.height), 8, 1)
        small_img = cv.CreateImage((cv.Round(img.width / self.image_scale),
                                    cv.Round(img.height / self.image_scale)), 8, 1)

        # convert color input image to grayscale
        cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

        # scale input image for faster processing
        cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
        cv.EqualizeHist(small_img, small_img)

        if self.cascade:
            t = cv.GetTickCount()
            faces = cv.HaarDetectObjects(small_img, self.cascade, cv.CreateMemStorage(0),
                                         self.haar_scale, self.min_neighbors, self.haar_flags, self.min_size)
            t = cv.GetTickCount() - t
            #		print "time taken for detection = %gms" % (t/(cv.GetTickFrequency()*1000.))
            if faces:
                face_found = True

                for ((x, y, w, h), n) in faces:
                    # the input to cv.HaarDetectObjects was resized, so scale the
                    # bounding box of each face and convert it to two CvPoints
                    pt1 = (int(x * self.image_scale), int(y * self.image_scale))
                    pt2 = (int((x + w) * self.image_scale), int((y + h) * self.image_scale))
                    cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
            else:
                face_found = False

        cv.ShowImage("video", img)
        return face_found

    def is_device_connected(self):
        process = subprocess.Popen(["ls", "/dev/video0"], stdout=subprocess.PIPE)
        out, err = process.communicate()
        return 'video0' in out

    def use_camera(self):
        # global cascade, capture, frame_copy
        if not self.is_device_connected():
            return

        try:

            # if camera already openned
            if self.capture is not None:
                return

            if self.cascade is None:
                self.cascade = cv.Load(os.path.join(APPLICATION_PATH, "face.xml"))

            self.capture = cv.CreateCameraCapture(0)


            if self.showVideo:
                cv.NamedWindow("video", 1)

            self.set_resolution(640, 480)

            self.frame_copy = None

        except:
            self.close_camera()
            print "Error in use_camera"
            pass

    def close_camera(self):
        try:
            if self.showVideo:
                cv.DestroyWindow("video")

            if self.find_face_is_on():
                self.stop_find_face()

            del self.capture
            self.capture = None
        except:
            print "Error in close_camera"
            pass

    def camera_is_on(self):
        return (self.capture is not None)

    def find_face_is_on(self):
        return (self.is_finding_faces)

    def set_resolution(self, width, height):
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, width)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, height)

    def start_find_face(self):
        if not self.camera_is_on():
            self.use_camera()
            # return

        if not self.is_finding_faces:
            # self.set_resolution(160, 120)
            self.set_resolution(320, 240)
            self.is_finding_faces = True

    def stop_find_face(self):
        if not self.camera_is_on():
            return

        if self.is_finding_faces:
            self.set_resolution(640, 480)
            self.is_finding_faces = False

    def flushCameraBuffer(self):

        for i in range(6):
            cv.GrabFrame(self.capture)
            # if not cv.GrabFrame(self.capture):
            #     break;

    def found_face(self):
        # global frame_copy
        if (not self.camera_is_on()) or (not self.find_face_is_on()):
            return False

        self.flushCameraBuffer()  # this reduces the frame delay
        frame = cv.QueryFrame(self.capture)
        if frame is None:
            self.close_camera()
            return False

        if not frame:
            cv.WaitKey(0)
        if not self.frame_copy:
            self.frame_copy = cv.CreateImage((frame.width, frame.height),
                                             cv.IPL_DEPTH_8U, frame.nChannels)

        if frame.origin == cv.IPL_ORIGIN_TL:
            cv.Copy(frame, self.frame_copy)
        else:
            cv.Flip(frame, self.frame_copy, 0)

        if self.showVideo:
            result = self.detect_and_draw(self.frame_copy)
        else:
            result = self.detect_no_draw(self.frame_copy)
        cv.WaitKey(10)
        return result

    def take_snapshot(self):
        # get image from webcam
        if not self.camera_is_on():
            self.use_camera()

        self.flushCameraBuffer()  # this reduces the frame delay
        frame = cv.QueryFrame(self.capture)
        self.create_folder_if_not_exist()
        image_name = "capture_%s.jpg" % time.strftime("%y_%m_%d_%H_%M_%S")
        image_path = os.path.join(PICTURE_PATH, image_name)
        cv.SaveImage(image_path, frame)
        cv.SaveImage(os.path.join(PICTURE_PATH, "current.jpg"), frame)  # this is the preview image
        return image_name

    def take_preview_image(self):
        # get image from webcam
        if not self.camera_is_on():
            self.use_camera()

        self.flushCameraBuffer()  # this reduces the frame delay
        frame = cv.QueryFrame(self.capture)
        if frame is None:
            self.close_camera()
            return
        self.create_folder_if_not_exist()
        cv.SaveImage(os.path.join(PICTURE_PATH, "current.jpg"), frame)  # this is the preview image

    def create_folder_if_not_exist(self):
        if not os.path.exists(PICTURE_PATH):
            os.makedirs(PICTURE_PATH)

    def list_all_files(self):
        file_list = []

        for f in os.listdir(os.path.abspath(PICTURE_PATH)):
            name, ext = os.path.splitext(f)  # Handles no-extension files, etc.
            if ext == '.jpg':
                file_list.append("%s%s" % (name, ext))
        return file_list

    def list_images_and_time(self):
        file_list = self.list_all_files()
        return_list = []
        for filename in file_list:
            try:
                date_object = datetime.strptime(filename, 'capture_%y_%m_%d_%I_%M_%S.jpg')
            except:
                continue
            return_list.append([str(date_object), filename])
        return return_list

if __name__ == '__main__':

    c = CameraControl()

    c.use_camera()
    while 1:
        print c.face_found()
        time.sleep(0.5)
