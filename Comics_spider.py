import os
import re
import time
import requests


class Comics_spider:
    index_prefix_url='http://www.90mh.com/manhua/'
    index_comic_name_url='chongshi'
    index_suffix_url='.html'

    pic_prefix_url='https://js.tingliu.cc/images/comic/'
    pic_comic_url=80
    chapter_url=158906

    #主函数
    def main(self):
        html=self.request_index_url()
        result=self.parse_result(html)
        self.load_a_chapter_to_file(result)

    #请求网页源码
    def request_index_url(self):
        index_url =self.index_prefix_url+self.index_comic_name_url+'/'+str(self.chapter_url)+self.index_suffix_url
        try:
            response=requests.get(index_url)
            if response.status_code==200:
                return response.text
        except requests.RequestException:
            return None

    #解析网页
    def parse_result(self,index_html):
        #使用正则表达式匹配出图片列表
        img_list_txt=re.search('var chapterImages = (.*?);',index_html).group(1)
        img_list=self.__list_txt_to_list(img_list_txt)
        #使用正则表达式匹配出标题
        chapter_title=re.search('var pageTitle = (.*?);',index_html).group(1)
        return {
            'title':chapter_title,
            'img_list':img_list
        }

    #将图片列表文本转换成图片列表
    def __list_txt_to_list(self,list_txt):
        #删去不必要的符号
        list_txt=list_txt.replace('[','')
        list_txt=list_txt.replace(']','')
        list_txt=list_txt.replace('"','')
        #分割为列表
        img_list=list_txt.split(',')
        return img_list
    #图片列表转url列表
    def __img_list_to_img_url_list(self,img_list):
        img_url_list=[self.pic_prefix_url+str(self.pic_comic_url)+'/'+str(self.chapter_url)+'/'+img_url for img_url in img_list]
        return img_url_list

    def load_a_chapter_to_file(self,result):
        #创建用于储存一话的文件夹
        os.mkdir(result['title']+'/')
        img_url_list=self.__img_list_to_img_url_list(result['img_list'])
        img_id=1
        for img_url in img_url_list:
            #请求图片二进制数据(添加了被拒重连)
            for i in range(10):
                try:
                    img=requests.get(img_url).content
                except Exception as e:
                    if i >=9:
                        print('重连被拒次数超过九次')
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.1)
                    break
            #设定图片路径
            path="{}/{}.jpg".format(result['title'],str(img_id))
            #将图片写入文件
            with open(path,'wb') as f:
                f.write(img)
                print("正在下载 {} 的第 {} 张图片".format(result['title'],img_id))
                f.close()
            img_id += 1
        print('下载完成')

if __name__ =='__main__':
    sp=Comics_spider()
    sp.main()