#!/usr/bin/python
# -*- coding: utf-8 -*- # 添加这行来更好地支持中文

import random
import urllib.parse
import requests
from time import sleep
import os, signal, sys
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.style import Style
from rich.table import Table # Import Table for menu alignment

# Ensure cylo.py is in the same directory
try:
    from cylo import Bubcyz
except ImportError:
    print("[错误] 找不到 cylo.py 文件。请确保它和 JBCGJX.py 在同一目录下。")
    sys.exit(1)

# --- 定义渐变颜色和分隔符号 ---
# 这些颜色主要用于分隔符
PINK = "#FFC0CB"  # 浅粉色
PURPLE = "#800080" # 紫色
SEPARATOR_CHAR = '★' # 用于分隔符的特殊符号
# --- 渐变定义结束 ---

# --- ASCII 艺术图案 ---
# 您提供的包含中文文字的爱心图案，精确复制
# 注意：包含混合字符类型（全角、中文）的复杂 ASCII 艺术的显示效果
# 取决于您终端的字体支持和编码设置，这可能导致在某些环境中显示为“乱码”。
ascii_art_jbc_left = r"""
　  　\.　-　 -　.　　
　　　 '　　 常　 _ , -`.
　　 '　　　　_,'　　 _,'
　　'　　　,-'　　　_/ 快
　 ' 爱 ,-' \　　 _/　 手
　'　 ,'　　 \　_'　　 搜
　'　'　　　 _\'　　　 季
　' ,　　_,-'　\　　　 伯
　\,_,--'　　　 \　　　 常
"""
# --- ASCII Art 结束 ---

def signal_handler(sig, frame):
    print("\n[bold yellow]再见！感谢使用！[/bold yellow]")
    sys.exit(0)

