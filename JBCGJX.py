#!/usr/bin/python

import random
import urllib.parse
import requests
from time import sleep
import os, signal, sys
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.style import Style
from rich.table import Table
import pystyle
from pystyle import Colors, Colorate

from cylo import Bubcyz

# 假设这是艺术小兔子的 ASCII 字符画
ascii_art = r"""
              /\_/\  
             ( o.o ) 
               >^<    
"""
BRIGHT_RAINBOW = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"]

def signal_handler(sig, frame):
    print("\nBye Bye...")
    sys.exit(0)

def gradient_text(text: str, colors: list[str]) -> Text:
    lines = text.splitlines()
    width = max((len(line) for line in lines), default=0)
    segs = max(len(colors) - 1, 1)
    out = Text()
    for i, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch == " ":
                out.append(" ")
            else:
                frac = x / max(width - 1, 1)
                pos = frac * segs
                i = int(pos)
                t = pos - i
                c1 = colors[i]
                c2 = colors[min(i + 1, segs)]
                r1 = int(c1[1:3], 16)
                g1 = int(c1[3:5], 16)
                b1 = int(c1[5:7], 16)
                r2 = int(c2[1:3], 16)
                g2 = int(c2[3:5], 16)
                b2 = int(c2[5:7], 16)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                out.append(ch, Style(color=f"#{r:02x}{g:02x}{b:02x}"))
        out.append("\n")
    return out

def banner(console: Console):
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(gradient_text(ascii_art, BRIGHT_RAINBOW))
    sep = gradient_text("★☆" * 17, BRIGHT_RAINBOW)
    console.print(sep)
    console.print(gradient_text("     欢迎来到季伯常的工具箱      ", BRIGHT_RAINBOW))
    console.print(gradient_text("     快手搜索季伯常获取秘钥      ", BRIGHT_RAINBOW))
    console.print(sep)

def load_player_data(cpm, console: Console):
    response = cpm.get_player_data()

    if response.get('ok'):
        data = response.get('data')
        required_keys = ['floats', 'localID', 'money', 'coin', 'integers']
        if all(key in data for key in required_keys):
            title = gradient_text("          CPM季伯常专属工具箱", ["#FFD700", "#FFA500"])
            console.print(f"\n[bold]{title}[/bold]")

            integers_value = data.get('integers', 0)
            formatted_integers = f"{sum(integers_value):,}" if isinstance(integers_value, list) else f"{integers_value:,}"

            items = [
                ("游戏昵称", data.get('Name', 'UNDEFINED')),
                ("玩家代码", data.get('localID', 'N/A')),
                ("绿钞余额", f"{data.get('money', 0):,}"),
                ("金币余额", f"{data.get('coin', 0):,}"),
            ]

            table = Table(show_header=False, box=None, show_edge=False)
            table.add_column(style=Style(color="#FF69B4"))
            table.add_column(style=Style(color="white"))

            for label, value in items:
                colored_label = gradient_text(f"{label} :", ["#FF69B4", "#FF1493"])
                table.add_row(colored_label, f"[bold]{value}[/bold]")

            console.print(table)

            sep = gradient_text("─" * 40, ["#FF69B4", "#FF1493"])
            console.print(sep)
        else:
            console.print("[bold red]! ERROR: 新账号需至少登录游戏一次 (✘)[/bold red]")
            exit(1)
    else:
        console.print("[bold red]! ERROR: 登录凭证无效 (✘)[/bold red]")
        exit(1)

def load_key_data(cpm, console: Console):
    data = cpm.get_key_data()

    title = gradient_text("          CPM季伯常专属工具箱", ["#FF69B4", "#FF1493"])
    console.print(f"\n[bold]{title}[/bold]")

    items = [
        ("你的秘钥", Text("********", style="dark_gray")),
        ("TG ID", data.get('telegram_id', 'N/A')),
        ("秘钥余额", 'Unlimited' if data.get('is_unlimited') else data.get('coins', 'N/A'))
    ]

    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", width=15)
    table.add_column(justify="right", width=20)

    for label, value in items:
        colored_label = gradient_text(f">> {label.ljust(12)}", ["#00BFFF", "#87CEEB"])
        if isinstance(value, Text):
            colored_value = value
        else:
            colored_value = Text(str(value), style="bold white")

        table.add_row(colored_label, colored_value)

    console.print(table)

def prompt_valid_value(content, tag, password=False):
    while True:
        value = Prompt.ask(content, password=password)
        if not value or value.isspace():
            console.print(f"[bold red]{tag} 不能为空或纯空格，请重新输入 (✘)[/bold red]")
        else:
            return value

