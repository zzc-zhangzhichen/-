# s1_getTrafficData.py
# -*- coding: utf-8 -*-
import http, time, random, os
import urllib.request


# http://its.map.baidu.com:8002/traffic/TrafficTileService?time=1604900544967&v=016&level=19&x=98760&y=19742
# 百度地图切片原点左下角，(x, y)，x为列，y为行
# 研究范围：左下(98697, 19700) - 右上(98787, 19766)


def getUserAgent():
    agent_list = [
        "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'
    ]
    agent = random.choice(agent_list)
    header = (
        'User-Agent', agent
    )

    return header


def getProxy():
    ip_list = [
        "http://117.93.118.88:3000",
        "http://111.177.192.57:3256",
        "http://112.195.242.60:3256",
        "http://124.205.153.81:80",
        "http://49.85.2.17:3000"
        "http://117.88.208.32:3000",
        "http://114.99.9.117:1133",
        "http://125.72.106.132:3256",
        "http://49.85.188.37:8014",
        "http://124.206.34.66:80",
        "http://117.68.192.93:1133",
        "http://114.233.170.151:8056",
        "http://60.168.207.147:1133",
        "http://114.233.170.48:8056",
        "http://1.70.67.20:9999",
        "http://121.226.215.247:9999",
        "http://114.233.194.202:8086",
        "http://114.112.127.78:80",
        "http://117.66.233.26:9999",
        "http://180.122.38.235:8090",
        "http://117.95.192.119:9999",
        "http://49.85.188.21:8058",
        "http://114.233.168.211:8088",
        "http://180.120.209.130:8888",
    ]
    ip = random.choice(ip_list)
    proxy = urllib.request.ProxyHandler({'http': ip})
    return proxy


def requestImg(proxy, header, url, file_name):
    if os.path.exists(file_name):
        return proxy, header
    try:

        opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
        opener = urllib.request.build_opener()
        opener.addheaders = [header]
        urllib.request.install_opener(opener)

        # req=urllib.request.Request(url=url,headers=header)
        # res = urllib.request.urlopen(url, timeout=60)
        req = urllib.request.Request(url)
        res = opener.open(req, timeout=30)
        with open(file_name, "wb") as f:
            content = res.read()
            f.write(content)
            res.close()
    # except urllib.error.HTTPError or urllib.error.URLError as e:
    #     print(e.reason)
    # except http.client.IncompleteRead or http.client.RemoteDisconnected as e:
    #     if num_retries == 0: # 重连机制
    #         return
    #     else:
    #         requestImg(proxy, header, url, file_name, num_retries - 1)
    except:
        print("exception...")
        proxy = getProxy()
        header = getUserAgent()
        proxy, header = requestImg(proxy, header, url, file_name)

    return proxy, header


if __name__ == "__main__":

    # 3.15-3.21 7:00-20:00
    day_index = 2
    hour_index = 4

    for i in range(1, day_index):
        for j in range(hour_index):
            t = 1615766400000 + i * 86400000 + j * 1800000
            dir_path = "./wuhan/images_" + str(i) + "_" + str(j)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            base_url = "http://its.map.baidu.com:8002/traffic/TrafficTileService?level=17&v=016&time="

            reset_clock = 50
            proxy = getProxy()
            header = getUserAgent()

            for x in range(24816, 24937):
                for y in range(6911, 6985):
                    url = base_url + str(t) + "&x=" + str(x) + "&y=" + str(y)
                    file_name = dir_path + "/" + str(x) + "-" + str(y) + '.png'

                    # 每50次更换ip、header
                    if reset_clock == 0:
                        proxy = getProxy()
                        header = getUserAgent()
                        reset_clock = 50

                    # 请求
                    proxy1, header1 = requestImg(proxy, header, url, file_name)
                    proxy = proxy1
                    header = header1
                    reset_clock = reset_clock - 1  # 重置时钟-1

                    print(i, j, x, y)
                    time.sleep(random.random())

                    # 每次请求如果遇到随机数66，暂停20s
                    if random.randint(1, 100) == 66:
                        print("sleeping......")
                        time.sleep(20 * random.random())

            # 某天某时所有请求完毕时，停留久一点
            time.sleep(random.uniform(100, 300))

    print("------ok------")


# s2_replaceEmpty
# -*- coding: utf-8 -*-
#!/usr/bin/env python

import glob, re
from PIL import Image

d = 2
t = 4

#for i in range(d):
for i in range(1,2):
    for j in range(t):
        p = './wuhan/images_'+str(i)+ '_' + str(j)  +'/*.png'

        # 按照x、y顺序对文件名进行排序
        files = glob.glob(p)
        for x in files:
            try:
                img = Image.open(x)
                img.close()
            except:
                img = Image.new(mode='RGBA', size=(256, 256))
                img.save(x)
# s3_mergeImages.py
# -*- coding: utf-8 -*-
# !/usr/bin/env python
import glob, re
from PIL import Image

d = 2
t = 4

for i in range(1,2):
    for j in range(t):
        s = './wuhan/images_' + str(i) + '_' + str(j) + '/*.png'

        # 按照x、y顺序对文件名进行排序
        files = glob.glob(s)
        files.sort(key=lambda x: tuple(int(i) for i in re.findall(r'\d+', x)[2:4]))

        # 将每一行文件名保存到一个数组中
        imagefiles = {}
        for item in files:
            match = re.findall(r'\d+', item)
            # pre = int(match.group())
            pre = match[2]

            if not imagefiles.get(pre):
                imagefiles[pre] = []

            imagefiles[pre].append(item)

        # 键值对转排序后的列表
        imagefiles = sorted(zip(imagefiles.keys(), imagefiles.values()))

        # 预先生成合并后大小的空图片
        total_width = len(imagefiles) * 256
        total_height = len(imagefiles[0][1]) * 256
        new_image = Image.new("RGBA", (total_width, total_height))

        # 逐行拼接
        x_offset = 0
        for item in imagefiles:
            y_offset = total_height - 256
            images = list(map(Image.open, item[1]))  # 映射函数，返回列表
            for subitem in images:
                new_image.paste(subitem, (x_offset, y_offset))
                y_offset -= subitem.size[0]
            x_offset += images[0].size[0]

        f_name = "./merge/merge_" + str(i) + "_" + str(j) + ".png"
        new_image.save(f_name, quality=100)

