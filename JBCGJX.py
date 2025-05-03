 #!/usr/bin/python
#!/usr/bin/python
import random
import urllib.parse
import requests
from time import sleep
import os, signal, sys
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.style import Style
from cylo import Bubcyz  # 确保 cylo.py 存在

# —— 鲜亮彩虹渐变色带 ——
BRIGHT_RAINBOW = [  # <-- 顶格，无缩进
    "#FF4500",  # 橙红
    "#FF8C00",  # 深橙
    "#FFD700",  # 金黄
    "#ADFF2F",  # 黄绿
    "#00FA9A",  # 中春绿
    "#00CED1",  # 暗绿松石
    "#1E90FF",  # 道奇蓝
    "#8A2BE2",  # 蓝紫
    "#EE82EE",  # 紫罗兰
]

# —— 新增输入提示样式和渐变颜色 ——
INPUT_PROMPT_STYLE = Style(color="#00CED1", bold=True, italic=True)  # <-- 顶格
GRADIENT_COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD"]  # <-- 顶格

# 捕捉 Ctrl+C
def signal_handler(sig, frame):  # <-- 顶格，函数定义无缩进
    print("\nBye Bye...")
    sys.exit(0)

# 水平亮彩虹渐变函数
def gradient_text(text: str, colors: list[str]) -> Text:
    lines = text.splitlines()
    width = max((len(line) for line in lines), default=0)
    segs = max(len(colors) - 1, 1)
    out = Text()
    for line in lines:
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
                # 修复颜色转换部分
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

# 简单小动物 ASCII 艺术
ascii_art = r"""
             (\_/)
             ( •_•)
             />🍪
"""

 # 登录欢迎界面
def banner(console: Console):
     os.system('cls' if os.name == 'nt' else 'clear')
     # 渐变小动物（移除居中）
     console.print(gradient_text(ascii_art, BRIGHT_RAINBOW))  # 移除 justify="center"
     # 分隔符 & 欢迎文本（移除居中）
     sep = gradient_text("★☆" * 17, BRIGHT_RAINBOW)
     console.print(sep)  # 移除 justify="center"
     console.print(gradient_text("     欢迎来到季伯常的工具箱      ", BRIGHT_RAINBOW))  # 前后各6空格
     console.print(gradient_text("     快手搜索季伯常获取秘钥      ", BRIGHT_RAINBOW))
     console.print(sep)  # 移除居中   
def load_player_data(cpm, console: Console):
    response = cpm.get_player_data()
    
    if response.get('ok'):
        data = response.get('data')
        required_keys = ['floats', 'localID', 'money', 'coin', 'integers']
        if all(key in data for key in required_keys):
            # 标题：粉色渐变 + 靠左
            title = gradient_text("ᴘʟᴀʏᴇʀ ᴅᴇᴛᴀɪʟꜱ", ["#FF69B4", "#FF1493"])
            console.print(f"\n[bold]{title}[/bold]")  # 移除居中
            
            # 处理成就点数
            integers_value = data.get('integers', 0)
            formatted_integers = f"{sum(integers_value):,}" if isinstance(integers_value, list) else f"{integers_value:,}"
            
            # 数据项（靠左对齐）
            items = [
                ("游戏昵称", data.get('Name', 'UNDEFINED')),
                ("玩家代码", data.get('localID', 'N/A')),
                ("绿钞余额", f"{data.get('money', 0):,}"),
                ("金币余额", f"{data.get('coin', 0):,}"),
                
            ]
            
            # 创建表格（强制左对齐）
            table = Table(show_header=False, box=None, show_edge=False)
            table.add_column(style=Style(color="#FF69B4"))  # 粉色字段名
            table.add_column(style=Style(color="white"))     # 白色数值
            
            for label, value in items:
                # 字段名添加冒号 + 粉色渐变
                colored_label = gradient_text(f"{label} :", ["#FF69B4", "#FF1493"])
                table.add_row(colored_label, f"[bold]{value}[/bold]")
            
            console.print(table)  # 不居中
            
            # 分隔线（粉色渐变 + 左对齐）
            sep = gradient_text("─" * 40, ["#FF69B4", "#FF1493"])
            console.print(sep)
        else:
            console.print("[bold red]! ERROR: 新账号需至少登录游戏一次 (✘)[/bold red]")
            exit(1)
    else:
        console.print("[bold red]! ERROR: 登录凭证无效 (✘)[/bold red]")
        exit(1)

