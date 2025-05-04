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
            title = gradient_text("          CPM季伯常专属工具箱", ["#FFD700", "#FFA500"])  # 粉色渐变
            console.print(f"\n[bold]{title}[/bold]")  # 保留加粗样式
            
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
    title = gradient_text("          CPM季伯常专属工具箱", ["#FF69B4", "#FF1493"])
    console.print(f"\n[bold]{title}[/bold]")  # 不居中
    
    # 敏感信息部分
    items = [
        ("你的秘钥", Text("********", style="dark_gray")),
        ("TG ID", data.get('telegram_id', 'N/A')),
        ("秘钥余额", 'Unlimited' if data.get('is_unlimited') else data.get('coins', 'N/A'))
    ]
    
    # 创建双列表格（标签左对齐，值右对齐）
    table = Table.grid(padding=(0, 2))  # 列间距为2字符
    table.add_column(justify="left", width=15)   # 标签列左对齐
    table.add_column(justify="right", width=20)  # 值列右对齐
    
    # 填充数据（单行显示）
    for label, value in items:
        # 生成渐变标签（固定宽度12字符）
        colored_label = gradient_text(f">> {label.ljust(12)}", ["#00BFFF", "#87CEEB"])
        # 处理值的样式
        if isinstance(value, Text):
            colored_value = value
        else:
            colored_value = Text(str(value), style="bold white")
        
        # 添加单行组合
        table.add_row(colored_label, colored_value)
    
    console.print(table)


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
    console.print("[bold #FF69B4] ===========[bold #FF69B4][ 快手搜索季伯常 ][/bold #FF69B4]==========[/bold #FF69B4]")
    console.print(f"[bold #FF69B4]>>登录地址                    : {data.get('country')} {data.get('zip')}[/bold #FF69B4]")
    console.print("[bold #FF69B4] ============[bold #FF69B4][ 季伯常菜单栏 ][/bold #FF69B4]===========[/bold #FF69B4]")

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
    while True:  # 外层循环：处理登录和主菜单
        # ------ 登录流程 ------
        banner(console)
        acc_email = prompt_valid_value("[bold][?] 账号邮箱[/bold]", "邮箱", password=False)
        acc_password = prompt_valid_value("[bold][?] 账号密码[/bold]", "密码", password=False)
        acc_access_key = prompt_valid_value("[bold][?] 访问密钥[/bold]", "密钥", password=False)
        console.print("[bold yellow][%] 正在尝试登录...[/bold yellow]")
        cpm = Bubcyz(acc_access_key)
        login_response = cpm.login(acc_email, acc_password)

        # ------ 登录错误处理 ------
        if login_response != 0:
            if login_response == 100:
                console.print("[bold red]错误：账号不存在 (✘)[/bold red]")
            elif login_response == 101:
                console.print("[bold red]错误：密码错误 (✘)[/bold red]")
            elif login_response == 103:
                console.print("[bold red]错误：无效的访问密钥 (✘)[/bold red]")
            else:
                console.print("[bold red]错误：登录失败，请检查输入 (✘)[/bold red]")
            sleep(2)
            continue  # 返回外层循环重新登录
        else:
            console.print("[bold green]登录成功！小飞棍来咯~ (✔)[/bold green]")
            sleep(1)

        # ------ 功能菜单循环（内层循环）------
        while True:
            banner(console)
            load_player_data(cpm, console)
            load_key_data(cpm)
            load_client_details()

            # ------ 菜单显示 ------
            MENU_GRADIENT = ["#9370DB", "#8A2BE2", "#9400D3", "#9932CC", "#BA55D3"]
            menu_table = Table.grid(padding=(0, 0, 0, 5))  # 移除所有内边距
            menu_table.add_column(justify="left", width=22)  # 描述列
            menu_table.add_column(justify="left", width=3)   # 价格列调整为紧凑宽度

            menu_items = [
        ("01", "获得绿钞：", "5K"), 
        ("02", "获得C币：", "10K"),
        ("03", "皇冠满成就：", "30K"),  
        ("04", "更改ID：", "30K"),
        ("05", "修改长昵称：", "5K"), 
        ("06", "车牌修改：", "5K"),
        ("07", "删除好友：", "5K"),
        ("08", "解锁付费车：", "5K"), 
        ("09", "全车辆解锁：", "10K"),
        ("10", "车辆警笛：", "5K"), 
        ("11", "W16引擎：", "5K"),
        ("12", "全喇叭解锁：", "5K"), 
        ("13", "关发动机损坏：", "5K"),
        ("14", "无限燃料：", "5K"),  
        ("15", "解锁房屋3：", "5K"),
        ("16", "烟雾特效：", "5K"),  
        ("17", "动画解锁：", "5K"),  
        ("18", "男装全解锁：", "5K"),
        ("19", "女装全解锁：", "5K"),
        ("20", "修改胜场数：", "5K"),
        ("21", "修改败场数：", "5K"),
        ("22", "克隆账户：", "50K"),
        ("23", "自定义马力：", "5K"),
        ("24", "后保险杠：", "5K"),
        ("25", "前保险杠：", "5K"),
        ("26", "强改密码：", "10K"),
        ("27", "强改邮箱：", "10K"),
        ("28", "自定义尾翼：", "5K"),
        ("29", "车身套件：", "5K"),
        ("0", "退出系统：", "")
]

            # 填充菜单项
            for num, desc, price in menu_items:
                colored_item = gradient_text(f"({num}) {desc}", MENU_GRADIENT)
                colored_price = gradient_text(price, MENU_GRADIENT) if price else ""
                menu_table.add_row(colored_item, colored_price)

            console.print(gradient_text("━"*11 + "【季伯常的工具箱】" + "━"*11, MENU_GRADIENT))
            console.print(menu_table)
            console.print(gradient_text("━"*11 + "【请选择功能】" + "━"*11, MENU_GRADIENT))

            # ------ 功能选择 ------
            service = IntPrompt.ask(
                gradient_text("请输入功能编号后按回车 ▶", MENU_GRADIENT),
                choices=[str(i) for i in range(30)],
                show_choices=False
            )
            # ========== 菜单部分结束 ==========
            
            # ========== 功能分支处理（1-29） ==========
            if service == 0:  # 退出系统
                console.print("[bold cyan]感谢使用！有问题请快手联系老季[/bold cyan]")
                sys.exit(0)

            elif service == 1:  # 获得绿钞
                console.print("[bold yellow][?] 请输入绿钞数量（1-500,000,000）[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                console.print("[%] 正在保存数据...", end="")
                if 0 < amount <= 500000000:
                    if cpm.set_player_money(amount):
                        console.print("\n[bold green]✓ 绿钞已到账[/bold green]")
                    else:
                        console.print("\n[bold red]✘ 操作失败：请检查密钥有效性[/bold red]")
                else:
                    console.print("\n[bold red]✘ 输入值超出有效范围[/bold red]")
                sleep(2)

            elif service == 2:  # 获得C币
                console.print("[bold yellow][?] 请输入C币数量（1-500,000）[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                console.print("[%] 正在保存数据...", end="")
                if 0 < amount <= 500000:
                    if cpm.set_player_coins(amount):
                        console.print("\n[bold green]✓ C币已到账[/bold green]")
                    else:
                        console.print("\n[bold red]✘ 操作失败[/bold red]")
                else:
                    console.print("\n[bold red]✘ 输入值超出有效范围[/bold red]")
                sleep(2)

            elif service == 3:  # 皇冠满成就
                console.print("[%] 正在同步成就数据...")
                if cpm.set_player_rank():
                    console.print("[bold green]✓ 成就已满级，请重新登录查看[/bold green]")
                else:
                    console.print("[bold red]✘ 同步失败[/bold red]")
                sleep(2)

            elif service == 4:  # 更改ID
                console.print("[bold yellow][!] 新ID不能包含空格（支持中英文/数字）[/bold yellow]")
                new_id = Prompt.ask("[?] 输入新ID")
                if ' ' not in new_id:
                    if cpm.set_player_localid(new_id.upper()):
                        console.print("[bold green]✓ ID修改成功[/bold green]")
                    else:
                        console.print("[bold red]✘ 非法字符或服务器错误[/bold red]")
                else:
                    console.print("[bold red]✘ ID包含空格[/bold red]")
                sleep(2)

            elif service == 5:  # 修改长昵称
                console.print("[bold yellow][!] 长昵称需与游戏ID一致[/bold yellow]")
                new_name = Prompt.ask("[?] 输入新昵称")
                if cpm.set_player_name(new_name):
                    console.print("[bold green]✓ 昵称已更新[/bold green]")
                else:
                    console.print("[bold red]✘ 修改失败[/bold red]")
                sleep(2)

            elif service == 6:  # 彩虹名称
                console.print("[bold yellow][?] 输入彩虹特效名称（支持特殊字符）[/bold yellow]")
                new_name = Prompt.ask("[?] 名称")
                if cpm.set_player_name(rainbow_gradient_string(new_name)):
                    console.print("[bold green]✓ 特效名称已应用[/bold green]")
                else:
                    console.print("[bold red]✘ 应用失败[/bold red]")
                sleep(2)

            elif service == 7:  # 车牌修改
                console.print("[%] 生成随机车牌中...")
                if cpm.set_player_plates():
                    console.print("[bold green]✓ 新车牌已生效[/bold green]")
                else:
                    console.print("[bold red]✘ 生成失败[/bold red]")
                sleep(2)

            elif service == 8:  # 解锁付费车
                console.print("[%] 正在解锁付费车辆...")
                if cpm.unlock_paid_cars():
                    console.print("[bold green]✓ 所有付费车辆已解锁[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 9:  # 全车辆解锁
                console.print("[%] 正在解锁全部车辆...")
                if cpm.unlock_all_cars():
                    console.print("[bold green]✓ 车库已全开[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 10:  # 车辆警笛
                console.print("[%] 正在解锁警笛功能...")
                if cpm.unlock_all_cars_siren():
                    console.print("[bold green]✓ 警笛已激活[/bold green]")
                else:
                    console.print("[bold red]✘ 激活失败[/bold red]")
                sleep(2)

            elif service == 11:  # W16引擎
                console.print("[%] 正在安装W16引擎...")
                if cpm.unlock_w16():
                    console.print("[bold green]✓ 引擎轰鸣声已就绪[/bold green]")
                else:
                    console.print("[bold red]✘ 安装失败[/bold red]")
                sleep(2)

            elif service == 12:  # 全喇叭解锁
                console.print("[%] 正在解锁全部喇叭...")
                if cpm.unlock_horns():
                    console.print("[bold green]✓ 喇叭库已全开[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 13:  # 禁用发动机损坏
                console.print("[%] 正在关闭发动机损坏...")
                if cpm.disable_engine_damage():
                    console.print("[bold green]✓ 发动机进入无敌模式[/bold green]")
                else:
                    console.print("[bold red]✘ 设置失败[/bold red]")
                sleep(2)

            elif service == 14:  # 无限燃料
                console.print("[%] 正在注入无限燃料...")
                if cpm.unlimited_fuel():
                    console.print("[bold green]✓ 油箱已永久满格[/bold green]")
                else:
                    console.print("[bold red]✘ 注入失败[/bold red]")
                sleep(2)

            elif service == 15:  # 解锁房屋3
                console.print("[%] 正在解锁第三套房...")
                if cpm.unlock_houses():
                    console.print("[bold green]✓ 海景房钥匙已到手[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 16:  # 烟雾特效
                console.print("[%] 正在加载烟雾特效...")
                if cpm.unlock_smoke():
                    console.print("[bold green]✓ 尾气彩虹烟雾已启用[/bold green]")
                else:
                    console.print("[bold red]✘ 加载失败[/bold red]")
                sleep(2)

            elif service == 17:  # 动画解锁
                console.print("[%] 正在解锁特殊动画...")
                if cpm.unlock_animations():
                    console.print("[bold green]✓ 炫酷动画已就绪[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 18:  # 男装全解锁
                console.print("[%] 正在解锁男士衣橱...")
                if cpm.unlock_equipments_male():
                    console.print("[bold green]✓ 男士时装库已全开[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 19:  # 女装全解锁
                console.print("[%] 正在解锁女士衣橱...")
                if cpm.unlock_equipments_female():
                    console.print("[bold green]✓ 女士时装库已全开[/bold green]")
                else:
                    console.print("[bold red]✘ 解锁失败[/bold red]")
                sleep(2)

            elif service == 20:  # 修改胜场数
                console.print("[bold yellow][?] 输入你想要显示的胜场数[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                if cpm.set_player_wins(amount):
                    console.print("[bold green]✓ 战绩已刷新[/bold green]")
                else:
                    console.print("[bold red]✘ 修改失败[/bold red]")
                sleep(2)

            elif service == 21:  # 修改败场数
                console.print("[bold yellow][?] 输入你想要显示的败场数[/bold yellow]")
                amount = IntPrompt.ask("[?] 数量")
                if cpm.set_player_loses(amount):
                    console.print("[bold green]✓ 战绩已刷新[/bold green]")
                else:
                    console.print("[bold red]✘ 修改失败[/bold red]")
                sleep(2)

            elif service == 22:  # 克隆账户
                console.print("[bold yellow][!] 请输入目标账户信息[/bold yellow]")
                to_email = prompt_valid_value("[?] 目标邮箱", "Email")
                to_password = prompt_valid_value("[?] 目标密码", "Password")
                if cpm.account_clone(to_email, to_password):
                    console.print("[bold green]✓ 账户克隆完成[/bold green]")
                else:
                    console.print("[bold red]✘ 目标账户无效或已存在[/bold red]")
                sleep(2)

            elif service == 23:  # 自定义马力
                console.print("[bold]请输入车辆参数[/bold]")
                car_id = IntPrompt.ask("[?] 车辆ID")
                new_hp = IntPrompt.ask("[?] 新马力值")
                new_inner_hp = IntPrompt.ask("[?] 内部马力值")
                new_nm = IntPrompt.ask("[?] 扭矩值")
                new_torque = IntPrompt.ask("[?] 最大扭矩")
                if cpm.hack_car_speed(car_id, new_hp, new_inner_hp, new_nm, new_torque):
                    console.print("[bold green]✓ 车辆性能已突破极限[/bold green]")
                else:
                    console.print("[bold red]✘ 参数错误[/bold red]")
                sleep(2)

            elif service == 24:  # 后保险杠
                console.print("[bold]请输入车辆ID[/bold]")
                car_id = IntPrompt.ask("[?] 车辆ID")
                if cpm.rear_bumper(car_id):
                    console.print("[bold green]✓ 后保险杠已移除[/bold green]")
                else:
                    console.print("[bold red]✘ 操作失败[/bold red]")
                sleep(2)

            elif service == 25:  # 前保险杠
                console.print("[bold]请输入车辆ID[/bold]")
                car_id = IntPrompt.ask("[?] 车辆ID")
                if cpm.front_bumper(car_id):
                    console.print("[bold green]✓ 前保险杠已移除[/bold green]")
                else:
                    console.print("[bold red]✘ 操作失败[/bold red]")
                sleep(2)

            elif service == 26:  # 强改密码
                console.print("[bold]请输入新密码[/bold]")
                new_password = prompt_valid_value("[?] 新密码", "Password")
                if cpm.change_password(new_password):
                    console.print("[bold green]✓ 密码已强制修改[/bold green]")
                else:
                    console.print("[bold red]✘ 修改失败[/bold red]")
                sleep(2)

            elif service == 27:  # 强改邮箱
                console.print("[bold]请输入新邮箱[/bold]")
                new_email = prompt_valid_value("[?] 新邮箱", "Email")
                if cpm.change_email(new_email):
                    console.print("[bold green]✓ 邮箱已强制修改[/bold green]")
                else:
                    console.print("[bold red]✘ 邮箱已被占用[/bold red]")
                sleep(2)

            elif service == 28:  # 自定义尾翼
                console.print("[bold]请输入车辆参数[/bold]")
                car_id = IntPrompt.ask("[?] 车辆ID")
                spoiler_id = IntPrompt.ask("[?] 尾翼编号")
                if cpm.telmunnongodz(car_id, spoiler_id):
                    console.print("[bold green]✓ 尾翼造型已更新[/bold green]")
                else:
                    console.print("[bold red]✘ 编号无效[/bold red]")
                sleep(2)

            elif service == 29:  # 车身套件
                console.print("[bold]请输入车辆参数[/bold]")
                car_id = IntPrompt.ask("[?] 车辆ID")
                bodykit_id = IntPrompt.ask("[?] 套件编号")
                if cpm.telmunnongonz(car_id, bodykit_id):
                    console.print("[bold green]✓ 车身套件已安装[/bold green]")
                else:
                    console.print("[bold red]✘ 编号无效[/bold red]")
                sleep(2)

            # ========== 退出提示（位于内层循环内）==========
            answ = Prompt.ask(
                "[bold yellow]是否继续使用？[/bold yellow] (y继续/n退出)",
                choices=["y", "n"],
                default="y"
            )
            if answ.lower() == "n":
                break  # 退出内层循环

    # ========== 外层循环提示 ==========
    console.print("[bold]正在返回主菜单...[/bold]")
    sleep(1)
