# coding=utf-8
import sys
import os
sys.path.append(sys.path[0] + '/app')

import time

import cv2
import argparse

import settings
from video_processor import VideoProcessor
import recognition_result_processor
import log
from queue import Queue
from plc_control import PLCControl
import face_util.face
from face_util.recognizer import Recognition

frame_queue = Queue(1)


class Camera:
    def __init__(self, username, password, ip):
        self.username = username
        self.password = password
        self.url = 'rtsp://{username}:{password}@{ip}/cam/realmonitor?channel=1&subtype=0'.format(
            username=username, password=password, ip=ip)

    def get_url(self):
        return self.url


class facerec_app:
    def __init__(self):
        self.camera = Camera(settings.USERNAME, settings.PASSWORD, settings.IP)
        self.resize_factor = settings.RESIZE_FACTOR

    def add_overlays(self, frame, faces):
        if faces is not None:
            factor = int(1 / self.resize_factor)
            for face in faces:
                face_bb = face.bounding_box.astype(int) * factor

                cv2.rectangle(frame, (face_bb[0], face_bb[1]),
                              (face_bb[2], face_bb[3]), (0, 255, 0), 2)
                if face.name is not None:
                    cv2.putText(
                        frame,
                        face.name, (face_bb[0], face_bb[3]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0),
                        thickness=2,
                        lineType=2)

    def run(self, args):
        if (args.use_svm):
            settings.USE_SVM = True
            print('use svm')
        else:
            settings.USE_SVM = False
            print('use distance')
        plc = PLCControl()
        face_recognition = Recognition()
        video_capture = VideoProcessor(
            self.camera.get_url(), output_queue=frame_queue)
        video_capture.start_processing()
        while True:
            # Capture frame-by-frame
            frame = video_capture.get_latest_frame()
            if frame is None:
                continue

            faces = face_recognition.identify(frame)
            legal = False
            for f in faces:
                recognition_result_processor.put_result(f.result)
                recognition_result_processor.send_email(f.result)
                if (f.result.result == settings.LEGAL):
                    legal = True

            if len(faces) > 0:
                recognition_result_processor.push_result()

            if legal:
                plc.open_door()

            self.add_overlays(frame, faces)
            if args.debug:
                cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything is done, release the capture
        video_capture.stop_processing()
        video_capture.cleanup()
        cv2.destroyAllWindows()


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--use_svm',
        type=bool,
        help='use svm to identify class or just compare distance',
        default=True)
    parser.add_argument(
        '--debug',
        type=bool,
        help='show image or not',
        default=True)
    return parser.parse_args(argv)


if __name__ == '__main__':
    app = facerec_app()
    print('real_time_face_recognition start')
    app.run(parse_arguments(sys.argv[1:]))
