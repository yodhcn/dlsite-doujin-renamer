# dlsite-doujin-renamer
![软件截图](screenshot.png)

## Features
- 支持深度查找带有 RJ 号的文件夹
- 支持手动选择文件夹或拖拽文件夹到软件窗口
- 支持在 `config.json` 中设置软件配置
- 支持在 `cache.db` 中缓存从 [dlsite.com](https://www.dlsite.com/maniax/) 抓取的元数据
- 将文件夹封面修改为作品封面

## Config
默认配置
```json
{
  "scaner_max_depth": 5,
  "scraper_locale": "ja_jp",
  "scraper_connect_timeout": 10,
  "scraper_read_timeout": 10,
  "scraper_sleep_interval": 3,
  "scraper_http_proxy": null,
  "renamer_template": "age_cat[maker_name][rjcode] work_name cv_list_str",
  "renamer_release_date_format": "%y%m%d",
  "renamer_exclude_square_brackets_in_work_name_flag": true,
  "renamer_illegal_character_to_full_width_flag": false,
  "renamer_make_folder_icon": true,
  "renamer_remove_jpg_file": true,
  "renamer_delimiter": " ",
  "renamer_cv_list_left": "(CV ",
  "renamer_cv_list_right": ")",
  "renamer_tags_max_number": 5,
  "renamer_tags_ordered_list": [
    "标签1",
    ["标签2", "替换2"],
    "标签3"
  ],
  "renamer_age_cat_map_gen": "全年龄",
  "renamer_age_cat_map_r15": "R15",
  "renamer_age_cat_map_r18": "R18",
  "renamer_age_cat_left": "(",
  "renamer_age_cat_right": ")",
  "renamer_age_cat_ignore_r18": true,
  "renamer_series_name_left": "",
  "renamer_series_name_right": "",
  "renamer_mode": "RENAME",
  "renamer_move_root": "RENAMER_MOVE_ROOT",
  "renamer_move_template": "maker_name/series_name/age_cat[rjcode] work_name cv_list_str"
}
```
- `scaner_max_depth` 扫描器的扫描深度
- `scraper_locale` 刮削器的刮削元数据的语言（`["en_us", "ja_jp", "ko_kr", "zh_cn", "zh_tw"]` 中的一个）
- `scraper_connect_timeout` 刮削器的 [requests 连接超时](https://docs.python-requests.org/zh_CN/latest/user/advanced.html#timeout)时间（秒）
- `scraper_connect_timeout` 刮削器的 [requests 读取超时](https://docs.python-requests.org/zh_CN/latest/user/advanced.html#timeout)时间（秒）
- `scraper_sleep_interval` 刮削器的请求网页的时间间隔（秒）
- `scraper_http_proxy` 刮削器的使用的代理（http代理），此项设置为 `null` 时，将尝试使用系统代理
- `renamer_template` 命名器的命名模板，命名器将替换模板中的关键字：
  - `rjcode` 同人作品的 RJ 号
  - `work_name` 同人作品的名称
  - `maker_id` 同人作品的社团 RG 号
  - `maker_name` 同人作品的社团名称
  - `series_name` 系列名。由于作品可能不存在系列名，请配合 `renamer_series_name_left` `renamer_series_name_right` 使用
  - `release_date` 同人作品的发售日期，具体的日期格式可在 `renamer_release_date_format` 中设置
  - `cv_list_str` 同人作品的声优列表
  - `tags_list_str` 同人作品的标签（分类）列表
  - `age_cat` 同人作品的年龄分级（全年龄、R15、R18）

  例如：`"renamer_template": "[maker_name] work_name (rjcode)[tags_list_str]"`<br/>
  重命名前：`RJ298293 蓄音レヱル 紅`<br/>
  重命名后：`[RaRo] 蓄音レヱル 紅 (RJ298293)[萌 感动 治愈 环绕音]`
- `renamer_release_date_format` 命名器模板中 `release_date` 的日期格式
- `renamer_exclude_square_brackets_in_work_name_flag` 命名器的 `work_name` 中是否排除 `【】` 及其间的内容。例如：
  - `"renamer_exclude_square_brackets_in_work_name_flag": true`<br/>
    `work_name = "道草屋 なつな2 隣の部屋のたぬきさん。"`
  - `"renamer_exclude_square_brackets_in_work_name_flag": false`<br/>
    `work_name = "【お隣り耳噛み】道草屋 なつな2 隣の部屋のたぬきさん。【お隣り耳かき】"`
- `renamer_illegal_character_to_full_width_flag` 命名器的新文件名中的非法字符（windows保留字）如何处理。`true`为全角化，`false`为直接删除。例如：
  - `"renamer_illegal_character_to_full_width_flag": true`<br/>
    `文/件*名` → `文／件＊名`
  - `"renamer_illegal_character_to_full_width_flag": false`<br/>
    `文/件*名` → `文件名`
- `make_folder_icon` 是否将文件夹封面改为作品封面，`true` 为修改，`false` 反之
- `remove_jpg_file` 是否保留文件夹中的作品封面图，`true` 为移除，`false` 为保留（不会消除文件夹封面）
- `renamer_delimiter` 命名器将列表转为字符串时的分隔符，作用于 `cv_list_str` 和 `tags_list_str`。不能含有系统保留字 ```[^\/:*?`<>|]*```
- `cv_list_left` `cv_list_right` 命名器在声优列表左右外括的符号，作用于 `cv_list_str`。不能含有系统保留字 ```[^\/:*?`<>|]*```
- `renamer_tags_max_number` 命名器向文件名中写入标签的最大个数
- `renamer_tags_ordered_list` 命名器向文件名中写入标签的优先顺序和替换标签。列表。每一项若是字符串，则为匹配的标签。若是二元列表，则为`["匹配的标签","替换的标签"]`。例如：
  - ```
    "renamer_delimiter": ",",
    "renamer_tags_max_number": 4,
    "renamer_tags_ordered_list": [
        "标签1",
        ["标签2","替换2"],
        "标签3"
    ]
    ```
  - 作品含有的标签：`标签6` `标签5` `标签4` `标签3` `标签2` `标签1`
  - 文件名中的标签：`标签1,替换2,标签3,标签6`
- `renamer_age_cat_map_gen` 自定义`全年龄`作品的年龄分级
- `renamer_age_cat_map_r15` 自定义`R15`作品的年龄分级
- `renamer_age_cat_map_r18` 自定义`R18`作品的年龄分级
- `renamer_age_cat_left` `renamer_age_cat_right` 自定义命名器在 `age_cat`(年龄分级) 左右两侧的符号。不能含有系统保留字 ```[^\/:*?`<>|]*```
- ``renamer_age_cat_ignore_r18`` 命名器是否忽略 R18 作品的 `age_cat` (年龄分级)，R18 作品占大多数时建议开启。例如：`"renamer_template": "age_cat[maker_name] work_name (rjcode)"`
  - `"renamer_age_cat_ignore_r18": true`<br/>
      `work_name = "[桃色CODE] 道草屋 なつな2 隣の部屋のたぬきさん。 (RJ363096)"`
  - `"renamer_age_cat_ignore_r18": false`<br/>
      `work_name = "(R18)[桃色CODE] 道草屋 なつな2 隣の部屋のたぬきさん。 (RJ363096)"`
- `renamer_series_name_left` `renamer_series_name_right` 自定义命名器在 `series_name`(系列名) 左右两侧的符号。不能含有系统保留字 ```[^\/:*?`<>|]*```
- `renamer_mode` 命名器的工作模式
  - `RENAME` 重命名，使用模板 `renamer_template`
  - `MOVE` 移动到指定根目录，使用模板 `renamer_move_template`
  - `LINK` 复制快捷方式到指定根目录（保持源文件夹不变，适合需要做种的使用场景），使用模板 `renamer_move_template`
- `renamer_move_root` `MOVE`与`LINK`工作模式下的指定根目录，**注意路径配置使用`/`分隔符**，例如 `"renamer_move_root": "D:/音声库"`
- `renamer_move_template` `MOVE`与`LINK`工作模式下的命名模板。<br/>
例如：`"renamer_move_template": "maker_name/[rjcode] work_name"` `"renamer_move_root": "D:/音声库"`<br/>
源路径：`D:/道草屋/RJ363096` → 目标路径：`D:/音声库/桃色CODE/[RJ363096] 道草屋 なつな2 隣の部屋のたぬきさん。`

【注】**请不要使用 Windows 系统自带的「记事本」编辑配置文件**，建议使用 [Notepad3](https://www.rizonesoft.com/downloads/notepad3/)、[Notepad++](https://notepad-plus-plus.org/) 或 [Visual Studio Code](https://code.visualstudio.com/) 等专业的文本编辑器。本软件的配置文件 `config.json` 使用不带 BOM 的标准 UTF-8 编码，但在 Windows 记事本的语境中，所谓的「UTF-8」指的是带 BOM 的 UTF-8。因此，用 Windows 系统自带的记事本编辑配置文件后，会导致本软件无法正确读取配置。

## 开发者文档
### 环境
1. install python 3.9
2. `pip install -r requirements.txt`
### 运行
`python main.py`
### 打包（输出路径 `dist/main.exe`）
`python build.py`

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=yodhcn/dlsite-doujin-renamer&type=Date)](https://www.star-history.com/#yodhcn/dlsite-doujin-renamer&Date)