def interpolate_color(start_color, end_color, fraction):
    """在两个十六进制颜色之间进行插值"""
    try:
        start_rgb = tuple(int(start_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        end_rgb = tuple(int(end_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        interpolated_rgb = tuple(int(start + fraction * (end - start)) for start, end in zip(start_rgb, end_rgb))
        interpolated_rgb = tuple(max(0, min(255, val)) for val in interpolated_rgb)
        return "#{:02x}{:02x}{:02x}".format(*interpolated_rgb)
    except ValueError:
        return "#FFFFFF" # 白色

# 这个渐变函数为单行文本应用随机渐变，现在用于提示语、菜单描述和信息显示
def random_gradient_text_line_rich(text):
    """为单行文本应用随机渐变并返回 rich.Text 对象"""
    modified_text = Text()
    num_chars = len(text)
    if num_chars == 0:
        return modified_text

    # 随机选择起始和结束颜色，确保不是太暗
    start_rgb = [random.randint(50, 230) for _ in range(3)]
    end_rgb = [random.randint(50, 230) for _ in range(3)]

    start_color = "#{:02x}{:02x}{:02x}".format(*start_rgb)
    end_color = "#{:02x}{:02x}{:02x}".format(*end_rgb)

    for i, char in enumerate(text):
        fraction = i / max(num_chars - 1, 1)
        interpolated_color = interpolate_color(start_color, end_color, fraction)
        modified_text.append(char, style=Style(color=interpolated_color))
    return modified_text

# 原 apply_gradient_to_text_line 函数已不再需要，因为所有单行渐变都使用随机模式
# def apply_gradient_to_text_line(text, start_color, end_color):
#     """Applies a gradient between specified colors to a single line of text and returns rich.Text"""
#     ... (代码省略)

# 这个函数专门用于生成彩虹渐变名称的 [RRGGBB]text 格式，与 CyloTool.py 匹配
def rainbow_gradient_string_cpm_format(customer_name):
    modified_string = ""
    num_chars = len(customer_name)
    # 生成随机起始和结束颜色用于渐变，类似于 JBCGJX 的方法
    start_rgb = [random.randint(30, 220) for _ in range(3)]
    end_rgb = [random.randint(30, 220) for _ in range(3)]
    start_color = "#{:02x}{:02x}{:02x}".format(*start_rgb)
    end_color = "#{:02x}{:02x}{:02x}".format(*end_rgb)

    for i, char in enumerate(customer_name):
        fraction = i / max(num_chars - 1, 1)
        # 插值颜色并格式化为 RRGGBB 字符串
        interpolated_hex = interpolate_color(start_color, end_color, fraction).lstrip('#')
        modified_string += f'[{interpolated_hex}]{char}'
    return modified_string


def gradient_text_multi_line(text, colors):
    """为多行文本应用垂直渐变"""
    lines = text.strip('\n').splitlines()
    if not lines:
        return Text()
    height = len(lines)

    colorful_text = Text()
    for y, line in enumerate(lines):
        fraction_y = y / (height - 1) if height > 1 else 0
        color_index = int(fraction_y * (len(colors) - 1))
        color_index = min(max(color_index, 0), len(colors) - 1)

        style = Style(color=colors[color_index])
        colorful_text.append(line, style=style)

        if y < len(lines) - 1:
             colorful_text.append("\n")
    return colorful_text

# 分隔符函数，使用指定的粉紫渐变和符号
def gradient_separator(title, console, separator_char='★', total_width=40, start_color=PINK, end_color=PURPLE):
    """打印一个固定宽度的分隔线，带居中标题和指定渐变颜色"""
    title_text_str = f" {title} " if title else "" # 如果有标题，则在标题前后添加空格
    title_width = len(title_text_str)

    # 调整 total_width 以更好地匹配分隔符的常见控制台宽度
    actual_total_width = max(total_width, title_width + 4)

    separator_space = actual_total_width - title_width
    left_len = separator_space // 2
    right_len = separator_space - left_len

    full_line_chars = (separator_char * left_len) + title_text_str + (separator_char * right_len)

    separator_line_text = Text()
    num_chars_in_line = len(full_line_chars)

    # 为整行应用水平渐变
    for i, char in enumerate(full_line_chars):
        fraction_x = i / max(num_chars_in_line - 1, 1)
        interpolated_color = interpolate_color(start_color, end_color, fraction_x)
        style = Style(color=interpolated_color)
        separator_line_text.append(char, style=style)

    console.print(separator_line_text)


def banner(console):
    """显示横幅，包括 ASCII 艺术图案和提示信息"""
    os.system('cls' if os.name == 'nt' else 'clear')

    # --- 显示渐变 ASCII 艺术图案 (左对齐) ---
    # 使用红/粉色渐变用于爱心（保持原样）
    art_colors = ["#FF0000", "#FF69B4", "#FFB6C1"] # 红到粉色
    # 为左对齐的艺术图案应用渐变
    colored_art = gradient_text_multi_line(ascii_art_jbc_left.strip(), art_colors) # 使用精确的爱心图案
    # 左对齐打印图案 (默认对齐方式就是左对齐)
    console.print(colored_art)
    console.print("\n")
    # --- ASCII 艺术结束 ---

    # 更新品牌名称并左对齐 (保持之前修改)
    brand_name = "季伯常专属工具版本 v1.1"
    text = Text(brand_name, style="bold black")
    console.print(text, justify="left")

    # 为横幅提示信息使用渐变分隔符，使用 STAR 符号和粉紫渐变
    gradient_separator("提示信息", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)

    # 将这三行提示信息改为随机渐变色
    console.print(random_gradient_text_line_rich("请在使用本工具前，先在 CPM 游戏中登出账号！"))
    console.print(random_gradient_text_line_rich("严禁分享您的访问密钥 检测到IP波动频繁封禁秘钥！"))
    console.print(random_gradient_text_line_rich("快手搜季伯常私信获得工具箱安装教程及使用权！"))

    # 为结束提示使用渐变分隔符，使用 STAR 符号和粉紫渐变
    gradient_separator("结束提示", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)


def load_player_data(cpm, console):
    """加载并显示玩家数据，文字使用随机渐变色"""
    # 为“玩家信息”使用渐变分隔符，使用 STAR 符号和粉紫渐变
    gradient_separator("玩家信息", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)

    response = cpm.get_player_data() # API 调用 - 未改动

    if response.get('ok'):
        data = response.get('data')
        required_keys = ['localID', 'money', 'coin', "Name", "FriendsID", "carIDnStatus"]

        if all(key in data for key in required_keys) and isinstance(data.get('carIDnStatus'), dict):
            # 为每行玩家数据应用随机渐变色
            console.print(random_gradient_text_line_rich(f">> 昵称 (Name)   : {data.get('Name', '未定义')}"))
            console.print(random_gradient_text_line_rich(f">> ID (LocalID)  : {data.get('localID', '未定义')}"))
            console.print(random_gradient_text_line_rich(f">> 绿钞 (Money)  : {data.get('money', '未定义')}"))
            console.print(random_gradient_text_line_rich(f">> 金币 (Coins)  : {data.get('coin', '未定义')}"))

            friends_count = len(data.get("FriendsID", []))
            console.print(random_gradient_text_line_rich(f">> 好友数量      : {friends_count}"))

            car_list = data.get("carIDnStatus", {}).get("carGeneratedIDs", [])
            unique_car_list = set(car_list)
            car_count = len(unique_car_list)
            console.print(random_gradient_text_line_rich(f">> 车辆数量      : {car_count}"))

        else:
            missing_keys = [key for key in required_keys if key not in data]
            error_msg = "[bold red] ! 错误：无法加载完整的玩家数据。"
            if missing_keys:
                error_msg += f" 缺少键: {', '.join(missing_keys)}。"
            error_msg += " 新账号必须至少登录一次游戏才能生成数据 (✘)[bold red]"
            console.print(error_msg)
            return False # Indicate failure
    else:
        error_detail = response.get('error', '未知错误')
        console.print(f"[bold red] ! 错误：获取玩家数据失败。原因: {error_detail} (✘)[bold red]")
        console.print("[bold yellow]   请检查您的网络连接和登录凭据是否正确。[/bold yellow]")
        return False # Indicate failure
    return True # Indicate success


def load_key_data(cpm, console):
    """加载并显示访问密钥信息，文字使用随机渐变色"""
    # 为“访问密钥信息”使用渐变分隔符，使用 STAR 符号和粉紫渐变
    gradient_separator("访问密钥信息", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)

    data = cpm.get_key_data() # API 调用 - 未改动

    access_key = data.get('access_key', 'N/A')
    if len(access_key) > 8:
         displayed_key = f"{access_key[:4]}...{access_key[-4:]}"
    else:
         displayed_key = access_key

    # 为每行密钥信息应用随机渐变色
    console.print(random_gradient_text_line_rich(f">> Access Key : {displayed_key}"))
    console.print(random_gradient_text_line_rich(f">> Telegram ID: {data.get('telegram_id', '未提供')}"))

    balance = data.get('coins', 'N/A')
    is_unlimited = data.get('is_unlimited', False)
    balance_display = "无限" if is_unlimited else balance
    console.print(random_gradient_text_line_rich(f">> 余额 (点数): {balance_display}"))


def prompt_valid_value(content, tag, console, password=False):
    """提示用户输入一个有效（非空）的值，提示文本使用随机渐变色"""
    # 应用随机渐变到提示文本
    gradient_content = random_gradient_text_line_rich(content)
    while True:
        # 将带渐变的 rich.Text 对象传递给 Prompt.ask
        # password 参数控制输入是否隐藏
        value = Prompt.ask(gradient_content, password=password, console=console)
        if not value or value.isspace(): # 检查值是否为空或只包含空格
            console.print(f"[bold red]输入错误：{tag} 不能为空或仅包含空格，请重新输入 (✘)[bold red]")
        else:
            return value

def load_client_details(console):
    """获取并显示客户端大致位置，文字使用随机渐变色"""
    try:
        response = requests.get("http://ip-api.com/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        # 为“地理位置 (估算)”使用渐变分隔符，使用 STAR 符号和粉紫渐变
        gradient_separator("地理位置 (估算)", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)
        # 为每行位置信息应用随机渐变色
        console.print(random_gradient_text_line_rich(f">> 国家/地区: {data.get('country', '未知')} ({data.get('countryCode', '')})"))
        console.print(random_gradient_text_line_rich(f">> 城市     : {data.get('city', '未知')} {data.get('zip', '')}"))
    except requests.exceptions.RequestException as e:
        console.print("[bold yellow] ! 警告：无法获取地理位置信息。[/bold yellow]")
    finally:
        # 为“主菜单”使用渐变分隔符，使用 STAR 符号和粉紫渐变
        gradient_separator("主菜单", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)


# 保持用于菜单描述的原有随机渐变文本函数 (与上面的 random_gradient_text_line_rich 功能一致，可以合并)
# 为了代码简洁，我们将菜单描述也统一使用 random_gradient_text_line_rich
# def random_gradient_text_line(text):
#     """Applies a random gradient to a single line of text"""
#     ... (代码省略)


if __name__ == "__main__":
    console = Console()
    signal.signal(signal.SIGINT, signal_handler)

    while True: # 登录循环
        banner(console)

        # 获取登录信息，提示语使用随机渐变色，输入可见
        # 在提示前使用渐变分隔符，使用 STAR 符号和粉紫渐变
        gradient_separator("账号登录", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE) # 提示前的分隔符

        # 使用 random_gradient_text_line_rich 为提示语应用随机渐变色
        acc_email = prompt_valid_value("请输入账号邮箱", "邮箱", console, password=False)
        acc_password = prompt_valid_value("请输入账号密码", "密码", console, password=False) # password=False 使输入可见
        acc_access_key = prompt_valid_value("请输入访问密钥 (Access Key):", "Access Key", console, password=False) # password=False 使输入可见


        console.print("[bold yellow][%] 正在尝试登录...", end="")

        try:
            cpm = Bubcyz(acc_access_key)
            login_response = cpm.login(acc_email, acc_password) # API 调用 - 未改动
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]登录失败 (网络错误 ✘)[bold red]")
            console.print(f"[dim]   错误详情: {e}[/dim]")
            console.print("[bold yellow]   请检查您的网络连接和登录凭据是否正确。[/bold yellow]")
            sleep(3)
            continue
        except Exception as e:
             console.print(f"[bold red]登录时发生未知错误 (✘)[bold red]")
             console.print(f"[dim]   错误详情: {e}[/dim]")
             sleep(3)
             continue

        if login_response != 0:
            if login_response == 100:
                console.print("[bold red]登录失败：账号未找到 (✘)[bold red]")
            elif login_response == 101:
                console.print("[bold red]登录失败：密码错误 (✘)[bold red]")
            elif login_response == 103:
                console.print("[bold red]登录失败：无效的 Access Key (✘)[bold red]")
            else:
                console.print(f"[bold red]登录失败：未知错误代码 {login_response} (✘)[bold red]")
                console.print("[bold yellow] ! 提示：请确保您填写了所有字段！[/bold yellow]")
            sleep(3)
            continue
        else:
            console.print("[bold green]登录成功 (✔)[bold green]")
            sleep(1)


        # --- 登录成功，进入主菜单循环 ---
        while True:
            banner(console) # 重新显示横幅

            if not load_player_data(cpm, console):
                console.print("[bold yellow]无法继续操作，请尝试重新登录或检查账号状态。[/bold yellow]")
                sleep(3)
                break

            load_key_data(cpm, console)
            load_client_details(console) # 显示位置和菜单标题

            # 定义菜单选项数据
            menu_options_data = [
                ("01", "修改绿钞数量 (上限 5千万)", "消耗: 1K 点数"),
                ("02", "修改金币数量 (上限 50万)", "消耗: 10K 点数"),
                ("03", "解锁皇冠成就 (156 成就)", "消耗: 30K 点数"),
                ("04", "更改玩家 ID (无字符/长度限制,不能有空格)", "消耗: 30K 点数"),
                ("05", "更改普通昵称", "消耗: 5K 点数"),
                ("06", "更改彩虹渐变昵称", "消耗: 5K 点数"),
                ("07", "解锁自定义车牌", "消耗: 2K 点数"),
                ("08", "删除当前账号 (操作无法撤销!)", "免费"),
                ("09", "注册新账号", "免费"),
                ("10", "清空好友列表", "消耗: 1K 点数"),
                ("11", "解锁所有付费车辆", "消耗: 5K 点数"),
                ("12", "解锁全部车辆 (包括非付费)", "消耗: 10K 点数"),
                ("13", "解锁所有车辆警笛", "消耗: 3K 点数"),
                ("14", "解锁 W16 引擎", "消耗: 3K 点数"),
                ("15", "解锁所有喇叭", "消耗: 3K 点数"),
                ("16", "解锁引擎无损伤", "消耗: 3K 点数"),
                ("17", "解锁无限燃料", "消耗: 3K 点数"),
                ("18", "解锁所有付费房屋", "消耗: 4K 点数"),
                ("19", "解锁轮胎烟雾", "消耗: 4K 点数"),
                ("20", "解锁所有普通车轮", "消耗: 4K 点数"),
                ("21", "解锁所有人物动作 (动画)", "消耗: 2K 点数"),
                ("22", "解锁所有男性服装", "消耗: 3K 点数"),
                ("23", "解锁所有女性服装", "消耗: 3K 点数"),
                ("24", "修改比赛胜利场数", "消耗: 10K 点数"),
                ("25", "修改比赛失败场数", "消耗: 10K 点数"),
                ("26", "克隆账号数据到另一账号", "消耗: 50K 点数"),
                ("27", "修改车辆马力/扭矩 (指定车辆)", "消耗: 5K 点数"),
                ("28", "自定义轮胎转向角度 (指定车辆)", "消耗: 5K 点数"),
                ("29", "自定义轮胎磨损度 (指定车辆)", "消耗: 3K 点数"),
                ("30", "自定义车辆行驶里程 (指定车辆)", "消耗: 3K 点数"),
                ("31", "自定义车辆刹车性能 (指定车辆)", "消耗: 2K 点数"),
                ("32", "移除车辆后保险杠 (指定车辆)", "消耗: 5K 点数"),
                ("33", "移除车辆前保险杠 (指定车辆)", "消耗: 5K 点数"),
                ("34", "强制修改当前账号密码", "消耗: 100K 点数"),
                ("35", "强制修改当前账号邮箱", "消耗: 100K 点数"),
                ("36", "自定义车辆尾翼 (指定车辆)", "消耗: 10K 点数"),
                ("37", "自定义车身套件 (指定车辆)", "消耗: 10K 点数"),
                ("38", "解锁高级/付费车轮", "消耗: 5K 点数"),
                ("39", "解锁皇冠图标车辆 (例如丰田皇冠)", "消耗: 10K 点数"),
                ("0", "退出工具箱", ""), # Exit option
            ]

            # --- 使用 Table 显示菜单选项，实现对齐 ---
            menu_table = Table(show_header=False, box=None, padding=(0, 1)) # 减少列间距

            menu_table.add_column(justify="left", style="default", ratio=1, overflow="fold") # 允许描述文字折行
            menu_table.add_column(justify="right", style="bold red", min_width=12) # 给消耗点数一个最小宽度，并用醒目颜色


            # 向表格添加行
            for num, desc, cost in menu_options_data:
                # 创建左侧单元格内容 (编号 + 渐变描述)
                left_cell_content = Text()
                left_cell_content.append(f"({num}) ", style="bold white")
                # 为描述文本应用随机渐变
                gradient_desc = random_gradient_text_line_rich(desc)
                left_cell_content.append(gradient_desc)

                # 创建右侧单元格内容 (消耗)
                right_cell_content = Text()
                if cost:
                     # 消耗字符串已经包含 "消耗: "
                     right_cell_content.append(cost, style="bold red")

                # 将行添加到表格
                menu_table.add_row(left_cell_content, right_cell_content)

            # 打印表格
            console.print(menu_table)

            # --- 菜单选项结束 ---

            # 为“CPM 工具箱”使用渐变分隔符，使用 STAR 符号和粉紫渐变
            gradient_separator("CPM 工具箱", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)

            # 获取用户选择
            choices = [str(i) for i in range(0, 40)]
            service = IntPrompt.ask(f"[bold][?] 请选择服务项目 [red][1-39 或 0 退出][/red][/bold]", choices=choices, show_choices=False, console=console)

            # 为“操作执行”使用渐变分隔符，使用 STAR 符号和粉紫渐变
            gradient_separator("操作执行", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE)

            # --- 根据用户选择执行操作 ---
            operation_successful = False
            exit_tool = False

            if service == 0: # 退出
                console.print("[bold white] 感谢您使用本工具！再见！[/bold white]")
                exit_tool = True
                operation_successful = True

            elif service == 1: # 修改绿钞数量
                console.print("[bold yellow][?] 请输入您想要的绿钞数量 (最大 500,000,000)[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量", console=console)
                console.print("[%] 正在保存数据...", end="")
                if 0 < amount <= 500000000:
                    if cpm.set_player_money(amount): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是点数不足或服务器问题，请稍后再试。[/bold red]")
                else:
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   请输入 1 到 500,000,000 之间的数字。[/bold red]")

            elif service == 2:  # 修改金币数量
                console.print("[bold yellow][?] 请输入您想要的金币数量 (最大 500,000)[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量", console=console)
                console.print("[%] 正在保存数据...", end="")
                if 0 < amount <= 500000:
                    if cpm.set_player_coins(amount): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是点数不足或服务器问题，请稍后再试。[/bold red]")
                else:
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   请输入 1 到 500,000 之间的数字。[/bold red]")

            elif service == 3: # 解锁皇冠成就
                console.print("[bold red][!] 提示:[/bold red] 如果游戏内未立即显示皇冠，请尝试重新登录游戏几次.")
                console.print("[bold red][!] 提示:[/bold red] 请勿对同一个账号重复执行此操作.")
                sleep(2)
                console.print("[%] 正在解锁皇冠成就...", end="")
                if cpm.set_player_rank(): # API 调用 - 未改动
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            elif service == 4: # 更改玩家 ID
                console.print("[bold yellow][?] 请输入您的新 ID (无特殊字符或长度限制，但不能包含空格)[/bold yellow]")
                new_id = prompt_valid_value("[?] 新 ID", "ID", console)
                console.print("[%] 正在保存数据...", end="")
                if ' ' not in new_id:
                    if cpm.set_player_localid(new_id.upper()): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是 ID 已被使用、点数不足或服务器问题。[/bold red]")
                else:
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   ID 不能为空且不能包含空格。[/bold red]")

            elif service == 5: # 更改普通昵称
                console.print("[bold yellow][?] 请输入您的新昵称[/bold yellow]")
                new_name = prompt_valid_value("[?] 新昵称", "昵称", console)
                console.print("[%] 正在保存数据...", end="")
                if new_name:
                    if cpm.set_player_name(new_name): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是昵称不符合规则、点数不足或服务器问题。[/bold red]")
                else:
                     console.print("[bold red]输入无效 (✘)[bold red]")
                     console.print("[bold red]   昵称不能为空。[/bold red]")

            elif service == 6: # 更改彩虹渐变昵称
                console.print("[bold yellow][?] 请输入您想设置为彩虹渐变色的昵称[/bold yellow]")
                new_name_plain = prompt_valid_value("[?] 基础昵称", "基础昵称", console)
                console.print("[%] 正在生成渐变色并保存数据...", end="")
                if new_name_plain:
                    rainbow_name_str = rainbow_gradient_string_cpm_format(new_name_plain)
                    if cpm.set_player_name(rainbow_name_str): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        console.print("[dim]   (请注意，游戏内显示效果取决于游戏是否支持 Rich/BBCode 格式)[/dim]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是昵称过长、点数不足或服务器问题。[/bold red]")
                else:
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   基础昵称不能为空。[/bold red]")

            elif service == 7: # 解锁自定义车牌
                console.print("[%] 正在解锁自定义车牌...", end="")
                if cpm.set_player_plates(): # API 调用 - 未改动
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            elif service == 8: # 删除当前账号
                console.print("[bold red][!] 警告：删除账号是永久性操作，无法撤销！所有数据将丢失！[/bold red]")
                answ = Prompt.ask("[bold red][?] 您确定要删除当前登录的账号吗？[/bold red]", choices=["y", "n"], default="n", console=console)
                if answ == "y":
                    console.print("[%] 正在删除账号...", end="")
                    cpm.delete() # API 调用 - 未改动
                    print("[bold green]账号删除指令已发送 (✔)[bold green]")
                    console.print("[bold yellow]   请重新启动工具或登录其他账号。[/bold yellow]")
                    exit_tool = True
                    operation_successful = True
                else:
                    console.print("[bold yellow]   操作已取消。[/bold yellow]")
                    operation_successful = False

            elif service == 9: # 注册新账号
                console.print("[bold yellow][!] 正在注册新账号[/bold yellow]")
                acc2_email = prompt_valid_value("[?] 新账号邮箱", "邮箱", console)
                acc2_password = prompt_valid_value("[?] 新账号密码", "密码", console, password=True)
                console.print("[%] 正在创建新账号...", end="")
                status = cpm.register(acc2_email, acc2_password) # API 调用 - 未改动
                if status == 0:
                    print("[bold green]成功 (✔)[bold green]")
                    console.print("[bold yellow]   提示：新账号需要先在游戏内登录一次才能使用本工具修改数据。[/bold yellow]")
                    operation_successful = True
                elif status == 105:
                    console.print("[bold red]注册失败 (✘)[bold red]")
                    console.print("[bold yellow]   原因：该邮箱已被注册。[/bold yellow]")
                else:
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print(f"[bold red]   未知错误代码: {status}，请稍后再试。[/bold red]")


            elif service == 10: # 清空好友列表
                console.print("[%] 正在清空好友列表...", end="")
                if cpm.delete_player_friends(): # API 调用 - 未改动
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            # --- 解锁操作 ---
            unlock_actions = {
                11: ("解锁所有付费车辆", cpm.unlock_paid_cars, "[!] 可能需要一些时间，请勿中断。"), # API 调用 - 未改动
                12: ("解锁全部车辆 (包括非付费)", cpm.unlock_all_cars, None), # API 调用 - 未改动
                13: ("解锁所有车辆警笛", cpm.unlock_all_cars_siren, None), # API 调用 - 未改动
                14: ("解锁 W16 引擎", cpm.unlock_w16, None), # API 调用 - 未改动
                15: ("解锁所有喇叭", cpm.unlock_horns, None), # API 调用 - 未改动
                16: ("解锁引擎无损伤", cpm.disable_engine_damage, None), # API 调用 - 未改动
                17: ("解锁无限燃料", cpm.unlimited_fuel, None), # API 调用 - 未改动
                18: ("解锁所有付费房屋", cpm.unlock_houses, None), # API 调用 - 未改动
                19: ("解锁轮胎烟雾", cpm.unlock_smoke, None), # API 调用 - 未改动
                20: ("解锁所有普通车轮", cpm.unlock_wheels, None), # API 调用 - 未改动
                21: ("解锁所有人物动作 (动画)", cpm.unlock_animations, None), # API 调用 - 未改动
                22: ("解锁所有男性服装", cpm.unlock_equipments_male, None), # API 调用 - 未改动
                23: ("解锁所有女性服装", cpm.unlock_equipments_female, None), # API 调用 - 未改动
                38: ("解锁高级/付费车轮", cpm.shittin, None), # API 调用 - 未改动
                39: ("解锁皇冠图标车辆 (例如丰田皇冠)", cpm.unlock_crown, "[!] 可能需要一些时间，请勿中断。"), # API 调用 - 未改动
            }

            if service in unlock_actions:
                action_name, action_func, note = unlock_actions[service]
                if note:
                    console.print(f"[bold yellow]{note}[/bold yellow]")
                console.print(f"[%]正在 {action_name}...", end="")
                if action_func(): # API 调用 - 未改动
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            elif service == 24 or service == 25: # 修改胜/负场数
                field = "胜利" if service == 24 else "失败"
                set_func = cpm.set_player_wins if service == 24 else cpm.set_player_loses # API 调用 - 未改动
                console.print(f"[bold yellow][?] 请输入想设置的比赛{field}场数[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量", console=console)
                console.print(f"[%] 正在修改比赛{field}场数...", end="")
                if amount >= 0:
                    if set_func(amount): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")
                else:
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   场数不能为负数。[/bold red]")

            elif service == 26: # 克隆账号
                console.print("[bold yellow][!] 请输入[接收]数据的目标账号信息[/bold yellow]")
                to_email = prompt_valid_value("[?] 目标账号邮箱", "邮箱", console)
                to_password = prompt_valid_value("[?] 目标账号密码", "密码", console, password=True)
                console.print("[%] 正在将当前账号数据克隆到目标账号...", end="")
                if cpm.account_clone(to_email, to_password): # API 调用 - 未改动
                     print("[bold green]成功 (✔)[bold green]")
                     console.print("[bold yellow]   提示：目标账号的原有数据可能已被覆盖。[/bold yellow]")
                     operation_successful = True
                else:
                     console.print("[bold red]失败 (✘)[bold red]")
                     console.print("[bold red]   原因：目标账号的邮箱/密码无效，或目标账号未注册，或点数不足。[/bold red]")

            elif service == 27: # 修改车辆马力/扭矩
                 console.print("[bold yellow][!] 警告：修改后可能无法恢复原始数值！[/bold yellow]")
                 console.print("[bold yellow][?] 请输入要修改的车辆信息[/bold yellow]")
                 car_id = IntPrompt.ask("[bold][?] 车辆 ID (数字序号)[/bold]", console=console)
                 new_hp = IntPrompt.ask("[bold][?] 新马力 (HP)[/bold]", console=console)
                 new_inner_hp = IntPrompt.ask("[bold][?] 新内部马力 (Inner HP)[/bold]", console=console)
                 new_nm = IntPrompt.ask("[bold][?] 新牛米 (NM)[bold]", console=console)
                 new_torque = IntPrompt.ask("[bold][?] 新扭矩 (Torque)[bold]", console=console)
                 console.print("[%] 正在修改车辆性能...",end="")
                 if all(val >= 0 for val in [car_id, new_hp, new_inner_hp, new_nm, new_torque]):
                     if cpm.hack_car_speed(car_id, new_hp, new_inner_hp, new_nm, new_torque): # API 调用 - 未改动
                         print("[bold green]成功 (✔)[bold green]")
                         operation_successful = True
                     else:
                         console.print("[bold red]失败 (✘)[bold red]")
                         console.print("[bold red]   操作失败，请检查车辆 ID 是否正确、点数是否足够或数值是否在合理范围。[/bold red]")
                 else:
                      console.print("[bold red]输入无效 (✘)[bold red]")
                      console.print("[bold red]   车辆 ID 和性能数值不能为负数。[/bold red]")

            # --- 自定义车辆属性 ---
            car_custom_actions = {
                28: ("轮胎转向角度", cpm.max_max1, "[?] 请输入新的转向角度值"), # API 调用 - 未改动
                29: ("轮胎磨损度 (%)", cpm.max_max2, "[?] 请输入新的磨损百分比"), # API 调用 - 未改动
                30: ("车辆行驶里程", cpm.millage_car, "[?] 请输入新的里程数"), # API 调用 - 未改动
                31: ("车辆刹车性能", cpm.brake_car, "[?] 请输入新的刹车性能值"), # API 调用 - 未改动
                36: ("车辆尾翼 ID", cpm.telmunnongodz, "[?] 请输入新的尾翼 ID"), # API 调用 - 未改动
                37: ("车身套件 ID", cpm.telmunnongonz, "[?] 请输入新的车身套件 ID"), # API 调用 - 未改动
            }

            if service in car_custom_actions:
                 action_name, action_func, prompt_msg = car_custom_actions[service]
                 console.print(f"[bold yellow][?] 请输入要修改 {action_name} 的车辆 ID[/bold yellow]")
                 car_id = IntPrompt.ask("[bold][?] 车辆 ID[/bold]", console=console)
                 console.print(f"[bold yellow]{prompt_msg}[/bold yellow]")
                 custom_value = IntPrompt.ask("[bold][?] 数值[/bold]", console=console)
                 console.print(f"[%] 正在为车辆 {car_id} 设置 {action_name} 为 {custom_value}...", end="")
                 if car_id >= 0 and custom_value >= 0: # 确保自定义值也非负
                     if action_func(car_id, custom_value): # API 调用 - 未改动
                         print("[bold green]成功 (✔)[bold green]")
                         operation_successful = True
                     else:
                         console.print("[bold red]失败 (✘)[bold red]")
                         console.print("[bold red]   操作失败，请检查车辆 ID 是否正确、点数是否足够或输入值是否有效。[/bold red]")
                 else:
                     console.print("[bold red]输入无效 (✘)[bold red]")
                     console.print("[bold red]   车辆 ID 和自定义数值不能为负数。[/bold red]")

            # --- 移除保险杠 ---
            elif service == 32 or service == 33:
                bumper_type = "后" if service == 32 else "前"
                remove_func = cpm.rear_bumper if service == 32 else cpm.front_bumper # API 调用 - 未改动
                console.print(f"[bold yellow][?] 请输入要移除 {bumper_type} 保险杠的车辆 ID[/bold yellow]")
                car_id = IntPrompt.ask("[bold][?] 车辆 ID[/bold]", console=console)
                console.print(f"[%] 正在为车辆 {car_id} 移除 {bumper_type} 保险杠...", end="")
                if car_id >= 0:
                    if remove_func(car_id): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，请检查车辆 ID 是否正确、点数是否足够。[/bold red]")
                else:
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   车辆 ID 不能为负数。[/bold red]")

            elif service == 34: # 修改密码
                console.print("[bold yellow][?] 请输入当前账号的新密码[/bold yellow]")
                new_password = prompt_valid_value("[bold][?] 新密码[/bold]", "密码", console, password=True)
                console.print("[%] 正在修改密码...", end="")
                if cpm.change_password(new_password): # API 调用 - 未改动
                    print("[bold green]成功 (✔)[bold green]")
                    console.print("[bold yellow]   提示：您的登录令牌已更新，请使用新密码重新登录。[/bold yellow]")
                    operation_successful = True
                    exit_tool = True # 用户必须重新登录
                else:
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器错误。[/bold red]")

            elif service == 35: # 修改邮箱
                console.print("[bold yellow][?] 请输入当前账号的新邮箱[/bold yellow]")
                new_email = prompt_valid_value("[bold][?] 新邮箱[/bold]", "邮箱", console)
                if '@' in new_email and '.' in new_email.split('@')[-1]:
                    console.print("[%] 正在修改邮箱...", end="")
                    if cpm.change_email(new_email): # API 调用 - 未改动
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                        console.print("[bold yellow]   邮箱已更改，请使用新邮箱重新登录。[/bold yellow]")
                        break # 跳出内层菜单循环，强制重新登录
                    else:
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是该邮箱已被注册、点数不足或服务器错误。[/bold red]")
                else:
                     console.print("[bold red]输入无效 (✘)[bold red]")
                     console.print("[bold red]   请输入有效的邮箱地址。[/bold red]")

            # 在操作完成（成功或失败）后打印渐变分隔符，使用粉紫渐变
            if operation_successful and not exit_tool: # 如果 exit_tool 为 True，则已经跳出或即将跳出
                 gradient_separator("", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE) # 无标题的渐变分隔符
                 answ = Prompt.ask("[?] 操作完成。是否返回主菜单？(y/n, 默认 y)", choices=["y", "n"], default="y", console=console)
                 if answ == "n":
                     console.print("[bold white] 感谢您使用本工具！再见！[/bold white]")
                     exit_tool = True # 标记以跳出外层循环
                 # 否则 (默认或输入 y)，循环继续自动进入内层菜单

            # 处理特定服务失败后的提示
            # 排除服务 0 (退出)、8 (删除) 和 9 (注册)，因为它们有自己的流程。
            elif not operation_successful and service not in [0, 8, 9]:
                gradient_separator("", console, separator_char=SEPARATOR_CHAR, start_color=PINK, end_color=PURPLE) # 无标题的渐变分隔符
                console.print("[bold yellow]   请检查错误信息，按回车键返回主菜单...[/bold yellow]")
                input() # 等待用户按回车键

            # 如果 exit_tool 标记为 True，则跳出内层菜单循环
            if exit_tool:
                 break # 跳出内层菜单循环

        # 当 exit_tool 为 True 时 (来自服务 0, 8, 34, 或用户选择 'n')
        # 或者修改邮箱成功 (服务 35) 时，会跳到此处。
        if exit_tool: # 如果内层循环设置了 exit_tool，也跳出外层 (登录) 循环。
            break