def load_client_details(console: Console):
    response = requests.get("http://ip-api.com/json")
    data = response.json()
    console.print("[bold #FF69B4] ===========[bold #FF69B4][ 快手搜索季伯常 ][/bold #FF69B4]==========[/bold #FF69B4]")
    console.print(f"[bold #FF69B4]>>登录地址    : {data.get('country')} {data.get('zip')}[/bold #FF69B4]")
    console.print("[bold #FF69B4] ============[bold #FF69B4][ 季伯常菜单栏 ][/bold #FF69B4]===========[/bold #FF69B4]")

def interpolate_color(start_color, end_color, fraction):
    start_rgb = tuple(int(start_color[i:i+2], 16) for i in (0, 2, 4))
    end_rgb = tuple(int(end_color[i:i+2], 16) for i in (0, 2, 4))
    interpolated_rgb = tuple(int(start + fraction * (end - start)) for start, end in zip(start_rgb, end_rgb))
    return "{:02x}{:02x}{:02x}".format(*interpolated_rgb)

def rainbow_gradient_string(customer_name):
    modified_string = ""
    num_chars = len(customer_name)
    start_color = "{:06x}".format(random.randint(0, 0xFFFFFF))
    end_color = "{:06x}".format(random.randint(0, 0xFFFFFF))
    for i, char in enumerate(customer_name):
        fraction = i / max(num_chars - 1, 1)
        interpolated_color = interpolate_color(start_color, end_color, fraction)
        modified_string += f'[{interpolated_color}]{char}'
    return modified_string

