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

# --- ASCII 艺术图案 ---
# 您提供的包含中文文字的爱心图案，精确复制
ascii_art_jbc_left = r"""
　  　\.　-　 -　.　　
　　　 '　　 常　 _ , -`.
　　 '　　　　_,'　　 _,'
　　'　　　,-'　　　_/ 快
　 ' 爱 ,-' \　　 _/　 手
　'　 ,'　　 \　_'　　 搜
　'　'　　　 _\'　　　 季
　' ,　　_,-'　\　　　 伯
　\,_,--'　　　 \　　　常
"""
# --- ASCII Art End ---

def signal_handler(sig, frame):
    print("\n[bold yellow]再见！感谢使用！[/bold yellow]")
    sys.exit(0)

def interpolate_color(start_color, end_color, fraction):
    """Interpolates between two hex colors"""
    try:
        start_rgb = tuple(int(start_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        end_rgb = tuple(int(end_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        interpolated_rgb = tuple(int(start + fraction * (end - start)) for start, end in zip(start_rgb, end_rgb))
        interpolated_rgb = tuple(max(0, min(255, val)) for val in interpolated_rgb)
        return "#{:02x}{:02x}{:02x}".format(*interpolated_rgb)
    except ValueError:
        return "#FFFFFF" # White

# This gradient function returns a rich.Text object for single line, used for prompts
def random_gradient_text_line_rich(text):
    """Applies a random gradient to a single line of text and returns rich.Text"""
    modified_text = Text()
    num_chars = len(text)
    if num_chars == 0:
        return modified_text

    start_rgb = [random.randint(30, 220) for _ in range(3)]
    end_rgb = [random.randint(30, 220) for _ in range(3)]

    start_color = "#{:02x}{:02x}{:02x}".format(*start_rgb)
    end_color = "#{:02x}{:02x}{:02x}".format(*end_rgb)

    for i, char in enumerate(text):
        fraction = i / max(num_chars - 1, 1)
        interpolated_color = interpolate_color(start_color, end_color, fraction)
        modified_text.append(char, style=Style(color=interpolated_color))
    return modified_text

# This function is specifically for generating the [RRGGBB]text format for rainbow names, matching CyloTool.py
def rainbow_gradient_string_cpm_format(customer_name):
    modified_string = ""
    num_chars = len(customer_name)
    # Generate random start and end colors for the gradient, similar to JBCGJX's approach
    start_rgb = [random.randint(30, 220) for _ in range(3)]
    end_rgb = [random.randint(30, 220) for _ in range(3)]
    start_color = "#{:02x}{:02x}{:02x}".format(*start_rgb)
    end_color = "#{:02x}{:02x}{:02x}".format(*end_rgb)

    for i, char in enumerate(customer_name):
        fraction = i / max(num_chars - 1, 1)
        # Interpolate color and format as RRGGBB string
        interpolated_hex = interpolate_color(start_color, end_color, fraction).lstrip('#')
        modified_string += f'[{interpolated_hex}]{char}'
    return modified_string


def gradient_text_multi_line(text, colors):
    """Applies a vertical gradient to multi-line text"""
    lines = text.strip('\n').splitlines()
    if not lines:
        return Text()
    height = len(lines)
    # Removed complex width calculation as it can be unreliable with mixed characters.
    # Relying on rich's handling of lines as is.

    colorful_text = Text()
    for y, line in enumerate(lines):
        fraction_y = y / (height - 1) if height > 1 else 0
        color_index = int(fraction_y * (len(colors) - 1))
        color_index = min(max(color_index, 0), len(colors) - 1)

        style = Style(color=colors[color_index])
        # Append line directly without padding
        colorful_text.append(line, style=style)

        if y < len(lines) - 1:
             colorful_text.append("\n")
    return colorful_text

def random_gradient_separator(title, console, separator_char='=', total_width=60):
    """Prints a fixed-width separator line with a centered title and random gradient color per line"""
    # Generate random colors for this specific separator line
    colors = [
        "#{:06x}".format(random.randint(50, 255)), # Ensure colors are not too dark
        "#{:06x}".format(random.randint(50, 255)),
        "#{:06x}".format(random.randint(50, 255)),
    ] # Use 3 random colors for a more varied gradient

    title_text_str = f" {title} " # Add space around title
    # Using len() for width calculation
    title_width = len(title_text_str)

    # Calculate space needed for separator characters on each side
    actual_total_width = max(total_width, title_width + 4)

    separator_space = actual_total_width - title_width
    left_len = separator_space // 2
    right_len = separator_space - left_len

    separator_line_text = Text()

    # Create the full line as a single string for gradient application
    full_line_chars = (separator_char * left_len) + title_text_str + (separator_char * right_len)

    # Apply horizontal gradient across the entire line
    num_chars_in_line = len(full_line_chars)
    for i, char in enumerate(full_line_chars):
        fraction_x = i / max(num_chars_in_line - 1, 1)
        color_index = int(fraction_x * (len(colors) - 1))
        color_index = min(max(color_index, 0), len(colors) - 1)
        style = Style(color=colors[color_index])
        separator_line_text.append(char, style=style)

    # Removed justify="center" to potentially allow custom alignment if needed, though usually separators are centered
    # For a left-aligned ASCII art and centered separators, this might be fine.
    console.print(separator_line_text)


def banner(console):
    """Displays banner including ASCII art"""
    os.system('cls' if os.name == 'nt' else 'clear')

    # --- Display Gradient ASCII Art (Left Aligned) ---
    # Using red/pink gradient for the heart (reverted colors)
    art_colors = ["#FF0000", "#FF69B4", "#FFB6C1"] # Red to Pink colors
    # Apply gradient to the left-aligned art
    colored_art = gradient_text_multi_line(ascii_art_jbc_left.strip(), art_colors) # Use the exact heart art
    # Print the art left-aligned (default justify is left)
    console.print(colored_art)
    console.print("\n")
    # --- ASCII Art End ---

    # Updated brand name and left justification (kept from previous modification)
    brand_name = "季伯常专属工具版本 v1.1"
    text = Text(brand_name, style="bold black")
    console.print(text, justify="left")


    # Use the random gradient separator for banner tips
    random_gradient_separator("提示信息", console, separator_char='-')

    console.print("[bold yellow]      请在使用本工具前，先在 CPM 游戏中登出账号！[/bold yellow]")
    console.print("[bold red]      严禁分享您的访问密钥 检测到IP波动频繁封禁秘钥！[/bold red]")
    console.print("[bold red]      快手搜季伯常私信获得工具箱安装教程及使用权！[/bold red]")
    random_gradient_separator("结束提示", console, separator_char='-')


def load_player_data(cpm, console):
    """Loads and displays player data"""
    # Use random gradient separator for "玩家信息" with star separator
    random_gradient_separator("玩家信息", console, separator_char='*')

    response = cpm.get_player_data()

    if response.get('ok'):
        data = response.get('data')
        required_keys = ['localID', 'money', 'coin', "Name", "FriendsID", "carIDnStatus"]

        # CyloTool.py Checks for 'floats' and 'integers' which might not be strictly necessary here
        # Keeping JBCGJX.py's check for essential keys and carIDnStatus structure
        if all(key in data for key in required_keys) and isinstance(data.get('carIDnStatus'), dict):
            console.print(f"[bold white]   >> 昵称 (Name)   : {data.get('Name', '未定义')}[/bold white]")
            console.print(f"[bold white]   >> ID (LocalID)  : {data.get('localID', '未定义')}[/bold white]")
            console.print(f"[bold white]   >> 绿钞 (Money)  : {data.get('money', '未定义')}[/bold white]")
            console.print(f"[bold white]   >> 金币 (Coins)  : {data.get('coin', '未定义')}[/bold white]")

            friends_count = len(data.get("FriendsID", []))
            console.print(f"[bold white]   >> 好友数量      : {friends_count}[/bold white]")

            # Using JBCGJX.py's more accurate car count logic
            car_list = data.get("carIDnStatus", {}).get("carGeneratedIDs", [])
            unique_car_list = set(car_list)
            car_count = len(unique_car_list)
            console.print(f"[bold white]   >> 车辆数量      : {car_count}[/bold white]")

        else:
            # Keeping JBCGJX.py's detailed error message
            missing_keys = [key for key in required_keys if key not in data]
            error_msg = "[bold red] ! 错误：无法加载完整的玩家数据。"
            if missing_keys:
                error_msg += f" 缺少键: {', '.join(missing_keys)}。"
            error_msg += " 新账号必须至少登录一次游戏才能生成数据 (✘)[bold red]"
            console.print(error_msg)
            return False # Indicate failure
    else:
        # Keeping JBCGJX.py's detailed error message
        error_detail = response.get('error', '未知错误')
        console.print(f"[bold red] ! 错误：获取玩家数据失败。原因: {error_detail} (✘)[bold red]")
        console.print("[bold yellow]   请检查您的网络连接和登录凭据是否正确。[/bold yellow]")
        return False # Indicate failure
    return True # Indicate success


def load_key_data(cpm, console):
    """Loads and displays Access Key information"""
    # Use random gradient separator for "访问密钥信息" with dash separator
    random_gradient_separator("访问密钥信息", console, separator_char='-')

    data = cpm.get_key_data()

    # Keeping JBCGJX.py's obscured key display
    access_key = data.get('access_key', 'N/A')
    if len(access_key) > 8:
         displayed_key = f"{access_key[:4]}...{access_key[-4:]}"
    else:
         displayed_key = access_key

    console.print(f"[bold white]   >> Access Key : {displayed_key}[/bold white]")
    console.print(f"[bold white]   >> Telegram ID: {data.get('telegram_id', '未提供')}[/bold white]")

    # Keeping JBCGJX.py's balance display
    balance = data.get('coins', 'N/A')
    is_unlimited = data.get('is_unlimited', False)
    balance_display = "无限" if is_unlimited else balance
    console.print(f"[bold white]   >> 余额 (点数): {balance_display}[/bold white]")


def prompt_valid_value(content, tag, console, password=False):
    """Prompts user for a valid (non-empty) value with gradient prompt text"""
    # Apply random gradient to the prompt content using the rich text function
    gradient_content = random_gradient_text_line_rich(content)
    while True:
        # Pass the rich.Text object with gradient to Prompt.ask
        # password parameter controls input hiding
        value = Prompt.ask(gradient_content, password=password, console=console)
        if not value or value.isspace(): # Check if value is empty or only spaces
            console.print(f"[bold red]输入错误：{tag} 不能为空或仅包含空格，请重新输入 (✘)[bold red]")
        else:
            return value

def load_client_details(console):
    """Gets and displays approximate client location"""
    try:
        response = requests.get("http://ip-api.com/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        # Use random gradient separator for "地理位置 (估算)"
        random_gradient_separator("地理位置 (估算)", console, separator_char='=')
        console.print(f"[bold white]   >> 国家/地区: {data.get('country', '未知')} ({data.get('countryCode', '')})[/bold white]")
        console.print(f"[bold white]   >> 城市     : {data.get('city', '未知')} {data.get('zip', '')}[/bold white]")
    except requests.exceptions.RequestException as e:
        console.print("[bold yellow] ! 警告：无法获取地理位置信息。[/bold yellow]")
    finally:
        # Use random gradient separator for "主菜单"
        random_gradient_separator("主菜单", console, separator_char='=')


# This gradient function returns a rich.Text object for single line
def random_gradient_text_line(text):
    """Applies a random gradient to a single line of text"""
    modified_text = Text()
    num_chars = len(text)
    if num_chars == 0:
        return modified_text

    start_rgb = [random.randint(30, 220) for _ in range(3)]
    end_rgb = [random.randint(30, 220) for _ in range(3)]

    start_color = "#{:02x}{:02x}{:02x}".format(*start_rgb)
    end_color = "#{:02x}{:02x}{:02x}".format(*end_rgb)

    for i, char in enumerate(text):
        fraction = i / max(num_chars - 1, 1)
        interpolated_color = interpolate_color(start_color, end_color, fraction)
        modified_text.append(char, style=Style(color=interpolated_color))
    return modified_text


if __name__ == "__main__":
    console = Console()
    signal.signal(signal.SIGINT, signal_handler)

    while True: # Login loop
        banner(console)

        # Get login info with gradient prompts and visible input
        random_gradient_separator("账号登录", console, separator_char='=') # Separator before prompts

        # Modified prompt calls to remove "[bold][?][/bold]" and set password=False
        acc_email = prompt_valid_value("请输入账号邮箱:", "邮箱", console, password=False)
        acc_password = prompt_valid_value("请输入账号密码:", "密码", console, password=False) # password=False for visible input
        acc_access_key = prompt_valid_value("请输入访问密钥 (Access Key):", "Access Key", console, password=False) # password=False for visible input


        console.print("[bold yellow][%] 正在尝试登录...", end="")

        try:
            cpm = Bubcyz(acc_access_key)
            login_response = cpm.login(acc_email, acc_password)
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
            # print(" ", end="") # Removed as rich print handles this better
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


        # --- Login successful, enter main menu loop ---
        while True:
            banner(console) # Redisplay banner

            if not load_player_data(cpm, console):
                console.print("[bold yellow]无法继续操作，请尝试重新登录或检查账号状态。[/bold yellow]")
                sleep(3)
                break

            load_key_data(cpm, console)
            load_client_details(console) # Displays location and menu title

            # Define menu options data
            menu_options_data = [
                ("01", "修改绿钞数量 (上限 5千万)", "消耗: 1K 点数"),
                ("02", "修改金币数量 (上限 50万)", "消耗: 10K 点数"),
                ("03", "解锁皇冠成就 (156 成就)", "消耗: 30K 点数"),
                ("04", "更改玩家 ID (无字符/长度限制,不能有空格)", "消耗: 30K 点数"), # MODIFIED
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
                ("34", "强制修改当前账号密码", "消耗: 10K 点数"),
                ("35", "强制修改当前账号邮箱", "消耗: 10K 点数"),
                ("36", "自定义车辆尾翼 (指定车辆)", "消耗: 10K 点数"),
                ("37", "自定义车身套件 (指定车辆)", "消耗: 10K 点数"),
                ("38", "解锁高级/付费车轮", "消耗: 5K 点数"),
                ("39", "解锁皇冠图标车辆 (例如丰田皇冠)", "消耗: 10K 点数"),
                ("0", "退出工具箱", ""), # Exit option
            ]

            # --- Display menu options using Table for alignment ---
            menu_table = Table(show_header=False, box=None, padding=(0, 1)) # 减少列间距

            menu_table.add_column(justify="left", style="default", ratio=1, overflow="fold") # 允许描述文字折行
            menu_table.add_column(justify="right", style="bold red", min_width=12) # 给消耗点数一个最小宽度，并用醒目颜色


            # Add rows to the table
            for num, desc, cost in menu_options_data:
                # Create the left cell content (Number + Gradient Description)
                left_cell_content = Text()
                left_cell_content.append(f"({num}) ", style="bold white")
                # Apply random gradient to the description text using the rich text function
                gradient_desc = random_gradient_text_line_rich(desc)
                left_cell_content.append(gradient_desc)

                # Create the right cell content (Cost)
                right_cell_content = Text()
                if cost:
                     # The cost string already includes "消耗: "
                     right_cell_content.append(cost, style="bold red")

                # Add the row to the table
                menu_table.add_row(left_cell_content, right_cell_content)

            # Print the table
            console.print(menu_table)

            # --- Menu options end ---

            # Use random gradient separator for "CPM 工具箱"
            random_gradient_separator("CPM 工具箱", console, separator_char='=')

            # Get user choice
            # Choices explicitly listed from 0 to 39 as in CyloTool.py
            choices = [str(i) for i in range(0, 40)]
            service = IntPrompt.ask(f"[bold][?] 请选择服务项目 [red][1-39 或 0 退出][/red][/bold]", choices=choices, show_choices=False, console=console)

            random_gradient_separator("操作执行", console, separator_char='=')

            # --- Perform actions based on user choice ---
            operation_successful = False
            exit_tool = False

            if service == 0: # Exit
                console.print("[bold white] 感谢您使用本工具！再见！[/bold white]")
                exit_tool = True
                operation_successful = True

            elif service == 1: # Modify Money
                console.print("[bold yellow][?] 请输入您想要的绿钞数量 (最大 500,000,000)[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量", console=console)
                console.print("[%] 正在保存数据...", end="")
                if 0 < amount <= 500000000:
                    # Call as in CyloTool.py
                    if cpm.set_player_money(amount):
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是点数不足或服务器问题，请稍后再试。[/bold red]")
                else:
                    # Invalid input messages from JBCGJX.py
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   请输入 1 到 500,000,000 之间的数字。[/bold red]")

            elif service == 2:  # Modify Coins
                console.print("[bold yellow][?] 请输入您想要的金币数量 (最大 500,000)[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量", console=console)
                console.print("[%] 正在保存数据...", end="")
                if 0 < amount <= 500000:
                    # Call as in CyloTool.py
                    if cpm.set_player_coins(amount):
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是点数不足或服务器问题，请稍后再试。[/bold red]")
                else:
                    # Invalid input messages from JBCGJX.py
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   请输入 1 到 500,000 之间的数字。[/bold red]")

            elif service == 3: # Unlock Crown Achievement
                # Keep JBCGJX.py's notes
                console.print("[bold red][!] 提示:[/bold red] 如果游戏内未立即显示皇冠，请尝试重新登录游戏几次.")
                console.print("[bold red][!] 提示:[/bold red] 请勿对同一个账号重复执行此操作.")
                sleep(2)
                console.print("[%] 正在解锁皇冠成就...", end="")
                # Call as in CyloTool.py
                if cpm.set_player_rank():
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    # Detailed error messages from JBCGJX.py
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            elif service == 4: # Change Player ID -- MODIFIED SECTION
                console.print("[bold yellow][?] 请输入您的新 ID (无特殊字符或长度限制，但不能包含空格)[/bold yellow]") # MODIFIED PROMPT
                # Use prompt_valid_value with console=console as in JBCGJX.py
                new_id = prompt_valid_value("[?] 新 ID", "ID", console) # This function already checks for empty or all-space string
                console.print("[%] 正在保存数据...", end="")
                # MODIFIED CONDITION: Check if new_id is not empty and does not contain spaces.
                # The prompt_valid_value already ensures it's not empty or just spaces.
                # We still need to explicitly check for spaces within the string if prompt_valid_value doesn't.
                # However, prompt_valid_value has: `if not value or value.isspace():`
                # This means `value` (which becomes `new_id`) will not be empty and not consist *only* of spaces.
                # A string like "id with space" would pass `value.isspace()` as false.
                # So, an additional check for internal spaces is good.
                if ' ' not in new_id: # Ensure no spaces within the ID string
                    if cpm.set_player_localid(new_id.upper()): # .upper() is consistent with CyloTool
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是 ID 已被使用、点数不足或服务器问题。[/bold red]")
                else:
                    # Invalid input messages from JBCGJX.py
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   ID 不能为空且不能包含空格。[/bold red]") # MODIFIED ERROR

            elif service == 5: # Change Normal Name
                console.print("[bold yellow][?] 请输入您的新昵称[/bold yellow]")
                # Use prompt_valid_value with console=console as in JBCGJX.py
                new_name = prompt_valid_value("[?] 新昵称", "昵称", console)
                console.print("[%] 正在保存数据...", end="")
                # Call as in CyloTool.py
                # Keep JBCGJX.py's basic check
                if new_name:
                    if cpm.set_player_name(new_name):
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是昵称不符合规则、点数不足或服务器问题。[/bold red]")
                else:
                     # Invalid input messages from JBCGJX.py
                     console.print("[bold red]输入无效 (✘)[bold red]")
                     console.print("[bold red]   昵称不能为空。[/bold red]")

            elif service == 6: # Change Rainbow Gradient Name
                console.print("[bold yellow][?] 请输入您想设置为彩虹渐变色的昵称[/bold yellow]")
                # Use prompt_valid_value with console=console as in JBCGJX.py
                new_name_plain = prompt_valid_value("[?] 基础昵称", "基础昵称", console)
                console.print("[%] 正在生成渐变色并保存数据...", end="")
                if new_name_plain:
                    # Generate the [RRGGBB]text format string, similar to CyloTool.py
                    rainbow_name_str = rainbow_gradient_string_cpm_format(new_name_plain)
                    # Call cpm method with the formatted string
                    if cpm.set_player_name(rainbow_name_str):
                        print("[bold green]成功 (✔)[bold green]")
                        # Keep JBCGJX.py's note
                        console.print("[dim]   (请注意，游戏内显示效果取决于游戏是否支持 Rich/BBCode 格式)[/dim]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是昵称过长、点数不足或服务器问题。[/bold red]")
                else:
                    # Invalid input messages from JBCGJX.py
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   基础昵称不能为空。[/bold red]")

            elif service == 7: # Unlock Custom Plate
                console.print("[%] 正在解锁自定义车牌...", end="")
                # Call as in CyloTool.py
                if cpm.set_player_plates():
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    # Detailed error messages from JBCGJX.py
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            elif service == 8: # Delete Account
                # Keep JBCGJX.py's warning and prompt style
                console.print("[bold red][!] 警告：删除账号是永久性操作，无法撤销！所有数据将丢失！[/bold red]")
                answ = Prompt.ask("[bold red][?] 您确定要删除当前登录的账号吗？[/bold red]", choices=["y", "n"], default="n", console=console)
                if answ == "y":
                    console.print("[%] 正在删除账号...", end="")
                    # Call delete method as in CyloTool.py (no return check in CyloTool.py)
                    cpm.delete()
                    # Keep JBCGJX.py's success message and exit logic
                    print("[bold green]账号删除指令已发送 (✔)[bold green]")
                    console.print("[bold yellow]   请重新启动工具或登录其他账号。[/bold yellow]")
                    exit_tool = True
                    operation_successful = True
                else:
                    # Keep JBCGJX.py's cancel message
                    console.print("[bold yellow]   操作已取消。[/bold yellow]")
                    operation_successful = False # Explicitly set to false, though it doesn't matter much here.

            elif service == 9: # Register New Account
                console.print("[bold yellow][!] 正在注册新账号[/bold yellow]")
                # Use prompt_valid_value with console=console and password=True as in JBCGJX.py
                acc2_email = prompt_valid_value("[?] 新账号邮箱", "邮箱", console)
                acc2_password = prompt_valid_value("[?] 新账号密码", "密码", console, password=True)
                console.print("[%] 正在创建新账号...", end="")
                # Call register method as in CyloTool.py
                status = cpm.register(acc2_email, acc2_password)
                # Keep JBCGJX.py's detailed result handling and messages
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


            elif service == 10: # Clear Friends List
                console.print("[%] 正在清空好友列表...", end="")
                # Call as in CyloTool.py
                if cpm.delete_player_friends():
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    # Detailed error messages from JBCGJX.py
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            # --- Unlock Actions ---
            # Kept the organized structure from JBCGJX.py
            unlock_actions = {
                11: ("解锁所有付费车辆", cpm.unlock_paid_cars, "[!] 可能需要一些时间，请勿中断。"),
                12: ("解锁全部车辆 (包括非付费)", cpm.unlock_all_cars, None),
                13: ("解锁所有车辆警笛", cpm.unlock_all_cars_siren, None),
                14: ("解锁 W16 引擎", cpm.unlock_w16, None),
                15: ("解锁所有喇叭", cpm.unlock_horns, None),
                16: ("解锁引擎无损伤", cpm.disable_engine_damage, None),
                17: ("解锁无限燃料", cpm.unlimited_fuel, None),
                18: ("解锁所有付费房屋", cpm.unlock_houses, None),
                19: ("解锁轮胎烟雾", cpm.unlock_smoke, None),
                20: ("解锁所有普通车轮", cpm.unlock_wheels, None),
                21: ("解锁所有人物动作 (动画)", cpm.unlock_animations, None),
                22: ("解锁所有男性服装", cpm.unlock_equipments_male, None),
                23: ("解锁所有女性服装", cpm.unlock_equipments_female, None),
                38: ("解锁高级/付费车轮", cpm.shittin, None),
                39: ("解锁皇冠图标车辆 (例如丰田皇冠)", cpm.unlock_crown, "[!] 可能需要一些时间，请勿中断。"),
            }

            if service in unlock_actions:
                action_name, action_func, note = unlock_actions[service]
                if note:
                    console.print(f"[bold yellow]{note}[/bold yellow]")
                console.print(f"[%]正在 {action_name}...", end="")
                # Call action function as in CyloTool.py
                if action_func():
                    print("[bold green]成功 (✔)[bold green]")
                    operation_successful = True
                else:
                    # Detailed error messages from JBCGJX.py
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")

            elif service == 24 or service == 25: # Modify Win/Loss Count
                field = "胜利" if service == 24 else "失败"
                set_func = cpm.set_player_wins if service == 24 else cpm.set_player_loses
                console.print(f"[bold yellow][?] 请输入想设置的比赛{field}场数[/bold yellow]")
                # Use IntPrompt with console=console
                amount = IntPrompt.ask("[?] 数量", console=console)
                console.print(f"[%] 正在修改比赛{field}场数...", end="")
                # Keep JBCGJX.py's >= 0 check
                if amount >= 0:
                    # Call set_func as in CyloTool.py
                    if set_func(amount):
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是点数不足或服务器问题。[/bold red]")
                else:
                    # Invalid input messages from JBCGJX.py
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   场数不能为负数。[/bold red]")

            elif service == 26: # Clone Account
                console.print("[bold yellow][!] 请输入[接收]数据的目标账号信息[/bold yellow]")
                # Use prompt_valid_value with console=console and password=True
                to_email = prompt_valid_value("[?] 目标账号邮箱", "邮箱", console)
                to_password = prompt_valid_value("[?] 目标账号密码", "密码", console, password=True) # MODIFIED CyloTool uses password=False here, JBCGJX was True. Let's keep True for security of target pass.
                console.print("[%] 正在将当前账号数据克隆到目标账号...", end="")
                # Call account_clone as in CyloTool.py
                if cpm.account_clone(to_email, to_password):
                     print("[bold green]成功 (✔)[bold green]")
                     # Keep JBCGJX.py's note
                     console.print("[bold yellow]   提示：目标账号的原有数据可能已被覆盖。[/bold yellow]")
                     operation_successful = True
                else:
                     # Detailed error messages from JBCGJX.py
                     console.print("[bold red]失败 (✘)[bold red]")
                     console.print("[bold red]   原因：目标账号的邮箱/密码无效，或目标账号未注册，或点数不足。[/bold red]")

            elif service == 27: # Modify Car HP/Torque
                 # Keep JBCGJX.py's warnings and prompts
                 console.print("[bold yellow][!] 警告：修改后可能无法恢复原始数值！[/bold yellow]")
                 console.print("[bold yellow][?] 请输入要修改的车辆信息[/bold yellow]")
                 # Use IntPrompt with console=console
                 car_id = IntPrompt.ask("[bold][?] 车辆 ID (数字序号)[/bold]", console=console)
                 new_hp = IntPrompt.ask("[bold][?] 新马力 (HP)[/bold]", console=console)
                 new_inner_hp = IntPrompt.ask("[bold][?] 新内部马力 (Inner HP)[/bold]", console=console)
                 new_nm = IntPrompt.ask("[bold][?] 新牛米 (NM)[bold]", console=console)
                 new_torque = IntPrompt.ask("[bold][?] 新扭矩 (Torque)[bold]", console=console)
                 console.print("[%] 正在修改车辆性能...",end="")
                 # Keep JBCGJX.py's >= 0 check
                 if all(val >= 0 for val in [car_id, new_hp, new_inner_hp, new_nm, new_torque]):
                     # Call hack_car_speed as in CyloTool.py
                     if cpm.hack_car_speed(car_id, new_hp, new_inner_hp, new_nm, new_torque):
                         print("[bold green]成功 (✔)[bold green]")
                         operation_successful = True
                     else:
                         # Detailed error messages from JBCGJX.py
                         console.print("[bold red]失败 (✘)[bold red]")
                         console.print("[bold red]   操作失败，请检查车辆 ID 是否正确、点数是否足够或数值是否在合理范围。[/bold red]")
                 else:
                      # Invalid input messages from JBCGJX.py
                      console.print("[bold red]输入无效 (✘)[bold red]")
                      console.print("[bold red]   车辆 ID 和性能数值不能为负数。[/bold red]")

            # --- Custom Car Attributes ---
            # Kept the organized structure from JBCGJX.py
            car_custom_actions = {
                28: ("轮胎转向角度", cpm.max_max1, "[?] 请输入新的转向角度值"),
                29: ("轮胎磨损度 (%)", cpm.max_max2, "[?] 请输入新的磨损百分比"),
                30: ("车辆行驶里程", cpm.millage_car, "[?] 请输入新的里程数"),
                31: ("车辆刹车性能", cpm.brake_car, "[?] 请输入新的刹车性能值"),
                36: ("车辆尾翼 ID", cpm.telmunnongodz, "[?] 请输入新的尾翼 ID"),
                37: ("车身套件 ID", cpm.telmunnongonz, "[?] 请输入新的车身套件 ID"),
            }

            if service in car_custom_actions:
                 action_name, action_func, prompt_msg = car_custom_actions[service]
                 console.print(f"[bold yellow][?] 请输入要修改 {action_name} 的车辆 ID[/bold yellow]")
                 # Use IntPrompt with console=console
                 car_id = IntPrompt.ask("[bold][?] 车辆 ID[/bold]", console=console)
                 console.print(f"[bold yellow]{prompt_msg}[/bold yellow]")
                 # Use IntPrompt with console=console
                 custom_value = IntPrompt.ask("[bold][?] 数值[/bold]", console=console)
                 console.print(f"[%] 正在为车辆 {car_id} 设置 {action_name} 为 {custom_value}...", end="")
                 # Keep JBCGJX.py's >= 0 check
                 if car_id >= 0 and custom_value >= 0: # Ensuring custom_value is also non-negative
                     # Call action_func as in CyloTool.py
                     if action_func(car_id, custom_value):
                         print("[bold green]成功 (✔)[bold green]")
                         operation_successful = True
                     else:
                         # Detailed error messages from JBCGJX.py
                         console.print("[bold red]失败 (✘)[bold red]")
                         console.print("[bold red]   操作失败，请检查车辆 ID 是否正确、点数是否足够或输入值是否有效。[/bold red]")
                 else:
                     # Invalid input messages from JBCGJX.py
                     console.print("[bold red]输入无效 (✘)[bold red]")
                     console.print("[bold red]   车辆 ID 和自定义数值不能为负数。[/bold red]")

            # --- Remove Bumpers ---
            elif service == 32 or service == 33:
                bumper_type = "后" if service == 32 else "前"
                remove_func = cpm.rear_bumper if service == 32 else cpm.front_bumper
                console.print(f"[bold yellow][?] 请输入要移除 {bumper_type} 保险杠的车辆 ID[/bold yellow]")
                # Use IntPrompt with console=console
                car_id = IntPrompt.ask("[bold][?] 车辆 ID[/bold]", console=console)
                console.print(f"[%] 正在为车辆 {car_id} 移除 {bumper_type} 保险杠...", end="")
                # Keep JBCGJX.py's >= 0 check
                if car_id >= 0:
                    if remove_func(car_id):
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，请检查车辆 ID 是否正确、点数是否足够。[/bold red]")
                else:
                    # Invalid input messages from JBCGJX.py
                    console.print("[bold red]输入无效 (✘)[bold red]")
                    console.print("[bold red]   车辆 ID 不能为负数。[/bold red]")

            elif service == 34: # Change Password
                console.print("[bold yellow][?] 请输入当前账号的新密码[/bold yellow]")
                # Use prompt_valid_value with console=console and password=True
                new_password = prompt_valid_value("[bold][?] 新密码[/bold]", "密码", console, password=True)
                console.print("[%] 正在修改密码...", end="")
                # Call change_password as in CyloTool.py
                if cpm.change_password(new_password):
                    print("[bold green]成功 (✔)[bold green]")
                    # Keep JBCGJX.py's note and exit logic
                    console.print("[bold yellow]   提示：您的登录令牌已更新，请使用新密码重新登录。[/bold yellow]")
                    operation_successful = True
                    exit_tool = True # User must re-login
                else:
                    # Detailed error messages from JBCGJX.py
                    console.print("[bold red]失败 (✘)[bold red]")
                    console.print("[bold red]   操作失败，可能是点数不足或服务器错误。[/bold red]")

            elif service == 35: # Change Email
                console.print("[bold yellow][?] 请输入当前账号的新邮箱[/bold yellow]")
                # Use prompt_valid_value with console=console
                new_email = prompt_valid_value("[bold][?] 新邮箱[/bold]", "邮箱", console)
                # Keep JBCGJX.py's basic email format check
                if '@' in new_email and '.' in new_email.split('@')[-1]:
                    console.print("[%] 正在修改邮箱...", end="")
                    # Call change_email as in CyloTool.py
                    if cpm.change_email(new_email):
                        print("[bold green]成功 (✔)[bold green]")
                        operation_successful = True
                        # Adopt CyloTool.py's logic to break to login loop after changing email
                        console.print("[bold yellow]   邮箱已更改，请使用新邮箱重新登录。[/bold yellow]")
                        break # Break out of the inner menu loop to force re-login
                    else:
                        # Detailed error messages from JBCGJX.py
                        console.print("[bold red]失败 (✘)[bold red]")
                        console.print("[bold red]   操作失败，可能是该邮箱已被注册、点数不足或服务器错误。[/bold red]")
                else:
                     # Invalid input messages from JBCGJX.py
                     console.print("[bold red]输入无效 (✘)[bold red]")
                     console.print("[bold red]   请输入有效的邮箱地址。[/bold red]")


            # Keep JBCGJX.py's success handling and prompt to return to menu or exit
            if operation_successful and not exit_tool: # If exit_tool is true, we are already breaking or will break.
                 console.print("[bold green]======================================[/bold green]")
                 answ = Prompt.ask("[?] 操作完成。是否返回主菜单？(y/n, 默认 y)", choices=["y", "n"], default="y", console=console)
                 if answ == "n":
                     console.print("[bold white] 感谢您使用本工具！再见！[/bold white]")
                     exit_tool = True # Signal to break outer loop as well
                 # else: continue (default or input y, loop continues automatically for inner menu)
            # Keep JBCGJX.py's failure handling for specific services
            # Exclude service 8 (delete) and 9 (register) from automatic "press enter to return" as they have their own flow.
            elif not operation_successful and service not in [0, 8, 9]: # service 0 also has its own exit path
                console.print("[bold red]======================================[/bold red]")
                console.print("[bold yellow]   请检查错误信息，按回车键返回主菜单...[/bold yellow]")
                input() # Wait for user to press Enter

            # Keep JBCGJX.py's exit loop break
            if exit_tool: # This flag is set on explicit exit (service 0), or after critical changes (delete, password change), or user choosing 'n'
                 break # Break out of the inner menu loop

        # This break is reached if exit_tool is True (from service 0, 8, 34, or user choosing 'n' after successful operation)
        # or if changing email (service 35) was successful which also breaks the inner loop.
        if exit_tool: # If exit_tool was set in inner loop, also break outer (login) loop.
            break # Break out of the outer login loop to end the script.
        # If we broke out of the inner loop for service 35 (change email),
        # exit_tool might not be true yet, so we fall through here
        # and continue the outer loop, leading to the login screen again (which is desired).