mkdir -p models

curl -L -o models/colorization_deploy_v2.prototxt \
https://raw.githubusercontent.com/richzhang/colorization/caffe/models/colorization_deploy_v2.prototxt

curl -L -o models/colorization_release_v2.caffemodel \
"https://www.dropbox.com/scl/fi/d8zffur3wmd4wet58dp9x/colorization_release_v2.caffemodel?rlkey=iippu6vtsrox3pxkeohcuh4oy&dl=1"

curl -L -o models/pts_in_hull.npy \
https://github.com/richzhang/colorization/raw/caffe/colorization/resources/pts_in_hull.npy