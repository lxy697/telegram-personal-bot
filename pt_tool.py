import requests
from bs4 import BeautifulSoup
import os

class TJUpt:
    def __init__(self, pass_key, save_path):
        self.rss_url = f"https://tjupt.org/torrentrss.php?rows=10&icat=1&isize=1&search_mode=0&passkey={pass_key}&linktype=dl"
        self.save_path = save_path
        self.resources = []
    
    def fetch_and_parse_rss(self,searchtxt):# 发送请求获取 RSS 内容
        url = f"{self.rss_url}&search={searchtxt}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve RSS feed: {response.status_code}")
            return []
        soup = BeautifulSoup(response.content, 'xml')  # 使用 xml 解析器解析 RSS
        items = soup.find_all('item')# 提取所有 item 标签中的资源
        resources = []
        for item in items:
            title = item.find('title').text if item.find('title') else 'No Title'
            description = item.find('description').text if item.find('description') else 'No Description'
            link = item.find('link').text if item.find('link') else 'No Link'
            enclosure_url = item.find('enclosure')['url'] if item.find('enclosure') else None
            pub_date = item.find('pubDate').text if item.find('pubDate') else 'No PubDate'
            resources.append({
                'title': title,
                'description': description,
                'link': link,
                'enclosure_url': enclosure_url,
                'pub_date': pub_date
            })
        return resources

    def rearrange_title(self,title):
        parts = title.split('[')# 按照 `[` 和 `]` 拆分标题，保留 `]`
        parts = [part for part in parts if part]# 移除第一个空元素，因为标题开头可能是 `[`，它会导致列表开头是空的
        if len(parts) > 1:
            size_info = parts[-1].split(']')[0]  # 取最后一项的大小部分
            other_parts = parts[:-1]# 获取其他部分的内容
            new_title = f"[{other_parts[0]} [{size_info}] " + " ".join(f"[{part}" for part in other_parts[1:])# 重新拼接成新的标题，将大小信息放到第二位
            return new_title
        else:
            return title# 如果没有按照预期拆分，返回原始标题
        
    def get_resources(self, searchtxt):
        self.resources = self.fetch_and_parse_rss(searchtxt)
        if self.resources == []:
            self.resources_txt = "检索失败"
        else:
            self.resources_txt = ""
            for idx, resource in enumerate(self.resources):
                modified_title = f"[{idx}] {self.rearrange_title(resource['title'])}"
                self.resources_txt += f"\u25CF {modified_title}\n"
            self.resources_txt += "请输入序号下载影片"
        return self.resources_txt

    def download_file(self, index):
        if not isinstance(index, int) or not (0 <= index < len(self.resources)):
            return "指令格式错误"
        url = self.resources[index]['enclosure_url']
        response = requests.get(url, stream=True)  # 以流模式下载文件
        if response.status_code == 200:
            with open(self.save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):  # 分块写入
                    file.write(chunk)
            return f"种子文件下载完毕\n\u25CF {self.rearrange_title(self.resources[index]['title'])}"
        else:
            return f"下载失败，状态码: {response.status_code}"






