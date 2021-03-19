---
categories: [machine learning]
tags: [TensorFlow]
---

# TensorFlow自定义数据集：tf.data.Dataset


---

当样本数据大到不能一次性载入内存时，TensorFlow推荐使用`tf.data.Dataset`创建样本的输入数据流，进而投喂给模型进行训练`model.fit(dataset)`。本文以带标签（即文件名）的验证码图片数据集为例，记录基本流程及一些备忘点。

## 基本流程

`tf.data.Dataset`的使用遵循基本的流程 [^1]：

- 从输入数据创建`Dataset`，例如`from_tensor_slices`，`list_files`
- 应用`Dataset`变换预处理数据，例如`map`、`filter`、`shuffle`、`batch`、`repeat`、`cache`等等
- 遍历`Dataset`并生成数据

针对本例中从文件夹读取图片的问题，我们直接可以从`tf.data.Dataset.list_files`开始。以下参考了TensorFlow手册 [^2] 中相关内容。


## 创建源数据集：`tf.data.Dataset.list_files`

该函数返回一个`Dataset`，其元素为满足给定模式的所有文件路径，并且元素默认 **随机**、**不确定** 排列。**不确定** 指的是每次遍历时得到的顺序都不一样。

如果需要得到固定的顺序，可以设置一个确定的`seed`或者关闭打乱选项`shuffle=False`。

```python
list_files(
    file_pattern, shuffle=None, seed=None
)
```

- `file_pattern` 需要载入文件的路径模式，例如`samples/*.jpg`
- `shuffle` 是否打乱数据集，默认**是**
- `seed` 用以打乱数据集的随机数种子


## 数据集变换预处理数据

我们已经得到了文件名，但真正需要喂给模型的是图片本身及其标签，所以需要在这个源数据集上进行变换操作。也就是说，`Dataset`的元素应满足`(X, Y)`的形式，当包含多特征的输入或输出，例如本例中输出四位的验证码，可以以字典的形式构造`(X, Y)`元组中的`X`或`Y`：

```python
(image_raw_data, {
  'label_1': 'A',
  'label_2': 'b',
  'label_3': 'c',
  'label_4': 'D'
  })
```

!!! warning "注意"
    当定义多输入多输出的模型结构时，输入输出的名称应与此处的定义前后一致 [^3]。


### `tf.data.Dataset.map`

TensorFlow提供了`map`函数将预定义的变换操作`map_func`作用在`Dataset`的每一个元素上，然后返回这个新的`Dataset`。

```python
map(
    map_func, num_parallel_calls=None
)
```

- `map_func` 以原来`Dataset`中的元素为参数的自定义函数，返回新`Dataset`中相应的元素
- `num_parallel_calls` 并行处理元素的个数，默认顺序执行

需要注意的是`map`函数以`Graph`的形式执行自定义的`map_func`，因此`EagerTensor`的性质例如`numpy()`将不可用。如果非用不可，API文档 [^1] 中提及了使用`tf.py_function`转换的形式，但是以性能损失为代价。

具体到本例中，

```python
path_pattern = 'samples/*.jpg'

dataset = tf.data.Dataset.list_files(path_pattern).map(
        lambda image_path: (
          _decode_image(image_path),  # load images, perform transformation as X
          _decode_labels(image_path)  # parse labels as Y
    ))
```

### `tf.data.Dataset.shuffle`

`shuffle`打乱当前`Dataset`并返回乱序后的`Dataset`，方便链式操作。

```python
shuffle(
    buffer_size, seed=None, reshuffle_each_iteration=None
)
```

- `buffer_size` 缓冲区大小。元素被依次填入缓冲区，然后从中随机取出以达到打乱效果。因此，`buffer_size`越大，乱序效果越好，但性能随之下降。
- `seed` 打乱用的随机数种子
- `reshuffle_each_iteration` 是否每次遍历时都自动打乱，默认 **是**。避免不同`epoch`的训练过程中，`Dataset`保持一致的顺序。


### `tf.data.Dataset.batch`

将一定数量的元素组织为一个`batch`，得到新的`Dataset`。同为链式操作。

```python
batch(
    batch_size, drop_remainder=False
)
```

- `batch_size` 批次的大小
- `drop_remainder` 当原来样本数量不能被`batch_size`整除时，是否丢弃最后剩下的不足一个批次的样本。默认 **保留**。


此外，`Dataset`还有一些列实用的操作，例如`filter`筛选元素、`cache`提升性能，具体操作API文档 [^1]。



## 代码汇总

```python
import tensorflow as tf

# --------------------------------------------
# create dataset from path pattern
# --------------------------------------------
def create_dataset_from_path(path_pattern, 
    batch_size=32, 
    image_size=(60, 120), 
    label_prefix='labels',
    grayscale=False): # load image and convert to grayscale
    # create path dataset
    # by default, `tf.data.Dataset.list_files` gets filenames 
    # in a non-deterministic random shuffled order
    return tf.data.Dataset.list_files(path_pattern).map(
        lambda image_path: _parse_path_function(image_path, image_size, label_prefix, grayscale)
    ).batch(batch_size)


def _parse_path_function(path, image_size, label_prefix, grayscale):
    '''parse image data and labels from path'''
    raw_image = open(path, 'rb').read()
    labels = tf.strings.substr(path, -8, 4) # path example: b'xxx\abcd.jpg'
    # decode image array and labels
    image_data = _decode_image(raw_image, image_size, grayscale)
    dict_labels = _decode_labels(labels, label_prefix)

    return image_data, dict_labels


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

至此可以将整个文件夹的图片喂给模型训练了，但是数十万张图片既不方便传输、频繁读文件操作也影响性能，因此下篇将所有数据写入`TFRecord`文件，然后使用`tf.data.TFRecordDataset`导入。




[^1]:  [tf.data.Dataset](https://tensorflow.google.cn/api_docs/python/tf/data/Dataset?hl=en)
[^2]:  [Load Images using tf.data](https://tensorflow.google.cn/tutorials/load_data/images#load_using_tfdata)
[^3]:  [Models with multiple inputs and outputs](https://tensorflow.google.cn/guide/keras/functional#models_with_multiple_inputs_and_outputs)