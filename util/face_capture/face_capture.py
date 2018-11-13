# coding=utf-8
import cv2
import sys
sys.path.append('../../app/face_util')
sys.path.append('../../app')
import settings
import os
import argparse
from face import Face
from detector import Detection


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str, help='当前录制人员的id')
    return parser.parse_args(argv)


def add_overlays(frame, faces):
    if faces is not None:
        factor = int(1 / settings.RESIZE_FACTOR)
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


def main(args):
    capture = cv2.VideoCapture(
        'rtsp://{username}:{password}@{ip}/cam/realmonitor?channel=1&subtype=0'
        .format(
            username=settings.USERNAME,
            password=settings.PASSWORD,
            ip=settings.IP))
    detection = Detection()
    num = 0
    path = 'faces'
    if not os.path.exists(path):
        os.mkdir(path)
    path = path + '/' + args.id
    if not os.path.exists(path):
        os.mkdir(path)
    print('capture faces for : ', str(args.id))
    while True:
        ret_val, frame = capture.read()
        if (not ret_val):
            continue
        faces = detection.find_faces(frame)
        for face in faces:
            filename = path + '/' + str(num) + '.jpg'
            if num % 10 == 0:
                cv2.imwrite(filename, face.image)
            num = num + 1
        add_overlays(frame, faces)

        if settings.SHOW_IMAGE:
            cv2.imshow('face capture', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print('capture faces num: ', str(num))


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))