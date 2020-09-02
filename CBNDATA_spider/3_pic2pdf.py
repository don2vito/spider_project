from PIL import Image
import os
import time
import pandas as pd

def pic2pdf(path,output_path,pdf_name):
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
    # print("hec", new_pic)
    try:
        pdf_file = Image.open(os.path.join(path, new_pic[0]))
        new_pic.pop(0)
        for i in new_pic:
            try:
                img = Image.open(os.path.join(path, i))
                # im_list.append(Image.open(i))
                if img.mode == "RGBA":
                    img = img.convert('RGB')
                    im_list.append(img)
                else:
                    im_list.append(img)
            except OSError:
                pass
        pdf_file.save(os.path.join(output_path,pdf_name), "PDF", resolution=100.0, save_all=True, append_images=im_list)
        print('{} 生成完成！！'.format(pdf_name))
    except IndexError:
        pass


if __name__ == '__main__':
    t1 = time.time()

    urls_data = pd.read_csv('./data_tables/spidered_urls.csv', sep=',', encoding='utf-8', engine='python')
    titles_list = list(urls_data['title'])

    temp_data = pd.read_csv('./data_tables/created_pdfs.csv', sep=',', encoding='utf-8', engine='python')
    temp_titles_list = list(temp_data['title'])

    titles_set = set(titles_list)
    temp_titles_set = set(temp_titles_list)

    true_titles_set = titles_set - temp_titles_set

    ture_titles_list = list(true_titles_set)

    folder_names = os.listdir('./data_pictures')
    for folder_name in ture_titles_list:
        output_path = './data_reports'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        path = os.path.join('./data_pictures',folder_name)
        # print(path)

        data = {
            'title': folder_name,
        }

        pdf_name = folder_name + '.pdf'
        if ".pdf" in pdf_name:
            pic2pdf(path=path,output_path=output_path,pdf_name=pdf_name)
        else:
            pic2pdf(path=path,output_path=output_path,pdf_name="{}.pdf".format(pdf_name))

        temp_data = temp_data.append(data, ignore_index=True)
        temp_data.to_csv(os.path.join('./data_tables', 'created_pdfs.csv'), sep=',', header=True, index=False,encoding='utf-8', columns=['title'])
        print('追加《{}》数据完成！！'.format(folder_name))

    t2 = time.time()
    print('运行共耗时： {:.1f}秒'.format(t2 - t1))