
from Maix import GPIO, I2S, FFT
import image, lcd, math,sensor

from fpioa_manager import fm

sample_rate = 19820#38640
sample_points = 1024
fft_points = 512
hist_x_num = fft_points/4

lcd.init(freq=15000000, color=65535, invert=0)#一些屏幕基本配置
sensor.reset()                      # Reset and initialize the sensor. It will
                                    # run automatically, call sensor.run(0) to stop
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(10)
#sensor.skip_frames(time = 100)     # Wait for settings take effect.
sensor.set_vflip(1)
fm.register(20,fm.fpioa.I2S0_IN_D0, force=True)
fm.register(19,fm.fpioa.I2S0_WS, force=True)
fm.register(18,fm.fpioa.I2S0_SCLK, force=True)

rx = I2S(I2S.DEVICE_0)
rx.channel_config(rx.CHANNEL_0, rx.RECEIVER, align_mode = I2S.STANDARD_MODE)
rx.set_sample_rate(sample_rate)#设置采样率 38640

img = image.Image()
if hist_x_num > 320:
    hist_x_num = 320
hist_width = int(320 / hist_x_num)#矩形的宽度
x_shift = 0
while True:
    img = img.clear()
    audio = rx.record(sample_points)#接收音频信号 1024
    fft_res = FFT.run(audio.to_bytes(),fft_points)#运算函数 频域
    fft_amp = FFT.amplitude(fft_res)#赋值函数.
    img = sensor.snapshot()         # Take a picture and return the image.
    img = img.draw_string([80,80][0],[0,0][1],"FFT_512points",(255,0,255),2,mono_space=0)#画字符串
    img = img.draw_string([60,60][0],[30,30][1],"sample rate = 19820",(255,0,255),2,mono_space=0)#画字符串
    for i in range(fft_points/4):
        fft_amp[i+1] = 2*fft_amp[i+1]
    cc = len(fft_amp)
    print(cc);
    x_shift = 0
    for i in range(hist_x_num):
        if fft_amp[i] > 240:
            hist_height = 240
        else:
            hist_height = fft_amp[i]
        #绘制方块                  x        y                   x           y
        img = img.draw_rectangle((x_shift,240-hist_height,hist_width,hist_height),[256,134,0],1)
        x_shift = x_shift + hist_width
    lcd.display(img)
    fft_amp.clear()
