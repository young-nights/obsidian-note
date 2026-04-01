<style>
.highlight{
  color: white;
  background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
  padding: 5px;
  border-radius: 5px;
}

.mint_green{
  color: white;
  background: #adcdadf2; 
  padding: 5px;
  border-radius: 5px;
}

.red {
  color: #ff0000;
}
.green {
  color:rgb(10, 162, 10);
}
.blue {
  color:rgb(17, 0, 255);
}

.wathet {
  color:rgb(0, 132, 255);
}
</style>


# <span class="wathet"><font size=4>B站开源文本转语音IndexTTS项目</font></span>
## <font size=3>一、安装 ffmpeg</font>
<font size=2>
<div style="background:#e8f5e8;padding:10px;border-radius:6px;color:#333;">
ℹ️ <span class="red">FFmpeg是一个开源的多媒体框架</span>，能够记录、转换和流媒体<span class="red">处理音视频数据</span>，它包含了一系列的工具和库，支持大量的多媒体格式，并能在不同的操作系统上运行，包括Windows、MacOS和Linux等。<br>
</div>

[📑Windows安装FFmpeg](./Windows安装FFmpeg.md)
</font>

## <font size=3>二、安装 Miniconda</font>
<font size=2>
<div style="background:#e8f5e8;padding:10px;border-radius:6px;color:#333;">
ℹ️ <span class="red">Conda 是一个开源的软件包管理和环境管理系统，</span>适用于多种语言（如Python、R等），主要用于数据科学，机器学习等领域。它不仅能够帮助用户<span class="red">安装和管理软件包，</span>还能<span class="red">创建和管理独立的运行环境</span>，以便于处理不同项目间的依赖关系冲突。Conda通过其强大的依赖解析能力，可以确保安装的所有软件包和谐共存。<br>
▪️ 跨平台支持：可在Windows、macOS和Linux上使用。<br>
▪️ 环境管理：允许用户轻松创建、导出、列出和移除虚拟环境。<br>
▪️ 包管理：提供从Anaconda仓库及其他第三方源中搜索、安装和更新软件包的能力。<br>
▪️ 依赖解决：自动解决软件包之间的依赖关系。<br>

 **<span class="red">Miniconda 是 Conda 的一个最小发行版本，仅包含Conda包管理和Python解释器，没有预装任何其他软件包</span>**。他是获取Conda功能的一种轻量级方式，让用户可以从头开始构建自己的软件包集合和环境。

▪️轻量化安装：相比于完整版的Anaconda，Miniconda的安装文件小得多，因为它只包含了最基本的功能。
▪️灵活性：用户可以根据需要自行选择要安装的软件包，而不是一开始就安装大量可能用不到的软件包。
▪️全面兼容：尽管是精简版，但Miniconda仍然提供了全部的Conda功能，包括环境和包管理能力。
</div>

[📑Windows安装 miniconda](./Windows安装Miniconda.md)

</font>


## <font size=3>三、创建项目conda环境</font>
<font size=2>

```bash
#先创建index-tts项目环境同时配置指定版本的Python环境
conda create -n index-tts python=3.10
#再激活这个项目环境
conda activate index-tts
```
</font>


## <font size=3>四、安装 Pynini</font>
<font size=2>
<div style="background:#e8f5e8;padding:10px;border-radius:6px;color:#333;">
ℹ️ Pynini 是一个基于开源的有限状态转换器(Finite-State Transducer, FST)库——OpenFst 的 Python 绑定。它允许用户在Python环境中利用有限状态机的强大功能进行字符串处理、自然语言处理(NLP)等任务。Pynini特别适用于需要复杂规则和转换的应用场景，例如拼音纠正、形态分析、语音识别中的语言模型构建等。

在语音识别合成系统中 **<span class="red">Pynini可用于开发语音模型，帮助提高识别准确率或生成更加自然的声音输出</span>**<br>
</div>
<br>

```bash
#代码块
conda install -c conda-forge pynini==2.1.6
pip install WeTextProcessing --no-deps
```
</font>


## <font size=3>五、安装 PyTorch</font>
<font size=2>
<div style="background:#e8f5e8;padding:10px;border-radius:6px;color:#333;">

ℹ️ **<span class="red">PyTorch 是一个开源的机器学习库</span>** ，主要用于自然语言处理、计算机视觉等领域中的应用，是学术界和工业界 **<span class="red">广泛使用的深度学习框架之一</span>**。
</div>

[📑安装 PyTorch](./安装Pytroch.md)


</font>


## <font size=3>六、下载代码</font>
<font size=2>

<div style="background:#fdecea;padding:10px 12px;border-left:4px solid #f66;border-radius:4px;color:#333;">
这里特别说明一下，这个教程是笔者根据B站上的 FutureAI实验室 这个up主的内容复刻它敲出来的，由于代码更新迭代，完全按照up的步骤进行配置会产生无法运行的问题，下面会详细说明，这里可行的代码会上传到笔者自己的github上，因此就不写克隆官方代码的方案了。
</div>

[📑问题详述](./问题详述.md)

```bash
# 点击鼠标右键，打开gitbash，运行以下代码下载官网的v1.5.0版本代码
# --depth 1 表示只下载该 Tag 的快照，不带其他历史，体积最小
git clone --branch v1.5.0 --depth 1 https://github.com/index-tts/index-tts.git

#或者通过下面这个链接直接下载
```

</font>



## <font size=3>七、安装项目依赖</font>

<font size=2>

```bash
#先转到指定盘符（此处以D盘为例）
D：
#再转到index-tts代码文件下
cd D:\Github-source-code\index-tts
#然后安装依赖
pip install -e .
pip install gradio modelscope

```
</font>



## <font size=3>八、模型下载</font>
<font size=2>

<div style="background:#e8f5e8;padding:10px;border-radius:6px;color:#333;">

ℹ️ <span class="wathet">IndexTTS 目前有两个版本，分别为 IndexTTS 和 IndexTTS-1.5 </span> ，**<span class="red">1.5版本显著提升了模型的稳定性和英语语言性能</span>**。根据需要选择一个版本下载即可
</div>

**IndexTTS-1.5**

```bash
modelscope download --model IndexTeam/IndexTTS-1.5 --local_dir models/IndexTTS-1.5
```

**IndexTTS**

```bash
modelscope download --model IndexTeam/IndexTTS --local_dir models/IndexTTS
```

</font>


## <font size=3>九、启动Web界面</font>
**IndexTTS-1.5**

```bash
python webui.py --model_dir models/IndexTTS-1.5
```

**IndexTTS**

```bash
python webui.py --model_dir models/IndexTTS
```



