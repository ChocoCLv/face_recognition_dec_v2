import shutil
import os
import random

raw_dir = './raw'
trainset_dir = './trainset'
testset_dir = './testset'
trainset_num = 900
testset_num = 100


def main():
    dir_list = os.listdir(raw_dir)
    for i in range(0, len(dir_list)):
        raw_path = os.path.join(raw_dir, dir_list[i])
        testset_path = os.path.join(testset_dir, dir_list[i])
        trainset_path = os.path.join(trainset_dir, dir_list[i])

        if not os.path.exists(testset_path):
            os.mkdir(testset_path)
        if not os.path.exists(trainset_path):
            os.mkdir(trainset_path)

        if os.path.isdir(raw_path):
            image_list = os.listdir(raw_path)
            random.shuffle(image_list)

            for j in range(0, trainset_num):
                spath = os.path.join(raw_path, image_list[j])
                filename = dir_list[i] + '-' + str(j) + '.jpg'
                dpath = os.path.join(trainset_path, filename)
                shutil.copyfile(spath, dpath)
                print('copy trainset for ' + dir_list[i] + '  ' + str(j) +
                      '/' + str(trainset_num))

            for j in range(trainset_num, trainset_num + testset_num):
                spath = os.path.join(raw_path, image_list[j])
                filename = dir_list[i] + '-' + str(j) + '.jpg'
                dpath = os.path.join(testset_path, filename)
                shutil.copyfile(spath, dpath)
                print('copy testset for ' + dir_list[i] + '  ' + str(j-trainset_num) +
                      '/' + str(testset_num))



if __name__ == '__main__':
    main()