if __name__ == "__main__":
    console = Console()
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        banner(console)
        acc_email = prompt_valid_value("[bold][?] 账户邮箱[/bold]", "邮箱", password=False)
        acc_password = prompt_valid_value("[bold][?] 账户密码[/bold]", "密码", password=False)
        acc_access_key = prompt_valid_value("[bold][?] 访问密钥[/bold]", "访问密钥", password=False)
        console.print("[bold yellow][%] 尝试登录[/bold yellow]: ", end=None)
        cpm = Bubcyz(acc_access_key)
        login_response = cpm.login(acc_email, acc_password)
        if login_response != 0:
            if login_response == 100:
                console.print("[bold red]账户未找到 (✘)[/bold red]")
            elif login_response == 101:
                console.print("[bold red]密码错误 (✘)[/bold red]")
            elif login_response == 103:
                console.print("[bold red]无效访问密钥 (✘)[/bold red]")
            else:
                console.print("[bold red]请重试[/bold red]")
                console.print("[bold yellow] '! 注意：确保您已填写所有字段 ![/bold yellow]")
            sleep(2)
            continue
        else:
            console.print("[bold green]登录成功 (✔)[/bold green]")
            sleep(1)

        while True:
            banner(console)
            load_player_data(cpm, console)
            load_key_data(cpm, console)
            load_client_details(console)
            choices = ["00", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39"]
            from rich.console import Console
            from rich.prompt import Prompt, IntPrompt
            from rich.text import Text
            import random

            console = Console()

# 定义颜色列表
            colors = ["red", "green", "blue", "yellow", "magenta", "cyan"]

            def get_random_gradient_text(text, width):
                start_color = random.choice(colors)
                end_color = random.choice(colors)
                text_obj = Text()
                length = len(text)
                for i, char in enumerate(text):
        # 计算颜色插值
                    fraction = i / length
                    r_start = int(start_color[1:3], 16)
                    g_start = int(start_color[3:5], 16)
                    b_start = int(start_color[5:7], 16)
                    r_end = int(end_color[1:3], 16)
                    g_end = int(end_color[3:5], 16)
                    b_end = int(end_color[5:7], 16)
                    r = int(r_start + fraction * (r_end - r_start))
                    g = int(g_start + fraction * (g_end - g_start))
                    b = int(b_start + fraction * (b_end - b_start))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    text_obj.append(char, style=f"color({color})")
                return text_obj

            def get_random_gradient_text(text, width):
                start_color = random.choice(colors)
                end_color = random.choice(colors)
                style = Style(color=start_color)
                text_obj = Text(text, style=style)
                return text_obj

            from rich.console import Console
            from rich.table import Table

            functions = [
                ("(01): 增加绿钞", "1K"),
                ("(02): 增加金币", "10K"),
                ("(03): 国王等级", "30K"),
                ("(04): 更改 ID", "30K"),
                ("(05): 更改长名称", "5K"),
                ("(06): 更改名称（彩虹色）", "5K"),
                ("(07): 车牌号码", "2K"),
                ("(08): 删除账户", "免费"),
                ("(09): 注册账户", "免费"),
                ("(10): 删除好友", "1K"),
                ("(11): 解锁付费车辆", "5K"),
                ("(12): 解锁所有车辆", "10K"),
                ("(13): 解锁所有车辆警笛", "3K"),
                ("(14): 解锁 W16 引擎", "3K"),
                ("(15): 解锁所有喇叭", "3K"),
                ("(16): 解锁免伤模式", "3K"),
                ("(17): 解锁无限燃料", "3K"),
                ("(18): 解锁家园 3", "4K"),
                ("(19): 解锁烟雾特效", "4K"),
                ("(20): 解锁车轮", "4K"),
                ("(21): 解锁动画效果", "2K"),
                ("(22): 解锁男性装备", "3K"),
                ("(23): 解锁女性装备", "3K"),
                ("(24): 更改比赛胜利次数", "10K"),
                ("(25): 更改比赛失败次数", "10K"),
                ("(26): 克隆账户", "50K"),
                ("(27): 自定义生命值", "5K"),
                ("(28): 自定义轮胎角度", "5K"),
                ("(29): 自定义轮胎燃烧器", "3K"),
                ("(30): 自定义车辆里程", "3K"),
                ("(31): 自定义车辆刹车", "2K"),
                ("(32): 移除后保险杠", "5K"),
                ("(33): 移除前保险杠", "5K"),
                ("(34): 强改账户密码", "10K"),
                ("(35): 强改账户邮箱", "10K"),
                ("(36): 自定义扰流板", "10K"),
                ("(37): 自定义车身套件", "10K"),
                ("(38): 解锁高级车轮", "5K"),
                ("(39): 解锁丰田皇冠", "10K")
            ]

            console = Console()
# 设置表格属性
            table = Table(show_header=False, pad_edge=False, padding=(0, 2, 0, 8), show_lines=True)
            table.add_column(style="bold purple", justify="left")
            table.add_column(style="bold magenta", justify="right")

            for func, price in functions:
                table.add_row(func, price)

            console.print(table)

            from rich.prompt import IntPrompt
            service = IntPrompt.ask("[?] 请输入服务编号")

            if service == 0:  # 退出
                console.print("[bold white] 感谢使用本工具[/bold white]")
                break
            elif service == 1:  # 增加绿钞
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要增加的绿钞数量[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                console.print("[%] 保存数据: ", end=None)
                if amount > 0 and amount <= 500000000:
                    if cpm.set_player_money(amount):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请使用有效数值! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 2:  # 增加金币
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要增加的金币数量[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                console.print("[ % ] 保存数据: ", end="")
                if amount > 0 and amount <= 500000:
                    if cpm.set_player_coins(amount):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败[/bold red]")
                        console.print("[bold red]请重试[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败[/bold red]")
                    console.print("[bold yellow] '请使用有效数值[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 3:  # 国王等级
                console.print("[bold red][!] 注意:[/bold red]: 如果国王等级未在游戏中显示，请关闭并重新打开游戏几次。", end=None)
                console.print("[bold red][!] 注意:[/bold red]: 请勿在同一账户上重复设置国王等级。", end=None)
                sleep(2)
                console.print("[%] 为您设置国王等级: ", end=None)
                if cpm.set_player_rank():
                    console.print("[bold yellow] '操作成功[/bold yellow]")
                    console.print("[bold yellow] '======================================[/bold yellow]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败[/bold red]")
                    console.print("[bold red]请重试[/bold red]")
                    sleep(2)
                    continue
            elif service == 4:  # 更改 ID
                console.print("[bold yellow] '[?] 输入您的新 ID[/bold yellow]")
                new_id = Prompt.ask("[?] ID")
                if new_id == '999999':
                    console.print("[bold yellow] 跳过 ID 修改操作 [/bold yellow]")
                    continue
                console.print("[%] 保存数据: ", end=None)
                if True:  # 表示无长度限制
                    if cpm.set_player_id(new_id):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]ID长度不符合要求! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 5:  # 更改名称
                console.print("[bold yellow] '[?] 输入您的新名称[/bold yellow]")
                new_name = Prompt.ask("[?] 名称")
                console.print("[%] 保存数据: ", end=None)
                if len(new_name) >= 0 and len(new_name) <= 255:
                    if cpm.set_player_name(new_name):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]名称长度不符合要求! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 6:  # 更改名称（彩虹色）
                console.print("[bold yellow] '[?] 输入您的新名称[/bold yellow]")
                new_name = Prompt.ask("[?] 名称")
                rainbow_name = rainbow_gradient_string(new_name)
                console.print("[%] 保存数据: ", end=None)
                if len(new_name) >= 0 and len(new_name) <= 255:
                    if cpm.set_player_name(rainbow_name):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]名称长度不符合要求! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 7:  # 车牌号码
                console.print("[bold yellow] '[?] 输入您的新车牌号码[/bold yellow]")
                new_license_plate = Prompt.ask("[?] 车牌号码")
                console.print("[%] 保存数据: ", end=None)
                if len(new_license_plate) >= 0 and len(new_license_plate) <= 10:
                    if cpm.set_player_license_plate(new_license_plate):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]车牌号码长度不符合要求! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 8:  # 删除账户
                console.print("[bold red][!] 注意:[/bold red] 此操作将永久删除您的账户。")
                confirm = Prompt.ask("[?] 是否确认删除？", choices=["y", "n"], default="n")
                if confirm == "y":
                    console.print("[%] 删除账户: ", end=None)
                    if cpm.delete_player_account():
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    continue
            elif service == 9:  # 注册账户
                console.print("[bold yellow] '[?] 输入您的新账户邮箱[/bold yellow]")
                new_email = Prompt.ask("[?] 邮箱")
                console.print("[bold yellow] '[?] 输入您的新账户密码[/bold yellow]")
                new_password = Prompt.ask("[?] 密码", password=True)
                console.print("[%] 注册账户: ", end=None)
                if cpm.register_player_account(new_email, new_password):
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 10:  # 删除好友
                console.print("[bold yellow] '[?] 输入您要删除的好友 ID[/bold yellow]")
                friend_id = Prompt.ask("[?] 好友 ID")
                console.print("[%] 删除好友: ", end=None)
                if cpm.delete_player_friend(friend_id):
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 11:  # 解锁付费车辆
                console.print("[%] 解锁付费车辆: ", end=None)
                if cpm.unlock_paid_vehicles():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 12:  # 解锁所有车辆
                console.print("[%] 解锁所有车辆: ", end=None)
                if cpm.unlock_all_vehicles():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 13:  # 解锁所有车辆警笛
                console.print("[%] 解锁所有车辆警笛: ", end=None)
                if cpm.unlock_all_vehicle_whistles():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 14:  # 解锁 W16 引擎
                console.print("[%] 解锁 W16 引擎: ", end=None)
                if cpm.unlock_w16_engine():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 15:  # 解锁所有喇叭
                console.print("[%] 解锁所有喇叭: ", end=None)
                if cpm.unlock_all_horns():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 16:  # 解锁免伤模式
                console.print("[%] 解锁免伤模式: ", end=None)
                if cpm.unlock_invincibility_mode():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 17:  # 解锁无限燃料
                console.print("[%] 解锁无限燃料: ", end=None)
                if cpm.unlock_unlimited_fuel():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 18:  # 解锁家园 3
                console.print("[%] 解锁家园 3: ", end=None)
                if cpm.unlock_home_3():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 19:  # 解锁烟雾特效
                console.print("[%] 解锁烟雾特效: ", end=None)
                if cpm.unlock_smoke_effect():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 20:  # 解锁车轮
                console.print("[%] 解锁车轮: ", end=None)
                if cpm.unlock_wheels():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 21:  # 解锁动画效果
                console.print("[%] 解锁动画效果: ", end=None)
                if cpm.unlock_animation_effects():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 22:  # 解锁男性装备
                console.print("[%] 解锁男性装备: ", end=None)
                if cpm.unlock_male_equipment():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 23:  # 解锁女性装备
                console.print("[%] 解锁女性装备: ", end=None)
                if cpm.unlock_female_equipment():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 24:  # 更改比赛胜利次数
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要更改的比赛胜利次数[/bold yellow]")
                win_count = IntPrompt.ask("[?] 次数")
                console.print("[%] 保存数据: ", end=None)
                if win_count >= 0:
                    if cpm.set_match_win_count(win_count):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请使用有效数值! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 25:  # 更改比赛失败次数
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要更改的比赛失败次数[/bold yellow]")
                lose_count = IntPrompt.ask("[?] 次数")
                console.print("[%] 保存数据: ", end=None)
                if lose_count >= 0:
                    if cpm.set_match_lose_count(lose_count):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请使用有效数值! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 26:  # 克隆账户
                console.print("[bold red][!] 注意:[/bold red] 克隆账户操作不可逆，请谨慎操作。")
                confirm = Prompt.ask("[?] 是否确认克隆账户？", choices=["y", "n"], default="n")
                if confirm == "y":
                    console.print("[%] 克隆账户: ", end=None)
                    if cpm.clone_player_account():
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    continue
            elif service == 27:  # 自定义生命值
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的生命值[/bold yellow]")
                health = IntPrompt.ask("[?] 生命值")
                console.print("[%] 保存数据: ", end=None)
                if health > 0:
                    if cpm.set_player_health(health):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请使用有效数值! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 28:  # 自定义角度
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的角度[/bold yellow]")
                angle = IntPrompt.ask("[?] 角度")
                console.print("[%] 保存数据: ", end=None)
                if angle >= 0 and angle <= 360:
                    if cpm.set_player_angle(angle):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请使用有效数值! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 29:  # 自定义轮胎燃烧器
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的轮胎燃烧器设置[/bold yellow]")
                burner_setting = Prompt.ask("[?] 设置")
                console.print("[%] 保存数据: ", end=None)
                if burner_setting:
                    if cpm.set_tire_burner_setting(burner_setting):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]设置不能为空! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 30:  # 自定义车辆里程
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的车辆里程[/bold yellow]")
                mileage = IntPrompt.ask("[?] 里程")
                console.print("[%] 保存数据: ", end=None)
                if mileage >= 0:
                    if cpm.set_vehicle_mileage(mileage):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请使用有效数值! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 31:  # 自定义车辆刹车
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的车辆刹车设置[/bold yellow]")
                brake_setting = Prompt.ask("[?] 设置")
                console.print("[%] 保存数据: ", end=None)
                if brake_setting:
                    if cpm.set_vehicle_brake_setting(brake_setting):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]设置不能为空! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 32:  # 移除后保险杠
                console.print("[%] 移除后保险杠: ", end=None)
                if cpm.remove_rear_bumper():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 33:  # 移除前保险杠
                console.print("[%] 移除前保险杠: ", end=None)
                if cpm.remove_front_bumper():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 34:  # 更改账户密码
                console.print("[bold yellow][bold white][?][/bold white] 输入您的新账户密码[/bold yellow]")
                new_password = Prompt.ask("[?] 密码", password=True)
                console.print("[%] 更改账户密码: ", end=None)
                if new_password:
                    if cpm.change_account_password(new_password):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]密码不能为空! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 35:  # 更改账户邮箱
                console.print("[bold yellow][bold white][?][/bold white] 输入您的新账户邮箱[/bold yellow]")
                new_email = Prompt.ask("[?] 邮箱")
                console.print("[%] 更改账户邮箱: ", end=None)
                if new_email:
                    if cpm.change_account_email(new_email):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]邮箱不能为空! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 36:  # 自定义扰流板
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的扰流板设置[/bold yellow]")
                spoiler_setting = Prompt.ask("[?] 设置")
                console.print("[%] 保存数据: ", end=None)
                if spoiler_setting:
                    if cpm.set_spoiler_setting(spoiler_setting):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]设置不能为空! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 37:  # 自定义车身套件
                console.print("[bold yellow][bold white][?][/bold white] 输入您想要自定义的车身套件设置[/bold yellow]")
                body_kit_setting = Prompt.ask("[?] 设置")
                console.print("[%] 保存数据: ", end=None)
                if body_kit_setting:
                    if cpm.set_body_kit_setting(body_kit_setting):
                        console.print("[bold green]操作成功 (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                        if answ == "y":
                            console.print("[bold white] 感谢使用本工具[/bold white]")
                            break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]设置不能为空! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 38:  # 解锁高级车轮
                console.print("[%] 解锁高级车轮: ", end=None)
                if cpm.unlock_advanced_wheels():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                else:
                    console.print("[bold red]操作失败 (✘)[/bold red]")
                    console.print("[bold red]请稍后重试! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 39:  # 解锁丰田皇冠
                console.print("[%] 解锁丰田皇冠: ", end=None)
                if cpm.unlock_toyota_crown():
                    console.print("[bold green]操作成功 (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 是否退出？", choices=["y", "n"], default="n")
                    if answ == "y":
                        console.print("[bold white] 感谢使用本工具[/bold white]")
                        break
                    else:
                        console.print("[bold red]操作失败 (✘)[/bold red]")
                        console.print("[bold red]请稍后重试! (✘)[/bold red]")
                        sleep(2)
                        continue 