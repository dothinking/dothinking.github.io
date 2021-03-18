---
keywords: TensorFlow tf.data.TFRecordDataset
tags: [TensorFlow]
---

# TensorFlow自定义数据集：tf.data.TFRecordDataset

2020-02-28

---

前文使用`tf.data.Dataset.list_files`创建文件路径`Dataset`并逐步载入图片数据的方式解决无法一次性加载所有图片数据到内存的问题，但依然存在频繁读文件的问题。本文参考TensorFlow官方文档读写图片例子 [^1]，将原来的图片数据以`TFRecord`文件形式进行存储，并重新载入`Dataset`和解析数据。

## 基本流程

`TFRecord`是一种存储二进制记录序列的简单格式，可以有效地进行 **线性读取** 数据。从创建到使用`TFRecord`文件的全流程：

- 获取源数据
- 写入`TFRecord`文件
- 读取和解析`TFRecord`文件

本文侧重点在获取源数据和拆分训练/测试数据集，读写`TFRecord`则直接参考官方示例 [^1] 的标准流程。


## 拆分数据集

习惯会按照一定比例，例如9:1拆分为训练和测试集。`Dataset`的`take`、`skip`、`shard`方法可以用于这个任务，但是或多或少存在一些不足：

- `take`和`skip`组合最为直接，但是需要知道数据集大小
- `shard`可以按间隔挑出一个子集，但是无法得到剩下的部分

!!! note "提示"
    `take`和`skip`需要在`shuffle`之前或者设置`shuffle`的`reshuffle_each_iteration=False`。否则不同的循环中，原来的`Dataset`已经改变顺序了，那么由此得到的`take`和`skip`会出现重叠元素。


以下参考思路 [^2]：

- `enumerate`得到元素的序号组合`(index, element)`
- `filter`筛选序号，利用两个相反的判断拆分为训练/测试两组（此时元素为`(index, element)`）
- `map`分别从拆分的两组中去掉辅助作用的序号


```python
def _split_train_test(file_pattern, test_rate, buffer_size):
    # by default, tf.data.Dataset.list_files always shuffles order during iteration
    # so set it false explicitly
    dataset = tf.data.Dataset.list_files(file_pattern, shuffle=False)
    
    # shuffle first and stop shuffling during each iteration
    # buffer_size is reccommanded to be larger than dataset size
    dataset = dataset.shuffle(buffer_size, reshuffle_each_iteration=False)

    # split train / test sets
    if test_rate:
        # define split interval
        sep = int(1.0/test_rate)
        is_test = lambda x, y: x % sep == 0
        is_train = lambda x, y: not is_test(x, y)
        recover = lambda x,y: y
        
        # split train/test set, and reset buffle mode: 
        # keep shuffle order different during iteration
        test_dataset = dataset.enumerate(start=1).filter(is_test).map(recover)
        train_dataset = dataset.enumerate(start=1).filter(is_train).map(recover)
    else:
        test_dataset, test_dataset = dataset, None
    
    return train_dataset, test_dataset
```


## 写入`TFRecord` 文件

基本套路：

- 准备`tf.train.Example`格式数据 [^3]，类似于字典`{"string": tf.train.Feature}`。

    其中`tf.train.Feature`存储具体数据，例如本例中的图片二进制字节和验证码字符串，当然也可以是数字格式的图片宽度、图片高度等。

    ```python
    def _image_example(path):
        """Create a dictionary with features: image raw data, label
            path: image path, e.g. b'test\\lcrh.jpg
        '"""
        # get image raw data and labels
        image_string = open(path, 'rb').read()
        image_labels = tf.strings.substr(path, -8, 4)
        
        # preparation for tf.train.Example
        feature = {
        'labels'   : tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_labels.numpy()])),
        'image_raw': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_string]))
        }
        
        return tf.train.Example(features=tf.train.Features(feature=feature))
    ```

