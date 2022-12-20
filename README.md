# dlsite-doujin-renamer
![软件截图](screenshot.png)

## Features
- 支持深度查找带有 RJ 号的文件夹
- 支持手动选择文件夹或拖拽文件夹到软件窗口
- 支持在 ```config.json``` 中设置软件配置
- 支持在 ```cache.db``` 中缓存从 [dlsite.com](https://www.dlsite.com/maniax/) 抓取的元数据

## Config
示例配置
```json
{
  "scaner_max_depth": 5,
  "scraper_locale": "zh_cn",
  "scraper_connect_timeout": 10,
  "scraper_read_timeout": 10,
  "scraper_sleep_interval": 3,
  "scraper_http_proxy": null,
  "renamer_template": "[maker_name][rjcode] work_name cv_list_str",
  "renamer_exclude_square_brackets_in_work_name_flag": false,
  "renamer_illegal_character_to_full_width_flag": false,
  'make_folder_icon': True,
  'remove_jpg_file': True,
  "renamer_delimiter": " ",
  'cv_list_left': "(CV ",
  'cv_list_right': ")",
  "renamer_tags_max_number": 5,
  "renamer_tags_ordered_list": [
    "标签1",
    ["标签2","替换2"],
    "标签3"
  ]
}
```
- ```scaner_max_depth``` 扫描器的扫描深度
- ```scraper_locale``` 刮削器的刮削元数据的语言（```["en_us", "ja_jp", "ko_kr", "zh_cn", "zh_tw"]``` 中的一个）
- ```scraper_connect_timeout``` 刮削器的 [requests 连接超时](https://docs.python-requests.org/zh_CN/latest/user/advanced.html#timeout)时间（秒）
- ```scraper_connect_timeout``` 刮削器的 [requests 读取超时](https://docs.python-requests.org/zh_CN/latest/user/advanced.html#timeout)时间（秒）
- ``scraper_sleep_interval`` 刮削器的请求网页的时间间隔（秒）
- ```scraper_http_proxy``` 刮削器的使用的代理（http代理），此项设置为 ```null``` 时，将尝试使用系统代理
- ```renamer_template``` 命名器的命名模板，命名器将替换模板中的关键字：
  - ```rjcode``` 同人作品的 RJ 号
  - ```work_name``` 同人作品的名称
  - ```maker_id``` 同人作品的社团 RG 号
  - ```maker_name``` 同人作品的社团名称
  - ```release_date``` 同人作品的发售日期
  - ```cv_list_str``` 同人作品的声优列表
  - ```tags_list_str``` 同人作品的标签（分类）列表

  例如：```"renamer_template": "[maker_name] work_name (rjcode)[tags_list_str]"```<br/>
  重命名前：``` 蓄音 紅```<br/>
  重命名后：```[RaRo] 蓄音 紅 ()[萌 感动 治愈 环绕音]```
- ```renamer_exclude_square_brackets_in_work_name_flag``` 命名器的 ```work_name``` 中是否排除 ```【】``` 及其间的内容。例如：
  - ```"renamer_exclude_square_brackets_in_work_name_flag": true```<br/>
    ```work_name = "道草屋 なつな2 隣の部屋のたぬきさん。"```
  - ```"renamer_exclude_square_brackets_in_work_name_flag": false```<br/>
    ```work_name = "【お隣り耳噛み】道草屋 なつな2 隣の部屋のたぬきさん。【お隣り耳かき】"```
- ```renamer_illegal_character_to_full_width_flag``` 命名器的新文件名中的非法字符（windows保留字）如何处理。`true` 为全角化，`false` 为直接删除。例如：
  - ```"renamer_illegal_character_to_full_width_flag": true```<br/>
    `文/件*名` → `文／件＊名`
  - ```"renamer_illegal_character_to_full_width_flag": false```<br/>
    `文/件*名` → `文件名`
- ```make_folder_icon``` 是否将文件夹封面改为作品封面，`true` 为修改，`false` 反之
- ```remove_jpg_file``` 是否保留文件夹中的作品封面图，`true` 为移除，`false` 为保留（不会消除文件夹封面）
- ```renamer_delimiter``` 命名器将列表转为字符串时的分隔符，作用于 `cv_list_str` 和 `tags_list_str`
- ```cv_list_left``` ```cv_list_right``` 命名器在声优列表左右外括的符号，作用于 `cv_list_str`
- ```renamer_tags_max_number``` 命名器向文件名中写入标签的最大个数
- ```renamer_tags_ordered_list``` 命名器向文件名中写入标签的优先顺序和替换标签。列表。每一项若是字符串，则为匹配的标签。若是二元列表，则为`["匹配的标签","替换的标签"]`。例如：
  - ```
    "renamer_delimiter": " ",
    "renamer_tags_max_number": 4,
    "renamer_tags_ordered_list": [
        "标签1",
        ["标签2","替换2"],
        "标签3"
    ]
    ```
  - 作品含有的标签：`标签6` `标签5` `标签4` `标签3` `标签2` `标签1`
  - 文件名中的标签：`标签1,替换2,标签3,标签6`

【注】**请不要使用 Windows 系统自带的「记事本」编辑配置文件**，建议使用 [Notepad3](https://www.rizonesoft.com/downloads/notepad3/)、[Notepad++](https://notepad-plus-plus.org/) 或 [Visual Studio Code](https://code.visualstudio.com/) 等专业的文本编辑器。本软件的配置文件 ```config.json``` 使用不带 BOM 的标准 UTF-8 编码，但在 Windows 记事本的语境中，所谓的「UTF-8」指的是带 BOM 的 UTF-8。因此，用 Windows 系统自带的记事本编辑配置文件后，会导致本软件无法正确读取配置。