def load_key_data(cpm):
    """加载并展示CPM密钥数据"""
    data = cpm.get_key_data()
    
    # 标题：粉色渐变 + 左对齐
    title = gradient_text("CPM季伯常专属工具箱", ["#FF69B4", "#FF1493"])
    console.print(f"\n[bold]{title}[/bold]")  # 不居中
    
    # 敏感信息部分
    items = [
        ("你的秘钥", "[dark_gray]********[/dark_gray]"),
        ("TG ID", data.get('telegram_id', 'N/A')),
        ("秘钥余额", 'Unlimited' if data.get('is_unlimited') else data.get('coins', 'N/A'))
    ]
    
    # 统一粉色渐变样式
    for label, value in items:
        # 字段名（含 >> 符号）应用渐变
        colored_label = gradient_text(f">> {label.ljust(4)}", ["#FF69B4", "#FF1493"])  # 调整对齐长度
        console.print(f"{colored_label} : [bold white]{value}[/bold white]")


def prompt_valid_value(content, tag, password=False):
    """带验证的输入提示"""
    while True:
        value = Prompt.ask(content, password=password)
        if not value or value.isspace():
            console.print(f"[bold red]{tag} 不能为空或纯空格，请重新输入 (✘)[/bold red]")
        else:
            return value
            
def load_client_details():
    response = requests.get("http://ip-api.com/json")
    data = response.json()
    console.print("[bold red] =============[bold white][ 𝙇𝙊𝘾𝘼𝙏𝙄𝙊𝙉 ][/bold white]=============[/bold red]")
    console.print(f"[bold white]>>登录地址        : {data.get('country')} {data.get('zip')}[/bold white]")
    console.print("[bold red] =============[bold white][ ＭＥＮＵ ][/bold white]==============[/bold red]")

