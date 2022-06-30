import requests
from lxml import etree
import os
import time
from PIL import Image

def get_src(url,headers):
    headers = headers
    
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)
    
    pic_names = selector.xpath('//*[@id="post-1452407"]/div/p/a/img/@src')
    return pic_names


def download_pics(path,headers,pic_names):
    output_path = path
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    headers = headers
    
    n = 1
    for pic in pic_names:
        pic_data = requests.get(pic, headers=headers)
        try:
            fp = open(os.path.join(output_path, str(n + 100) + '.jpg'),'wb')
        except ConnectionError:
            fp = open(os.path.join(output_path, str(n + 100) + '.jpg'),'wb')
        fp.write(pic_data.content)
        fp.close()
        print(f'第{n}张图片已保存……')
        n = n + 1


def pic2pdf(path, pdf_name):
    file_list = os.listdir(path)
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(x)
    pic_name.sort()

    new_pic = []
    for x in pic_name:
        if "jpg" in x:
            new_pic.append(x)
    for x in pic_name:
        if "png" in x:
            new_pic.append(x)
    for x in pic_name:
        if "jpeg" in x:
            new_pic.append(x)
            
    pdf_file = Image.open(os.path.join(path, new_pic[0]))
    new_pic.pop(0)
    for i in new_pic:
        img = Image.open(os.path.join(path, i))
        # im_list.append(Image.open(i))
        if img.mode == "RGBA":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    pdf_file.save(os.path.join(path,pdf_name), "PDF", resolution=100.0, save_all=True, append_images=im_list)
    print('{} 生成完成！！'.format(pdf_name))
    
    
def main():
    path = './pics'
    headers = {
              'Content-Type': 'application/json;charset=utf-8',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
              }
    url = 'http://www.199it.com/archives/1452407.html'
    pdf_name = '618电商营销全景洞察.pdf'
    
    t1 = time.time()
    pic_list = get_src(url,headers)
    download_pics(path,headers,pic_list)    
    if ".pdf" in pdf_name:
        pic2pdf(path=path, pdf_name=pdf_name)
    else:
        pic2pdf(path=path, pdf_name="{}.pdf".format(pdf_name))
    t2 = time.time()
    print(f'共耗时{t2 - t1:.2f}秒！')


if __name__ == '__main__':
    main()
    