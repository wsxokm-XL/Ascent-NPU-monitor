# Ascent-NPU-monitor
A progress for ascent npu monitor

![54816fbbacf8fa5914586665db5aae6](https://github.com/user-attachments/assets/fac4f774-2788-4c6f-9eb0-5414e8bfbe8e)

## 脚本下载
```bash
mkdir /usr/local/npu-monitor
cd /usr/local/npu-monitor
wget https://gitee.com/youwantto/Ascent-NPU-monitor/blob/main/monitor
wget https://gitee.com/youwantto/Ascent-NPU-monitor/blob/main/show_smi.py
wget https://gitee.com/youwantto/Ascent-NPU-monitor/blob/main/config.ini
```

## 脚本使用
1.  需要python安装 `prettytable` 和 `configparser` 库:
    ```bash
    pip install prettytable
    pip install configparser 
    ```
2.  给shell脚本添加可执行权限：

    ```bash
    chmod +x monitor
    ```
3.  运行脚本：

    ```bash
    # 静态查看npu
    ./monitor

    # 动态查看npu
    ./monitor watch
    # 按q退出monitor
    
    ```
4.  修改环境变量 （按需）：

    将脚本所在路径加入 `~/.bashrc` 配置中

    使环境变量修改生效：`source ~/.bashrc`

    之后可以直接通过 `monitor` 命令运行

5.  配置文件 `config.ini`:
    ```{config.ini}
    [config]
    npu_num = 8
    
    [chart]
    chart_his_max_length = 30
    use_threshold1 = 20
    use_threshold2 = 70
    ```
    npu_num参数为npu数量，chart_his_max_length参数为展示的内存使用率、npu使用率柱状图总长度，use_threshold1，use_threshold2为内存使用率、npu使用率的两个阈值，20，70表示使用率20以下展示颜色为绿色，20-70为黄色，70以上为红色。
    

   