def interpolate_color(start_color, end_color, fraction):
    start_rgb = tuple(int(start_color[i:i+2], 16) for i in (1, 3, 5))
    end_rgb = tuple(int(end_color[i:i+2], 16) for i in (1, 3, 5))
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
        acc_email = prompt_valid_value("[bold][?] Account Email[/bold]", "Email", password=False)
        acc_password = prompt_valid_value("[bold][?] Account Password[/bold]", "Password", password=False)
        acc_access_key = prompt_valid_value("[bold][?] Access Key[/bold]", "Access Key", password=False)
        console.print("[bold yellow][%] Trying to Login[/bold yellow]: ", end=None)
        cpm = Bubcyz(acc_access_key)
        login_response = cpm.login(acc_email, acc_password)
        if login_response != 0:
            if login_response == 100:
                console.print("[bold red]ACCOUNT NOT FOUND (✘)[/bold red]")
                sleep(2)
                continue
            elif login_response == 101:
                console.print("[bold red]WRONG PASSWORD (✘)[/bold red]")
                sleep(2)
                continue
            elif login_response == 103:
                console.print("[bold red]INVALID ACCESS KEY (✘)[/bold red]")
                sleep(2)
                continue
            else:
                console.print("[bold red]TRY AGAIN[/bold red]")
                console.print("[bold yellow] '! Note: make sure you filled out the fields ![/bold yellow]")
                sleep(2)
                continue
        else:
            console.print("[bold green]芜湖小飞棍起飞咯 (✔)[/bold green]")
            sleep(1)
        while True:
            banner(console)
            load_player_data(cpm, console)
            load_key_data(cpm)
            load_client_details()
                        # ========== 菜单部分 ==========
            MENU_GRADIENT = [
                "#9370DB", "#8A2BE2", "#9400D3", 
                "#9932CC", "#BA55D3"
            ]

            # 创建两列表格布局
            menu_table = Table.grid(padding=(0, 1))
            menu_table.add_column(justify="left", width=20)
            menu_table.add_column(justify="right", width=15)

            # 修正后的功能列表（删除无效序号）
            choices = [
            "0","01","02","03","04","05","06","07","08","09",
            "10","11","12","13","14","15","16","17","18","19",
            "20","21","22","23","24","25","26","27","28","29"
        ]

            menu_items = [
        ("01", "获得绿钞", "5K"), 
        ("02", "获得C币", "10K"),
        ("03", "皇冠满成就", "30K"),  
        ("04", "更改ID", "30K"),
        ("05", "修改长昵称", "5K"), 
        ("06", "车牌修改", "5K"),
        ("07", "删除好友", "5K"),
        ("08", "解锁付费车", "5K"), 
        ("09", "全车辆解锁", "10K"),
        ("10", "车辆警笛", "5K"), 
        ("11", "W16引擎", "5K"),
        ("12", "全喇叭解锁", "5K"), 
        ("13", "禁用发动机损坏", "5K"),
        ("14", "无限燃料", "5K"),  
        ("15", "解锁房屋3", "5K"),
        ("16", "烟雾特效", "5K"),  
        ("17", "动画解锁", "5K"),  
        ("18", "男装全解锁", "5K"),
        ("19", "女装全解锁", "5K"),
        ("20", "修改胜场数", "5K"),
        ("21", "修改败场数", "5K"),
        ("22", "克隆账户", "50K"),
        ("23", "自定义马力", "5K"),
        ("24", "后保险杠", "5K"),
        ("25", "前保险杠", "5K"),
        ("26", "强改密码", "10K"),
        ("27", "强改邮箱", "10K"),
        ("28", "自定义尾翼", "5K"),
        ("29", "车身套件", "5K"),
        ("0", "退出系统", "")
]

            # 填充菜单项
            for num, desc, price in menu_items:
                colored_item = gradient_text(f"({num}) {desc}", MENU_GRADIENT)
                colored_price = gradient_text(price, MENU_GRADIENT) if price else ""
                menu_table.add_row(colored_item, colored_price)

            # 打印菜单
            console.print(gradient_text("━"*11 + "【季伯常 工具箱】" + "━"*11, MENU_GRADIENT))
            console.print(menu_table)
            console.print(gradient_text("━"*11 + "【功能区 选择区】" + "━"*11, MENU_GRADIENT))

            service = IntPrompt.ask(
                gradient_text("请输入功能编号以后按回车 ▶", MENU_GRADIENT),
                choices=choices,
                show_choices=False
            )
            # ========== 菜单部分结束 ==========
            
            if service == 0 or service == "00": # Exit
                console.print("[bold white] 感谢使用 有任何问题快手联系老季[/bold white]")
            elif service == 1: # Increase Money
                console.print("[bold yellow][bold white][?][/bold white] 请输入游戏你想显示的金币数量?[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                console.print("[%] 正在保存数据: ", end=None)
                if 0 < amount <= 500000000:
                    if cpm.set_player_money(amount):
                        console.print("[bold green]✓ 数据保存成功[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 是否退出？(y退出/n返回) ", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] 感谢使用 有任何问题快手联系老季[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]✘ 操作失败：数量输入错误[/bold red]")
                        console.print("[bold red]我也不知道 你再试试 (✘)[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]账密或者秘钥错误 (✘)[/bold red]")
                    console.print("[bold red]请你看看账密或者秘钥! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 2:  # Increase Coins
                console.print("[bold yellow][bold white][?][/bold white] 请输入游戏你想显示的金币数量?[/bold yellow]")
                amount = IntPrompt.ask("[?] Amount")
                print("[ % ] Saving your data: ", end="")
                if amount > 0 and amount <= 500000:
                    if cpm.set_player_coins(amount):
                        console.print("[bold green]保存中  (✔)[/bold green]")
                        console.print("[bold green]======================================[/bold green]")
                        answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] 欢迎使用老季工具箱下次再来[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]保存中[/bold red]")
                        console.print("[bold red]有点问题 请重试[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] 'Please use valid values[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 3: # 刷满成就
                console.print("[bold red][!] Note:[/bold red]: 正在帮你刷满成就.", end=None)
                console.print("[bold red][!] Note:[/bold red]: ⚠ 提示：操作后请重新登录游戏查看皇冠标志", end=None)
                sleep(2)
                console.print("[%] 正在帮你刷满成就请耐心等待: ", end=None)
                if cpm.set_player_rank():
                    console.print("[bold yellow] ' 成就数据已同步[/bold yellow]")
                    console.print("[bold yellow] '======================================[/bold yellow]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] 欢迎使用老季工具箱下次再来[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 4: # 修改ID
                console.print("[bold yellow] '[?] 输入你的新ID号码直接回车 支持纯数字纯字母纯汉字 不能有空格会报错[/bold yellow]")
                new_id = Prompt.ask("[?] ID")
                console.print("[%] Saving your data: ", end=None)
                if len(new_id) >= 0 and len(new_id) <= 9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 and (' ' in new_id) == False:
                    if cpm.set_player_localid(new_id.upper()):
                        console.print("[bold yellow] '修改成功 老季牛B[/bold yellow]")
                        console.print("[bold yellow] '======================================[/bold yellow]")
                        answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] 欢迎使用老季工具箱下次再来[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]报错了[/bold red]")
                        console.print("[bold red]检查有无空格重试一下[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]报错[/bold red]")
                    console.print("[bold yellow] '请你看清楚有没有空格[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 5: # 修改长名
                console.print("[bold yellow] '[?] 改游戏长名字需要和ID一摸一样的否则进游戏恢复默认[/bold yellow]")
                new_name = Prompt.ask("[?] Name")
                console.print("[%] Saving your data: ", end=None)
                if len(new_name) >= 0 and len(new_name) <= 999999999:
                    if cpm.set_player_name(new_name):
                        console.print("[bold yellow] '保存中[/bold yellow]")
                        console.print("[bold yellow] '======================================[/bold yellow]")
                        answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] 欢迎使用老季工具箱下次再来[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] 'Please use valid values[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 6: # Change Name Rainbow
                console.print("[bold yellow] '[?] Enter your new Rainbow Name[/bold yellow]")
                new_name = Prompt.ask("[?] Name")
                console.print("[%] Saving your data: ", end=None)
                if len(new_name) >= 0 and len(new_name) <= 999999999:
                    if cpm.set_player_name(rainbow_gradient_string(new_name)):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print("[bold yellow] '======================================[/bold yellow]")
                        answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] 欢迎使用老季工具箱下次再来[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] 'Please use valid values[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 7: # Number Plates
                console.print("[%] Giving you a Number Plates: ", end=None)
                if cpm.set_player_plates():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] 欢迎使用老季工具箱下次再来[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 8: # 删除账号
                console.print("[bold yellow] '[!] After deleting your account there is no going back !![/bold yellow]")
                answ = Prompt.ask("[?] 确定删除账号原地退游 ?!", choices=["y", "n"], default="n")
                if answ == "y":
                    cpm.delete()
                    console.print("[bold yellow] '删完了你退游吧[/bold yellow]")
                    console.print("[bold yellow] '======================================[/bold yellow]")
                    console.print("[bold yellow] f'完成了 拜拜了老六[/bold yellow]")
                else: continue
            elif service == 9: # Account Register
                console.print("[bold yellow] '[!] Registring new Account[/bold yellow]")
                acc2_email = prompt_valid_value("[?] Account Email", "Email", password=False)
                acc2_password = prompt_valid_value("[?] Account Password", "Password", password=False)
                console.print("[%] Creating new Account: ", end=None)
                status = cpm.register(acc2_email, acc2_password)
                if status == 0:
                    console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                    console.print("[bold yellow] '======================================[/bold yellow]")
                    console.print("[bold yellow] f'INFO: In order to tweak this account with Telmun[/bold yellow]")
                    console.print("[bold yellow] 'you most sign-in to the game using this account[/bold yellow]")
                    sleep(2)
                    continue
                elif status == 105:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] 'This email is already exists ![/bold yellow]")
                    sleep(2)
                    continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 10: # Delete Friends
                console.print("[%] Deleting your Friends: ", end=None)
                if cpm.delete_player_friends():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 11: # Unlock All Paid Cars
                console.print("[!] Note: this function takes a while to complete, please don't cancel.", end=None)
                console.print("[%] Unlocking All Paid Cars: ", end=None)
                if cpm.unlock_paid_cars():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 12: # Unlock All Cars
                console.print("[%] Unlocking All Cars: ", end=None)
                if cpm.unlock_all_cars():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 13: # Unlock All Cars Siren
                console.print("[%] Unlocking All Cars Siren: ", end=None)
                if cpm.unlock_all_cars_siren():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?]保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 14: # Unlock w16 Engine
                console.print("[%] Unlocking w16 Engine: ", end=None)
                if cpm.unlock_w16():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 15: # Unlock All Horns
                console.print("[%] Unlocking All Horns: ", end=None)
                if cpm.unlock_horns():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 16: # Disable Engine Damage
                console.print("[%] Unlocking Disable Damage: ", end=None)
                if cpm.disable_engine_damage():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?]保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 17: # Unlimited Fuel
                console.print("[%] Unlocking Unlimited Fuel: ", end=None)
                if cpm.unlimited_fuel():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 18: # Unlock House 3
                console.print("[%] Unlocking House 3: ", end=None)
                if cpm.unlock_houses():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 19: # Unlock Smoke
                console.print("[%] Unlocking Smoke: ", end=None)
                if cpm.unlock_smoke():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?]保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 20: # Unlock Smoke
                console.print("[%] Unlocking Wheels: ", end=None)
                if cpm.unlock_wheels():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(8)
                    continue
            elif service == 21: # Unlock Smoke
                console.print("[%] Unlocking Animations: ", end=None)
                if cpm.unlock_animations():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 22: # Unlock Smoke
                console.print("[%] Unlocking Equipaments Male: ", end=None)
                if cpm.unlock_equipments_male():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?]保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 23: # Unlock Smoke
                console.print("[%] Unlocking Equipaments Female: ", end=None)
                if cpm.unlock_equipments_female():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 24: # Change Races Wins
                console.print("[bold yellow] '[!] Insert how much races you win[/bold yellow]")
                amount = IntPrompt.ask("[?] Amount")
                console.print("[%] Changing your data: ", end=None)
                if amount > 0 and amount <= 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999:
                    if cpm.set_player_wins(amount):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print("[bold yellow] '======================================[/bold yellow]")
                        answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] '[!] Please use valid values[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 25: # Change Races Loses
                console.print("[bold yellow] '[!] Insert how much races you lose[/bold yellow]")
                amount = IntPrompt.ask("[?] Amount")
                console.print("[%] Changing your data: ", end=None)
                if amount > 0 and amount <= 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999:
                    if cpm.set_player_loses(amount):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print("[bold yellow] '======================================[/bold yellow]")
                        answ = Prompt.ask("[?]保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                        if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                        else: continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold yellow] '[!] Please use valid values[/bold yellow]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] '[!] Please use valid values[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 26: # Clone Account
                console.print("[bold yellow] '[!] Please Enter Account Detalis[/bold yellow]")
                to_email = prompt_valid_value("[?] Account Email", "Email", password=False)
                to_password = prompt_valid_value("[?] Account Password", "Password", password=False)
                console.print("[%] Cloning your account: ", end=None)
                if cpm.account_clone(to_email, to_password):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:     
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] '[!] THAT RECIEVER ACCOUNT IS GMAIL PASSWORD IS NOT VALID OR THAT ACCOUNT IS NOT REGISTERED[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 27:
                console.print("[bold yellow][!] Note[/bold yellow]: original speed can not be restored!.")
                console.print("[bold yellow][!] Enter Car Details.[/bold yellow]")
                car_id = IntPrompt.ask("[bold][?] Car Id[/bold]")
                new_hp = IntPrompt.ask("[bold][?]Enter New HP[/bold]")
                new_inner_hp = IntPrompt.ask("[bold][?]Enter New Inner Hp[/bold]")
                new_nm = IntPrompt.ask("[bold][?]Enter New NM[/bold]")
                new_torque = IntPrompt.ask("[bold][?]Enter New Torque[/bold]")
                console.print("[bold yellow][%] Hacking Car Speed[/bold yellow]:",end=None)
                if cpm.hack_car_speed(car_id, new_hp, new_inner_hp, new_nm, new_torque):
                    console.print("[bold green]SUCCESFUL (✔)[/bold green]")
                    console.print("================================")
                    answ = Prompt.ask("[?]保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] '[!] Please use valid values[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 28: # ANGLE
                console.print("[bold yellow] '[!] ENTER CAR DETALIS[/bold yellow]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")
                console.print("[bold yellow] '[!] ENTER STEERING ANGLE[/bold yellow]")
                custom = IntPrompt.ask("[red][?]﻿ENTER THE AMOUNT OF ANGLE YOU WANT[/red]")                
                console.print("[red][%] HACKING CAR ANGLE[/red]: ", end=None)
                if cpm.max_max1(car_id, custom):
                    console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                    answ = Prompt.ask("[red][?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 29: # tire
                console.print("[bold yellow] '[!] ENTER CAR DETALIS[/bold yellow]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")
                console.print("[bold yellow] '[!] ENTER PERCENTAGE[/bold yellow]")
                custom = IntPrompt.ask("[pink][?]﻿ENTER PERCENTAGE TIRES U WANT[/pink]")                
                console.print("[red][%] Setting Percentage [/red]: ", end=None)
                if cpm.max_max2(car_id, custom):
                    console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                    answ = Prompt.ask("[bold green][?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 30: # Millage
                console.print("[bold]ENTER CAR DETAILS![/bold]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")
                console.print("[bold]ENTER NEW MILLAGE![/bold]")
                custom = IntPrompt.ask("[bold blue][?]﻿ENTER MILLAGE U WANT[/bold blue]")                
                console.print("[bold red][%] Setting Percentage [/bold red]: ", end=None)
                if cpm.millage_car(car_id, custom):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 31: # Brake
                console.print("[bold]ENTER CAR DETAILS![/bold]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")
                console.print("[bold]ENTER NEW BRAKE![/bold]")
                custom = IntPrompt.ask("[bold blue][?]﻿ENTER BRAKE U WANT[/bold blue]")                
                console.print("[bold red][%] Setting BRAKE [/bold red]: ", end=None)
                if cpm.brake_car(car_id, custom):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 32: # Bumper rear
                console.print("[bold]ENTER CAR DETAILS![/bold]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")                
                console.print("[bold red][%] Removing Rear Bumper [/bold red]: ", end=None)
                if cpm.rear_bumper(car_id):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 33: # Bumper front
                console.print("[bold]ENTER CAR DETAILS![/bold]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")                
                console.print("[bold red][%] Removing Front Bumper [/bold red]: ", end=None)
                if cpm.front_bumper(car_id):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 75:  # /testin endpoint
                console.print("[bold]ENTER CUSTOM FLOAT DATA[/bold]")
                custom = IntPrompt.ask("[bold][?] VALUE (e.g. 1 or 0)[/bold]")     # This is the value
                console.print(f"[bold red][%] Setting float key... [/bold red]", end=None)
                if cpm.testin(custom):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold yellow]FAILED[/bold yellow]")
                    console.print("[bold yellow]PLEASE TRY AGAIN[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 34:
                console.print("[bold]Enter New Password![/bold]")
                new_password = prompt_valid_value("[bold][?] Account New Password[/bold]", "Password", password=False)
                console.print("[bold red][%] Changing Password [/bold red]: ", end=None)
                if cpm.change_password(new_password):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white]Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold yellow]FAILED[/bold yellow]")
                    console.print("[bold yellow]PLEASE TRY AGAIN[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 36: # telmunnongodz
                console.print("[bold]ENTER CAR DETAILS![/bold]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")
                console.print("[bold]ENTER SPOILER ID![/bold]")
                custom = IntPrompt.ask("[bold blue][?]ENTER NEW SPOILER ID[/bold blue]")                
                console.print("[bold red][%] SAVING YOUR DATA [/bold red]: ", end=None)
                if cpm.telmunnongodz(car_id, custom):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 37: # telmunnongonz
                console.print("[bold]ENTER CAR DETAILS![/bold]")
                car_id = IntPrompt.ask("[bold][?] CAR ID[/bold]")
                console.print("[bold]ENTER BODYKIT ID![/bold]")
                custom = IntPrompt.ask("[bold blue][?]INSERT BODYKIT ID[/bold blue]")                
                console.print("[bold red][%] SAVING YOUR DATA [/bold red]: ", end=None)
                if cpm.telmunnongonz(car_id, custom):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 35:
                console.print("[bold]Enter New Email![/bold]")
                new_email = prompt_valid_value("[bold][?] Account New Email[/bold]", "Email")
                console.print("[bold red][%] Changing Email [/bold red]: ", end=None)
                if cpm.change_email(new_email):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    answ = Prompt.ask("[bold][?] 保存成功是否退出？(y退出/n返回) ?", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white]Thank You for using my tool[/bold white]")
                    else: break
                else:
                    console.print("[bold red]FAILED[/bold yellow]")
                    console.print("[bold red]EMAIL IS ALREADY REGISTERED [/bold red]")
                    sleep(4)
            elif service == 38: # SHITTIN
                console.print("[%] Unlocking Premium Wheels..: ", end=None)
                if cpm.shittin():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 39: # Unlock toyota crown
                console.print("[!] Note: this function takes a while to complete, please don't cancel.", end=None)
                console.print("[%] Unlocking Toyota Crown: ", end=None)
                if cpm.unlock_crown():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print("[bold green]======================================[/bold green]")
                    answ = Prompt.ask("[?] 保存成功是否退出？(y退出/n返回)", choices=["y", "n"], default="n")
                    if answ == "y": console.print("[bold white] Thank You for using my tool[/bold white]")
                    else: continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            else:
                continue
            break
        break              