- `tf.io.TFRecordWriter`将`tf.train.Example`序列化的值写入文件

    ```python
    # --------------------------------------------
    # Write raw image data to `images.tfrecords`
    # --------------------------------------------
    def write_images_to_tfrecord(image_file_pattern, # e.g. 'samples/*.jpg'
        dir_record, # folder for storing TFRecord files
        prefix_record='sample',
        split_test=0.1,  # split train/test rate
        buffer_size=10000):
        ''' load images and save to TFRecord file
                - get image raw data and labels (filename)
                - split into train / test sets
                - write to TFRecord file
        '''
        # split path dataset
        train_dataset, test_dataset = _split_train_test(image_file_pattern, split_test, buffer_size)

        # read image in train set and save to TFRecord file
        train_record = os.path.join(dir_record, f'{prefix_record}_train.tfrecords')
        with tf.io.TFRecordWriter(train_record) as writer:
            for path in train_dataset.as_numpy_iterator():
                tf_example = _image_example(path)
                writer.write(tf_example.SerializeToString())

        # read image in test set and save to TFRecord file
        if test_dataset:
            test_record = os.path.join(dir_record, f'{prefix_record}_test.tfrecords')
            with tf.io.TFRecordWriter(test_record) as writer:
                for path in test_dataset.as_numpy_iterator():
                    tf_example = _image_example(path)
                    writer.write(tf_example.SerializeToString())
        else:
            test_record = None

        return train_record, test_record
    ```


## 读取`TFRecord`文件

- 读入`TFRecord`文件得到`tf.data.TFRecordDataset`对象，继承自`tf.data.Dataset`。

    进而可以进行`map`、`shuffle`、`batch`等链式操作。

    ```python
    # --------------------------------------------
    # create dataset from TFRecord file
    # --------------------------------------------
    def create_dataset_from_tfrecord(record_file, 
        batch_size=32, 
        image_size=(60, 120), 
        label_prefix='labels',
        buffer_size=10000,
        grayscale=False): # load image and convert to grayscale
        '''create image/labels dataset from TFRecord file'''          
        return tf.data.TFRecordDataset(record_file).map(
            lambda example_proto: _parse_image_function(example_proto, image_size, label_prefix, grayscale),
            num_parallel_calls=tf.data.experimental.AUTOTUNE # -1 any available CPUs
        ).shuffle(buffer_size).batch(batch_size)
    ```

- `TFRecordDataset`中的元素是序列化后的`tf.train.Example`，配合`tf.io.parse_single_example`进行解析。

    上面代码块中的`_parse_image_function`即对其进行解析，得到存储其中的图片二进制文件流及验证码字符串`Tensor`。

    ```python
    def _parse_image_function(example_proto, image_size, label_prefix, grayscale):
        '''Parse the input tf.Example protocal using the dictionary describing the features'''
        image_feature_description = {
            'labels'   : tf.io.FixedLenFeature([], tf.string),
            'image_raw': tf.io.FixedLenFeature([], tf.string)
        }
        image_features = tf.io.parse_single_example(example_proto, image_feature_description)
        
        # decode image array and labels
        image_data = _decode_image(image_features['image_raw'], image_size, grayscale)
        dict_labels = _decode_labels(image_features['labels'], label_prefix)
        
        return image_data, dict_labels
    ```

- 最后转换图片二进制码为`RGB`数据、转换验证码各个字符为相应数字编码，作为模型训练的数据。

    ```python
    def _decode_image(image, resize, grayscale):
        '''preprocess image with given raw data
            - image: image raw data
        '''
        image = tf.image.decode_jpeg(image, channels=3)
        
        # convert to floats in the [0,1] range.
        image = tf.image.convert_image_dtype(image, tf.float32)
        image = tf.image.resize(image, resize)
        
        # RGB to grayscale -> channels=1
        if grayscale:
            image = tf.image.rgb_to_grayscale(image) # shape=(h, w, 1)

        return image # (h, w, c)


    def _decode_labels(labels, prefix):
        ''' this function is used within dataset.map(), 
            where eager execution is disables by default:
                check tf.executing_eagerly() returns False.
            So any Tensor.numpy() is not allowed in this function.
        '''
        dict_labels = {}
        for i in range(4):
            c = tf.strings.substr(labels, i, 1) # labels example: b'abcd'
            label = tf.strings.unicode_decode(c, input_encoding='utf-8') - ord('a')
            dict_labels[f'{prefix}{i}'] = label

        return dict_labels
    ```


[^1]: [Walkthrough: Reading and writing image data](https://tensorflow.google.cn/tutorials/load_data/tfrecord#walkthrough_reading_and_writing_image_data)
[^2]: [How do I split Tensorflow datasets?](https://stackoverflow.com/questions/51125266/how-do-i-split-tensorflow-datasets/51126863#51126863)
[^3]: [Data types for tf.Example](https://tensorflow.google.cn/tutorials/load_data/tfrecord#tfexample)